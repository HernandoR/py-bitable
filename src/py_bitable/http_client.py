import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple

import httpx
from ratelimit import limits, sleep_and_retry


def singleton(cls):
    """单例装饰器"""
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class HttpClient:
    """
    带有QPS控制、重试机制和并发支持的单例HTTP客户端
    使用ratelimit库实现频率控制
    """

    def __init__(
        self,
        timeout: float = 10.0,
        qps_limit: int = 10,  # 每秒最大请求数
        max_workers: int = 5,  # 最大并发线程数
    ):
        self.timeout = timeout
        self.qps_limit = qps_limit
        self.max_workers = max_workers  # 控制并发数

        # 初始化HTTP客户端
        self.client: Optional[httpx.Client] = None
        self._init_client()

        self.limited_get: Optional[Callable[..., Dict[str, Any]]] = None
        self.limited_post: Optional[Callable[..., Dict[str, Any]]] = None

        # 创建带限流的请求方法
        self._setup_rate_limited_methods()

        # 创建线程池
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)

    def _init_client(self):
        """初始化httpx客户端"""
        self.client = httpx.Client(timeout=self.timeout)

    def _setup_rate_limited_methods(self):
        """设置带速率限制的请求方法"""
        # 计算限流参数：calls=qps_limit, period=1秒
        rate_limit_decorator = limits(calls=self.qps_limit, period=1)

        # 为GET和POST方法添加限流和重试
        self.limited_get = sleep_and_retry(rate_limit_decorator(self._get_request))
        self.limited_post = sleep_and_retry(rate_limit_decorator(self._post_request))

    def _get_request(self, url: str, **kwargs) -> Dict[str, Any]:
        """原始GET请求实现"""
        response = self.client.get(url, **kwargs)
        response.raise_for_status()
        return response.json() if response.content else {}

    def _post_request(self, url: str, **kwargs) -> Dict[str, Any]:
        """原始POST请求实现"""
        response = self.client.post(url, **kwargs)
        response.raise_for_status()
        return response.json() if response.content else {}

    # 公开的便捷方法
    def get(self, url: str, **kwargs) -> Dict[str, Any]:
        """无限制的GET请求"""
        return self._get_request(url, **kwargs)

    def post(self, url: str, **kwargs) -> Dict[str, Any]:
        """无限制的POST请求"""
        return self._post_request(url, **kwargs)

    def concurrent_get(
        self, urls: List[str], **kwargs
    ) -> List[Tuple[str, Optional[Dict[str, Any]], Optional[Exception]]]:
        """
        并发发送多个GET请求，受QPS限制

        Args:
            urls: 要请求的URL列表
            **kwargs: 传递给get请求的参数

        Returns:
            结果列表，每个元素是一个元组：(url, 响应结果, 异常)
        """
        futures = []
        results = []

        for url in urls:
            # 提交任务到线程池
            future = self.executor.submit(self.limited_get, url, **kwargs)
            futures.append((url, future))

        # 获取结果
        for url, future in futures:
            try:
                result = future.result()
                results.append((url, result, None))
            except Exception as e:
                results.append((url, None, e))

        return results

    def concurrent_post(
        self,
        requests: List[Tuple[str, Dict]],
        **kwargs,
    ) -> List[Tuple[str, Optional[Dict[str, Any]], Optional[Exception]]]:
        """
        并发发送多个POST请求，受QPS限制

        Args:
            requests: 请求列表，每个元素是(url, data)元组
            **kwargs: 传递给post请求的参数

        Returns:
            结果列表，每个元素是一个元组：(url, 响应结果, 异常)
        """
        futures = []
        results = []

        for url, data in requests:
            # 提交任务到线程池
            future = self.executor.submit(self.limited_post, url, json=data, **kwargs)
            futures.append((url, future))

        # 获取结果
        for url, future in futures:
            try:
                result = future.result()
                results.append((url, result, None))
            except Exception as e:
                results.append((url, None, e))

        return results

    def __del__(self):
        """清理资源"""
        if hasattr(self, "executor"):
            self.executor.shutdown()
        if self.client:
            self.client.close()


# 使用示例
if __name__ == "__main__":
    import time

    # 初始化客户端，设置每秒最多5个请求，最大并发数3
    client = HttpClient(qps_limit=5, max_workers=3)

    # 测试并发限流效果
    start_time = time.time()
    # url test to google
    urls = ["https://httpbin.org/get" for i in range(15)]

    # 并发发送请求
    results = client.concurrent_get(urls)

    for url, result, error in results:
        if error:
            print(f"请求失败 {url}: {str(error)}")
        else:
            print(f"请求成功 {url}: {result.get('args', {}).get('index')}")

    end_time = time.time()
    print(f"总耗时: {end_time - start_time:.2f}秒")
    # 15个请求，QPS=5，理论耗时应在3秒左右，但因为并发处理，实际体验会更流畅

    # try limited get
    for i in range(7):
        t = time.time()
        response = client.limited_get("https://httpbin.org/get", params={"index": i})
        te = time.time()
        print(f"请求 {i} 耗时: {te - t:.2f}秒")
        print(response)
