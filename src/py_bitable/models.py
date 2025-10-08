"""Pydantic models for Feishu Bitable API."""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class AttachmentFile(BaseModel):
    """Attachment file information."""

    file_token: str = Field(..., description="File token from upload")
    name: Optional[str] = Field(None, description="File name")
    size: Optional[int] = Field(None, description="File size in bytes")
    type: Optional[str] = Field(None, description="MIME type")


class AttachmentField(BaseModel):
    """Attachment field value."""

    attachments: List[AttachmentFile] = Field(
        default_factory=list, description="List of attachments"
    )


class RecordField(BaseModel):
    """Base class for record fields.

    Users should subclass this to define their own record schemas.
    """

    class Config:
        """Pydantic config."""

        extra = "allow"  # Allow additional fields


class BitableRecord(BaseModel):
    """A record in Bitable table."""

    record_id: Optional[str] = Field(None, description="Record ID")
    fields: Dict[str, Any] = Field(..., description="Record fields")


class FieldType(BaseModel):
    """Field type information."""

    type: str = Field(..., description="Field type")
    # Add more specific type properties as needed


class FieldMetadata(BaseModel):
    """Metadata for a table field."""

    field_id: str = Field(..., description="Field ID")
    field_name: str = Field(..., description="Field name")
    type: int = Field(..., description="Field type code")
    property: Optional[Dict[str, Any]] = Field(None, description="Field properties")
    description: Optional[str] = Field(None, description="Field description")
    is_primary: Optional[bool] = Field(None, description="Whether this is primary key")


class TableSchema(BaseModel):
    """Table schema with field metadata."""

    fields: List[FieldMetadata] = Field(..., description="List of table fields")


class UploadPrepareResponse(BaseModel):
    """Response from upload prepare API."""

    upload_id: str = Field(..., description="Upload ID")
    block_size: int = Field(..., description="Block size for chunked upload")
    block_num: int = Field(..., description="Number of blocks")


class UploadFinishResponse(BaseModel):
    """Response from upload finish API."""

    file_token: str = Field(..., description="File token for the uploaded file")


class BatchCreateRecordsRequest(BaseModel):
    """Request for batch creating records."""

    records: List[Dict[str, Any]] = Field(..., description="List of records to create")


class BatchCreateRecordsResponse(BaseModel):
    """Response from batch create records API."""

    records: List[BitableRecord] = Field(..., description="Created records")


class FeishuApiResponse(BaseModel):
    """Generic Feishu API response wrapper."""

    code: int = Field(..., description="Response code")
    msg: str = Field(..., description="Response message")
    data: Optional[Union[Dict[str, Any], List[Any]]] = Field(
        None, description="Response data"
    )
