"""Python library for uploading attachments and creating records in Feishu Bitable."""

from py_bitable.bitable import Bitable
from py_bitable.client import BitableApiClient
from py_bitable.models import (
    AttachmentField,
    BitableRecord,
    FieldMetadata,
    RecordField,
)

__all__ = [
    "Bitable",
    "BitableApiClient",
    "BitableRecord",
    "RecordField",
    "AttachmentField",
    "FieldMetadata",
]


def main() -> None:
    """Main entry point."""
    print("py-bitable - Feishu Bitable API library")
