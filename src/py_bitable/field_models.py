# ------------------------------
# 基础依赖模型
# ------------------------------
from typing import List, Optional, Union

from pydantic import BaseModel, Field, ValidationInfo, field_validator

from .field_enums import (
    AutoNumberRuleTypeEnum,
    AutoNumberTimeFormatEnum,
    AutoNumberTypeEnum,
    CurrencyCodeEnum,
    DateFormatterEnum,
    FieldTypeEnum,
    LocationInputTypeEnum,
    NumberFormatterEnum,
    RatingSymbolEnum,
    UITypeEnum,
)


class BarcodeEditMode(BaseModel):
    """条码字段的编辑模式"""

    manual: bool = Field(default=True, description="是否允许手动录入")
    scan: bool = Field(default=True, description="是否允许移动端扫描录入")


class SelectOption(BaseModel):
    """单选/多选字段的选项"""

    id: Optional[str] = Field(None, description="选项ID(新增时无需指定)")
    name: str = Field(..., description="选项名称")
    color: Optional[int] = Field(None, ge=0, le=54, description="选项颜色(0-54)")


class RatingConfig(BaseModel):
    """评分字段的配置"""

    symbol: Optional[RatingSymbolEnum] = Field(
        default=RatingSymbolEnum.STAR, description="评分图标"
    )


class LocationConfig(BaseModel):
    """地理位置字段的配置"""

    input_type: LocationInputTypeEnum = Field(..., description="地理位置输入限制")


class AutoNumberRule(BaseModel):
    """自定义编号的规则"""

    type: AutoNumberRuleTypeEnum = Field(..., description="规则类型")
    value: str = Field(..., description="规则值")

    @field_validator("value")
    def validate_rule_value(cls, v: str, info: ValidationInfo) -> str:
        """校验不同规则类型的value合法性"""
        rule_type = info.data.get("type")
        if rule_type == AutoNumberRuleTypeEnum.SYSTEM_NUMBER:
            if not v.isdigit() or not (1 <= int(v) <= 9):
                raise ValueError("system_number的value必须是1-9的整数")
        elif rule_type == AutoNumberRuleTypeEnum.FIXED_TEXT:
            if len(v) > 20:
                raise ValueError("fixed_text的value长度不能超过20个字符")
        elif rule_type == AutoNumberRuleTypeEnum.CREATED_TIME:
            valid_formats = [fmt.value for fmt in AutoNumberTimeFormatEnum]
            if v not in valid_formats:
                raise ValueError(f"created_time的value必须是{valid_formats}之一")
        return v


class AutoNumberConfig(BaseModel):
    """自动编号字段的配置"""

    type: AutoNumberTypeEnum = Field(..., description="自动编号类型")
    reformat_existing_records: Optional[bool] = Field(
        default=False, description="是否应用于已有记录"
    )
    options: Optional[List[AutoNumberRule]] = Field(
        None, description="自定义编号规则列表"
    )

    @field_validator("options")
    def require_options_for_custom(
        cls, v: Optional[List[AutoNumberRule]], info: ValidationInfo
    ) -> Optional[List[AutoNumberRule]]:
        """自定义编号类型必须提供规则列表"""
        if info.data.get("type") == AutoNumberTypeEnum.CUSTOM and not v:
            raise ValueError("自定义编号(custom)必须提供options规则列表")
        return v


# ------------------------------
# 字段属性模型
# ------------------------------
class FieldProperty(BaseModel):
    """字段属性统一模型(根据FieldType动态匹配结构)"""

    # 1. 条码字段相关
    allowed_edit_modes: Optional[BarcodeEditMode] = Field(
        None, description="条码编辑模式"
    )

    # 2. 数字/货币/进度/公式格式
    formatter: Optional[NumberFormatterEnum] = Field(None, description="数字格式")

    # 3. 货币字段相关
    currency_code: Optional[CurrencyCodeEnum] = Field(None, description="货币类型")

    # 4. 进度字段相关
    range_customize: Optional[bool] = Field(
        default=False, description="是否自定义进度范围"
    )
    min: Optional[float] = Field(None, description="进度最小值")
    max: Optional[float] = Field(None, description="进度最大值")

    # 5. 评分字段相关
    rating: Optional[RatingConfig] = Field(None, description="评分配置")

    # 6. 单选/多选字段相关
    options: Optional[List[SelectOption]] = Field(None, description="选项列表")

    # 7. 日期字段相关
    date_formatter: Optional[DateFormatterEnum] = Field(
        default=DateFormatterEnum.YMD_SLASH, description="日期格式"
    )
    auto_fill: Optional[bool] = Field(default=False, description="是否自动填充创建时间")

    # 8. 人员/群组字段相关
    multiple: Optional[bool] = Field(default=True, description="是否允许选择多个")

    # 9. 关联字段相关
    table_id: Optional[str] = Field(None, description="关联数据表ID")
    back_field_name: Optional[str] = Field(None, description="关联表的双向字段名")

    # 10. 公式字段相关
    formula_expression: Optional[str] = Field(None, description="公式表达式")

    # 11. 地理位置字段相关
    location: Optional[LocationConfig] = Field(None, description="地理位置配置")

    # 12. 自动编号字段相关
    auto_serial: Optional[AutoNumberConfig] = Field(None, description="自动编号配置")

    @field_validator("min", "max")
    def validate_progress_range(
        cls, v: Optional[float], info: ValidationInfo
    ) -> Optional[float]:
        """校验进度字段的范围设置"""
        if info.data.get("range_customize") and v is None:
            raise ValueError("进度字段启用自定义范围时，必须提供min和max")
        return v

    @field_validator("min", "max")
    def validate_rating_range(
        cls, v: Optional[int], info: ValidationInfo
    ) -> Optional[int]:
        """校验评分字段的范围设置"""
        if info.data.get("rating"):
            if v is None:
                raise ValueError("评分字段必须提供min(0/1)和max(1-10)")
            if info.field_name == "min" and v not in [0, 1]:
                raise ValueError("评分最小值只能是0或1")
            if info.field_name == "max" and not (1 <= v <= 10):
                raise ValueError("评分最大值必须在1-10之间")
        return v

    @field_validator("currency_code")
    def validate_currency_code(
        cls, v: Optional[CurrencyCodeEnum], info: ValidationInfo
    ) -> Optional[CurrencyCodeEnum]:
        """校验货币字段的货币类型"""
        formatter = info.data.get("formatter")
        if (
            formatter
            in [
                NumberFormatterEnum.CNY,
                NumberFormatterEnum.CNY_DECIMAL_2,
                NumberFormatterEnum.USD,
                NumberFormatterEnum.USD_DECIMAL_2,
            ]
            and not v
        ):
            raise ValueError("货币字段必须提供currency_code")
        return v


