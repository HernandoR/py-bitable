"""Low-level API client for Feishu Bitable."""

import os
import zlib
from functools import wraps
from io import BytesIO
from time import time
from typing import Any, Dict, List, Optional

from py_bitable.http_client import HttpClient
from py_bitable.models import (
    BatchCreateRecordsResponse,
    FieldMetadata,
    UploadFinishResponse,
    UploadPrepareResponse,
)


def retry_on_exception(
    exceptions: tuple = (Exception,),
    max_retries: int = 3,
    delay: float = 1.0,
):
    """Decorator to retry a function on specified exceptions."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    if retries >= max_retries:
                        raise e
                    time.sleep(delay)

        return wrapper

    return decorator


class BitableApiClient:
    """Low-level API client for Feishu Bitable operations.

    This client handles authentication and direct API calls to Feishu.
    """

    def __init__(
        self,
        app_id: str,
        app_secret: str,
        base_url: str = "https://open.feishu.cn/open-apis",
    ):
        """Initialize the API client.

        Args:
            app_id: Feishu app ID
            app_secret: Feishu app secret
            base_url: Feishu API base URL
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = base_url
        self._access_token: Optional[str] = None
        self._tenant_access_token: Optional[str] = None

        self.client_qps5 = HttpClient(timeout=30, qps_limit=5, max_workers=5)
        self.client_qps100 = HttpClient(timeout=30, qps_limit=100, max_workers=10)

        self._max_retries = int(os.getenv("BITABLE_MAX_RETRIES", "3"))
        self._retry_delay = float(os.getenv("BITABLE_RETRY_DELAY", "1.0"))
        self._timeout = float(os.getenv("BITABLE_TIMEOUT", "10.0"))

    def _get_tenant_access_token(self) -> str:
        """Get tenant access token for API calls.

        Returns:
            Tenant access token
        """
        if self._tenant_access_token:
            return self._tenant_access_token

        url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
        payload = {"app_id": self.app_id, "app_secret": self.app_secret}

        # data = self.http_post(url, json=payload)
        data = self.client_qps100.limited_post(url, json=payload)

        if data.get("code") != 0:
            raise ValueError(f"Failed to get access token: {data.get('msg')}")

        self._tenant_access_token = data["tenant_access_token"]
        return self._tenant_access_token

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers with authentication.

        Returns:
            Headers dict with Authorization
        """
        token = self._get_tenant_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        }

    def get_table_fields(self, app_token: str, table_id: str) -> List[FieldMetadata]:
        """Get field metadata for a table.

        Args:
            app_token: Bitable app token
            table_id: Table ID

        Returns:
            List of field metadata
        """
        url = f"{self.base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
        headers = self._get_headers()

        data = self.http_get(url, headers=headers)

        if data.get("code") != 0:
            raise ValueError(f"Failed to get table fields: {data.get('msg')}")

        items = data.get("data", {}).get("items", [])
        return [FieldMetadata(**item) for item in items]

    def upload_file_prepare(
        self,
        file_path: str,
        parent_type: str = "bitable_image",
        parent_node: str = "",
        file_name: Optional[str] = None,
    ) -> UploadPrepareResponse:
        """Prepare for file upload (multipart upload).

        Args:
            file_path: Path to the file to upload
            parent_type: Parent type (default: bitable_image)
            parent_node: Parent node token

        Returns:
            Upload prepare response with upload_id and block info
        """
        file_size = os.path.getsize(file_path)
        file_name = file_name or os.path.basename(file_path)

        url = f"{self.base_url}/drive/v1/medias/upload_prepare"
        headers = self._get_headers()

        payload = {
            "file_name": file_name,
            "size": file_size,
            "parent_type": parent_type,
            "parent_node": parent_node,
        }
        # data = self.http_post(url, headers=headers, json=payload)
        data = self.client_qps5.limited_post(url, headers=headers, json=payload)

        if data.get("code") != 0:
            raise ValueError(f"Failed to prepare upload: {data.get('msg')}")

        upload_data = data["data"]
        return UploadPrepareResponse(**upload_data)

    @retry_on_exception()
    def upload_file_part(
        self, upload_id: str, seq: int, file_data: bytes
    ) -> Dict[str, Any]:
        """Upload a file part.

        Args:
            upload_id: Upload ID from prepare
            seq: Sequence number of this part
            file_data: File data for this part

        Returns:
            Response data
        """
        url = f"{self.base_url}/drive/v1/medias/upload_part"
        headers = self._get_headers()
        headers.pop("Content-Type", None)  # Let httpx set multipart content type

        # Adler-32
        cksm = zlib.adler32(file_data) & 0xFFFFFFFF

        data = {
            "upload_id": upload_id,
            "seq": seq,
            "size": len(file_data),
            "checksum": cksm,
        }
        files = {"file": ("chunk", BytesIO(file_data), "application/octet-stream")}

        # response_data = self.http_post(url, headers=headers, data=data, files=files)
        response_data = self.client_qps5.limited_post(
            url, headers=headers, data=data, files=files
        )

        if response_data.get("code") != 0:
            raise ValueError(f"Failed to upload part: {response_data.get('msg')}")

        return response_data["data"]

    def upload_file_finish(
        self, upload_id: str, block_num: int
    ) -> UploadFinishResponse:
        """Finish file upload.

        Args:
            upload_id: Upload ID from prepare
            block_num: Total number of blocks uploaded

        Returns:
            Upload finish response with file_token
        """
        url = f"{self.base_url}/drive/v1/medias/upload_finish"
        headers = self._get_headers()

        payload = {"upload_id": upload_id, "block_num": block_num}
        # data = self.http_post(url, headers=headers, json=payload)
        data = self.client_qps5.limited_post(url, headers=headers, json=payload)

        if data.get("code") != 0:
            raise ValueError(f"Failed to finish upload: {data.get('msg')}")

        return UploadFinishResponse(**data["data"])

    def upload_file(
        self,
        file_path: str,
        parent_type: str = "bitable_image",
        parent_node: str = "",
        file_name: Optional[str] = None,
    ) -> str:
        """Upload a file completely (prepare, upload parts, finish).

        Args:
            file_path: Path to the file to upload
            parent_type: Parent type (default: bitable_image)
            parent_node: Parent node token

        Returns:
            File token of the uploaded file
        """
        # Prepare upload
        prepare_response = self.upload_file_prepare(
            file_path,
            parent_type,
            parent_node,
            file_name,
        )

        # Read file and split into blocks
        with open(file_path, "rb") as f:
            file_data = f.read()

        block_size = prepare_response.block_size
        block_num = prepare_response.block_num

        # Upload each block
        for seq in range(block_num):
            start = seq * block_size
            end = min((seq + 1) * block_size, len(file_data))
            block_data = file_data[start:end]
            self.upload_file_part(prepare_response.upload_id, seq, block_data)

        # Finish upload
        finish_response = self.upload_file_finish(
            prepare_response.upload_id,
            block_num,
        )
        return finish_response.file_token

    def list_tables(self, app_token: str) -> dict[str:Any]:
        """List tables in the Bitable app.

        Args:
            app_token: Bitable app token
        Returns:
            dictionary of tables, key is id and value is table info
        """
        url = f"{self.base_url}/bitable/v1/apps/{app_token}/tables"
        headers = self._get_headers()
        # 使用统一 http_get；原先 client 使用 timeout=30.0，保留该超时作为单次请求参数
        data = self.http_get(url, headers=headers, timeout=30.0)

        if data.get("code") != 0:
            raise ValueError(f"Failed to list tables: {data.get('msg')}")

        data = data["data"]
        res = {item["table_id"]: item for item in data["items"]}
        while data["has_more"]:
            token = data["page_token"]
            data = self.http_get(
                f"{url}?page_token={token}", headers=headers, timeout=30.0
            )
            if data.get("code") != 0:
                raise ValueError(f"Failed to list tables: {data.get('msg')}")

            data = data["data"]
            res.update({item["table_id"]: item for item in data["items"]})
        return res

    def create_table(
        self, app_token: str, table_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new table in the Bitable app.
        ref https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table/create

        Args:
            app_token: Bitable app token
            table_data: Data for the new table (e.g., name, description)
        Returns:
            Created table information
        """
        url = f"{self.base_url}/bitable/v1/apps/{app_token}/tables"
        headers = self._get_headers()
        payload = table_data
        # data = self.http_post(url, headers=headers, json=payload, timeout=30.0)
        data = self.client_qps5.limited_post(url, headers=headers, json=payload)

        if data.get("code") != 0:
            raise ValueError(f"Failed to create table: {data.get('msg')}")

        return data.get("data", {})

    def batch_create_records(
        self, app_token: str, table_id: str, records: List[Dict[str, Any]]
    ) -> BatchCreateRecordsResponse:
        """Batch create records in a table.
        Args:
            app_token: Bitable app token
            table_id: Table ID
            records: List of records to create (each record is a dict of fields)

        Returns:
            Batch create response with created records
        """
        url = f"{self.base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create"
        headers = self._get_headers()

        payload = {"records": [{"fields": record} for record in records]}
        # data = self.http_post(url, headers=headers, json=payload, timeout=30.0)
        data = self.client_qps5.limited_post(url, headers=headers, json=payload)

        if data.get("code") != 0:
            raise ValueError(f"Failed to create records: {data}")

        records_data = data.get("data", {}).get("records", [])
        return BatchCreateRecordsResponse(
            records=[
                {
                    "record_id": r.get("record_id"),
                    "fields": r.get("fields", {}),
                }
                for r in records_data
            ]
        )
