from enum import Enum, IntEnum


class FieldTypeEnum(IntEnum):
    """字段类型枚举（对应文档中的 `type`)"""

    # 文本类
    TEXT_BASE = 1  # 包含：文本、条码、邮箱
    # 数字类
    NUMBER_BASE = 2  # 包含：数字、进度、货币、评分
    # 选择类
    SINGLE_SELECT = 3
    MULTI_SELECT = 4
    # 时间日期类
    DATE = 5
    # 布尔类
    CHECKBOX = 7
    # 人员/群组类
    USER = 11
    GROUP_CHAT = 23
    # 联系信息类
    PHONE = 13
    EMAIL = 1  # 归属于 TEXT_BASE，需配合 UI_TYPE.EMAIL 使用
    # 链接/关联类
    URL = 15
    SINGLE_LINK = 18  # 单向关联
    DUPLEX_LINK = 21  # 双向关联
    LOOKUP = 19  # 查找引用
    # 特殊内容类
    ATTACHMENT = 17
    FORMULA = 20
    LOCATION = 22
    STAGE = 24  # 流程
    BUTTON = 3001
    # 自动记录类
    CREATED_TIME = 1001
    MODIFIED_TIME = 1002
    CREATED_USER = 1003
    MODIFIED_USER = 1004
    AUTO_NUMBER = 1005


class UITypeEnum(str, Enum):
    """UI展示类型枚举（对应文档中的 `ui_type`)"""

    # 文本类
    TEXT = "Text"
    BARCODE = "Barcode"
    EMAIL = "Email"
    # 数字类
    NUMBER = "Number"
    PROGRESS = "Progress"
    CURRENCY = "Currency"
    RATING = "Rating"
    # 选择类
    SINGLE_SELECT = "SingleSelect"
    MULTI_SELECT = "MultiSelect"
    # 时间日期类
    DATE_TIME = "DateTime"
    # 布尔类
    CHECKBOX = "Checkbox"
    # 人员/群组类
    USER = "User"
    GROUP_CHAT = "GroupChat"
    # 联系信息类
    PHONE = "Phone"
    # 链接/关联类
    URL = "Url"
    SINGLE_LINK = "SingleLink"
    DUPLEX_LINK = "DuplexLink"
    LOOKUP = "Lookup"
    # 特殊内容类
    ATTACHMENT = "Attachment"
    FORMULA = "Formula"
    LOCATION = "Location"
    STAGE = "Stage"
    BUTTON = "Button"
    # 自动记录类
    CREATED_TIME = "CreatedTime"
    MODIFIED_TIME = "ModifiedTime"
    CREATED_USER = "CreatedUser"
    MODIFIED_USER = "ModifiedUser"
    AUTO_NUMBER = "AutoNumber"


class NumberFormatterEnum(str, Enum):
    """数字/货币/进度/公式的格式枚举（对应 `property.formatter`)"""

    # 基础数字格式
    INTEGER = "0"
    DECIMAL_1 = "0.0"
    DECIMAL_2 = "0.00"
    DECIMAL_3 = "0.000"
    DECIMAL_4 = "0.0000"
    THOUSAND = "1,000"
    THOUSAND_DECIMAL_2 = "1,000.00"
    # 百分比格式
    PERCENT = "%"
    PERCENT_DECIMAL_2 = "0.00%"
    # 货币格式
    CNY = "¥"
    CNY_DECIMAL_2 = "¥0.00"
    USD = "$"
    USD_DECIMAL_2 = "$0.00"


class CurrencyCodeEnum(str, Enum):
    """货币类型枚举（对应 `property.currency_code`)"""

    CNY = "CNY"  # 人民币 ¥
    USD = "USD"  # 美元 $
    EUR = "EUR"  # 欧元 €
    GBP = "GBP"  # 英镑 £
    AED = "AED"  # 阿联酋迪拉姆 dh
    AUD = "AUD"  # 澳大利亚元 $
    BRL = "BRL"  # 巴西雷亚尔 R$
    CAD = "CAD"  # 加拿大元 $
    CHF = "CHF"  # 瑞士法郎 CHF
    HKD = "HKD"  # 港元 $
    INR = "INR"  # 印度卢比 ₹
    IDR = "IDR"  # 印尼盾 Rp
    JPY = "JPY"  # 日元 ¥
    KRW = "KRW"  # 韩元 ₩
    MOP = "MOP"  # 澳门元 MOP$
    MXN = "MXN"  # 墨西哥比索 $
    MYR = "MYR"  # 马来西亚令吉 RM
    PHP = "PHP"  # 菲律宾比索 ₱
    PLN = "PLN"  # 波兰兹罗提 zł
    RUB = "RUB"  # 俄罗斯卢布 ₽
    SGD = "SGD"  # 新加坡元 $
    THB = "THB"  # 泰国铢 ฿
    TRY = "TRY"  # 土耳其里拉 ₺
    TWD = "TWD"  # 新台币 NT$
    VND = "VND"  # 越南盾 ₫


class RatingSymbolEnum(str, Enum):
    """评分图标枚举（对应 `property.rating.symbol`)"""

    STAR = "star"  # 星星
    HEART = "heart"  # 爱心
    THUMBS_UP = "thumbsup"  # 赞
    FIRE = "fire"  # 火
    SMILE = "smile"  # 笑脸
    LIGHTNING = "lightning"  # 闪电
    FLOWER = "flower"  # 花
    NUMBER = "number"  # 数字


class DateFormatterEnum(str, Enum):
    """日期格式枚举（对应 `property.date_formatter`)"""

    YMD_SLASH = "yyyy/MM/dd"  # 2021/01/30
    YMD_HM_DASH = "yyyy-MM-dd HH:mm"  # 2021-01-30 14:00
    MD_DASH = "MM-dd"  # 01-30
    MDY_SLASH = "MM/dd/yyyy"  # 01/30/2021
    DMY_SLASH = "dd/MM/yyyy"  # 30/01/2021


class LocationInputTypeEnum(str, Enum):
    """地理位置输入限制（对应 `property.location.input_type`)"""

    ONLY_MOBILE = "only_mobile"  # 仅移动端实时定位
    NOT_LIMIT = "not_limit"  # 无限制


class AutoNumberTypeEnum(str, Enum):
    """自动编号类型（对应 `property.auto_serial.type`)"""

    CUSTOM = "custom"  # 自定义编号
    AUTO_INCREMENT = "auto_increment_number"  # 自增数字


class AutoNumberRuleTypeEnum(str, Enum):
    """自定义编号规则类型（对应 `property.auto_serial.options.type`)"""

    SYSTEM_NUMBER = "system_number"  # 自增数字位数（1-9)
    FIXED_TEXT = "fixed_text"  # 固定字符（≤20字符)
    CREATED_TIME = "created_time"  # 创建日期


class AutoNumberTimeFormatEnum(str, Enum):
    """自定义编号日期格式（对应 `AutoNumberRuleType.CREATED_TIME` 的 value)"""

    YMD = "yyyyMMdd"  # 20220130
    YM = "yyyyMM"  # 202201
    Y = "yyyy"  # 2022
    MD = "MMdd"  # 0130
    M = "MM"  # 01
    D = "dd"  # 30
