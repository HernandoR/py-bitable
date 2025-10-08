"""Unit tests for py-bitable models."""

import pytest
from pydantic import ValidationError

from py_bitable.models import (
    AttachmentField,
    AttachmentFile,
    BitableRecord,
    FieldMetadata,
    UploadFinishResponse,
    UploadPrepareResponse,
)


class TestAttachmentFile:
    """Tests for AttachmentFile model."""

    def test_create_attachment_file(self):
        """Test creating an attachment file."""
        attachment = AttachmentFile(
            file_token="test_token_123",
            name="test.pdf",
            size=1024,
            type="application/pdf",
        )
        assert attachment.file_token == "test_token_123"
        assert attachment.name == "test.pdf"
        assert attachment.size == 1024
        assert attachment.type == "application/pdf"

    def test_attachment_file_required_fields(self):
        """Test that file_token is required."""
        with pytest.raises(ValidationError):
            AttachmentFile()

    def test_attachment_file_optional_fields(self):
        """Test creating attachment with only required fields."""
        attachment = AttachmentFile(file_token="token123")
        assert attachment.file_token == "token123"
        assert attachment.name is None
        assert attachment.size is None
        assert attachment.type is None


class TestAttachmentField:
    """Tests for AttachmentField model."""

    def test_create_attachment_field(self):
        """Test creating an attachment field."""
        field = AttachmentField(
            attachments=[
                AttachmentFile(file_token="token1", name="file1.pdf"),
                AttachmentFile(file_token="token2", name="file2.jpg"),
            ]
        )
        assert len(field.attachments) == 2
        assert field.attachments[0].file_token == "token1"
        assert field.attachments[1].file_token == "token2"

    def test_attachment_field_empty(self):
        """Test creating an empty attachment field."""
        field = AttachmentField()
        assert field.attachments == []


class TestFieldMetadata:
    """Tests for FieldMetadata model."""

    def test_create_field_metadata(self):
        """Test creating field metadata."""
        field = FieldMetadata(
            field_id="fld123",
            field_name="Name",
            type=1,
            description="Name field",
            is_primary=True,
        )
        assert field.field_id == "fld123"
        assert field.field_name == "Name"
        assert field.type == 1
        assert field.description == "Name field"
        assert field.is_primary is True

    def test_field_metadata_required_fields(self):
        """Test required fields."""
        # Should work with only required fields
        field = FieldMetadata(field_id="fld123", field_name="Test", type=1)
        assert field.field_id == "fld123"
        assert field.description is None
        assert field.is_primary is None


class TestBitableRecord:
    """Tests for BitableRecord model."""

    def test_create_record(self):
        """Test creating a Bitable record."""
        record = BitableRecord(
            record_id="rec123", fields={"Name": "Test", "Age": 30}
        )
        assert record.record_id == "rec123"
        assert record.fields["Name"] == "Test"
        assert record.fields["Age"] == 30

    def test_record_without_id(self):
        """Test creating a record without ID (new record)."""
        record = BitableRecord(fields={"Name": "New Record"})
        assert record.record_id is None
        assert record.fields["Name"] == "New Record"


class TestUploadResponses:
    """Tests for upload response models."""

    def test_upload_prepare_response(self):
        """Test UploadPrepareResponse model."""
        response = UploadPrepareResponse(
            upload_id="upload123", block_size=4194304, block_num=3
        )
        assert response.upload_id == "upload123"
        assert response.block_size == 4194304
        assert response.block_num == 3

    def test_upload_finish_response(self):
        """Test UploadFinishResponse model."""
        response = UploadFinishResponse(file_token="file_token_456")
        assert response.file_token == "file_token_456"