# ------------------------------
# 核心字段模型
# ------------------------------
class BitableField(BaseModel):
    """多维表格字段核心模型
    https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-field/guide
    """

    field_id: Optional[str] = Field(None, description="字段ID(新增时无需指定)")
    field_name: str = Field(..., description="字段名称")
    type: FieldTypeEnum = Field(..., description="字段类型")
    description: Optional[str] = Field(None, description="字段描述")
    is_primary: Optional[bool] = Field(default=False, description="是否为索引字段")
    property: Optional[Union[FieldProperty, None]] = Field(None, description="字段属性")
    ui_type: Optional[UITypeEnum] = Field(None, description="UI展示类型")
    is_hidden: Optional[bool] = Field(default=False, description="是否为隐藏字段")

    @field_validator("ui_type")
    def validate_ui_type_consistency(
        cls, v: Optional[UITypeEnum], info: ValidationInfo
    ) -> Optional[UITypeEnum]:
        """校验ui_type与type的一致性"""
        field_type = info.data.get("type")
        if not v:
            return v

        # 文本类type(1)只能对应文本类ui_type
        if field_type == FieldTypeEnum.TEXT_BASE:
            valid_ui = [UITypeEnum.TEXT, UITypeEnum.BARCODE, UITypeEnum.EMAIL]
            if v not in valid_ui:
                raise ValueError(f"type={field_type}只能对应ui_type={valid_ui}")

        # 数字类type(2)只能对应数字类ui_type
        elif field_type == FieldTypeEnum.NUMBER_BASE:
            valid_ui = [
                UITypeEnum.NUMBER,
                UITypeEnum.PROGRESS,
                UITypeEnum.CURRENCY,
                UITypeEnum.RATING,
            ]
            if v not in valid_ui:
                raise ValueError(f"type={field_type}只能对应ui_type={valid_ui}")

        # 其他类型的type与ui_type必须一一对应
        type_ui_mapping = {
            FieldTypeEnum.SINGLE_SELECT: UITypeEnum.SINGLE_SELECT,
            FieldTypeEnum.MULTI_SELECT: UITypeEnum.MULTI_SELECT,
            FieldTypeEnum.DATE: UITypeEnum.DATE_TIME,
            FieldTypeEnum.CHECKBOX: UITypeEnum.CHECKBOX,
            FieldTypeEnum.USER: UITypeEnum.USER,
            FieldTypeEnum.GROUP_CHAT: UITypeEnum.GROUP_CHAT,
            FieldTypeEnum.PHONE: UITypeEnum.PHONE,
            FieldTypeEnum.URL: UITypeEnum.URL,
            FieldTypeEnum.SINGLE_LINK: UITypeEnum.SINGLE_LINK,
            FieldTypeEnum.DUPLEX_LINK: UITypeEnum.DUPLEX_LINK,
            FieldTypeEnum.LOOKUP: UITypeEnum.LOOKUP,
            FieldTypeEnum.ATTACHMENT: UITypeEnum.ATTACHMENT,
            FieldTypeEnum.FORMULA: UITypeEnum.FORMULA,
            FieldTypeEnum.LOCATION: UITypeEnum.LOCATION,
            FieldTypeEnum.STAGE: UITypeEnum.STAGE,
            FieldTypeEnum.BUTTON: UITypeEnum.BUTTON,
            FieldTypeEnum.CREATED_TIME: UITypeEnum.CREATED_TIME,
            FieldTypeEnum.MODIFIED_TIME: UITypeEnum.MODIFIED_TIME,
            FieldTypeEnum.CREATED_USER: UITypeEnum.CREATED_USER,
            FieldTypeEnum.MODIFIED_USER: UITypeEnum.MODIFIED_USER,
            FieldTypeEnum.AUTO_NUMBER: UITypeEnum.AUTO_NUMBER,
        }
        if field_type in type_ui_mapping and v != type_ui_mapping[field_type]:
            raise ValueError(
                f"type={field_type}必须对应ui_type={type_ui_mapping[field_type]}"
            )

        return v
