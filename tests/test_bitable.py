"""Unit tests for Bitable class."""

from unittest.mock import MagicMock, patch

from pydantic import BaseModel

from py_bitable import Bitable
from py_bitable.models import AttachmentFile, FieldMetadata


class TestRecord(BaseModel):
    """Test Pydantic model for records."""

    Name: str
    Description: str = ""
    Priority: int = 1


class TestBitable:
    """Tests for Bitable class."""

    def test_init(self):
        """Test Bitable initialization."""
        bitable = Bitable(
            app_id="app_id",
            app_secret="app_secret",
            app_token="app_token",
            table_id="table_id",
        )
        assert bitable.app_token == "app_token"
        assert bitable.table_id == "table_id"
        assert bitable.client is not None

    @patch("py_bitable.bitable.BitableApiClient")
    def test_get_table_schema(self, mock_client_class):
        """Test getting table schema."""
        # Setup mock
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_fields = [
            FieldMetadata(field_id="fld1", field_name="Name", type=1),
            FieldMetadata(field_id="fld2", field_name="Description", type=1),
        ]
        mock_client.get_table_fields.return_value = mock_fields

        # Test
        bitable = Bitable("app_id", "app_secret", "app_token", "table_id")
        bitable.client = mock_client

        schema = bitable.get_table_schema()

        assert len(schema) == 2
        assert schema[0].field_name == "Name"
        assert schema[1].field_name == "Description"
        mock_client.get_table_fields.assert_called_once_with("app_token", "table_id")

    @patch("py_bitable.bitable.BitableApiClient")
    def test_get_field_id(self, mock_client_class):
        """Test getting field ID by name."""
        # Setup mock
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_fields = [
            FieldMetadata(field_id="fld1", field_name="Name", type=1),
            FieldMetadata(field_id="fld2", field_name="Age", type=2),
        ]
        mock_client.get_table_fields.return_value = mock_fields

        # Test
        bitable = Bitable("app_id", "app_secret", "app_token", "table_id")
        bitable.client = mock_client

        field_id = bitable.get_field_id("Name")
        assert field_id == "fld1"

        field_id = bitable.get_field_id("Age")
        assert field_id == "fld2"

        field_id = bitable.get_field_id("NonExistent")
        assert field_id is None

    @patch("py_bitable.bitable.BitableApiClient")
    def test_create_record_with_dict(self, mock_client_class):
        """Test creating a record with a dict."""
        # Setup mock
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_fields = [
            FieldMetadata(field_id="fld1", field_name="Name", type=1),
            FieldMetadata(field_id="fld2", field_name="Age", type=2),
        ]
        mock_client.get_table_fields.return_value = mock_fields

        from py_bitable.models import BatchCreateRecordsResponse, BitableRecord

        mock_response = BatchCreateRecordsResponse(
            records=[
                BitableRecord(
                    record_id="rec123", fields={"fld1": "John", "fld2": 30}
                )
            ]
        )
        mock_client.batch_create_records.return_value = mock_response

        # Test
        bitable = Bitable("app_id", "app_secret", "app_token", "table_id")
        bitable.client = mock_client

        record = bitable.create_record({"Name": "John", "Age": 30})

        assert record["record_id"] == "rec123"
        # Verify the client was called with field IDs
        call_args = mock_client.batch_create_records.call_args
        assert call_args[0][0] == "app_token"
        assert call_args[0][1] == "table_id"
        # Check that field names were converted to IDs
        records = call_args[0][2]
        assert "fld1" in records[0]
        assert "fld2" in records[0]

    @patch("py_bitable.bitable.BitableApiClient")
    def test_create_record_with_pydantic_model(self, mock_client_class):
        """Test creating a record with a Pydantic model."""
        # Setup mock
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_fields = [
            FieldMetadata(field_id="fld1", field_name="Name", type=1),
            FieldMetadata(field_id="fld2", field_name="Description", type=1),
            FieldMetadata(field_id="fld3", field_name="Priority", type=2),
        ]
        mock_client.get_table_fields.return_value = mock_fields

        from py_bitable.models import BatchCreateRecordsResponse, BitableRecord

        mock_response = BatchCreateRecordsResponse(
            records=[
                BitableRecord(
                    record_id="rec456",
                    fields={"fld1": "Task", "fld2": "Test task", "fld3": 5},
                )
            ]
        )
        mock_client.batch_create_records.return_value = mock_response

        # Test
        bitable = Bitable("app_id", "app_secret", "app_token", "table_id")
        bitable.client = mock_client

        record_data = TestRecord(Name="Task", Description="Test task", Priority=5)
        record = bitable.create_record(record_data)

        assert record["record_id"] == "rec456"

    @patch("py_bitable.bitable.BitableApiClient")
    @patch("os.path.getsize")
    @patch("os.path.basename")
    def test_upload_attachment(
        self, mock_basename, mock_getsize, mock_client_class
    ):
        """Test uploading an attachment."""
        # Setup mocks
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.upload_file.return_value = "file_token_123"
        mock_basename.return_value = "test.pdf"
        mock_getsize.return_value = 2048

        # Test
        bitable = Bitable("app_id", "app_secret", "app_token", "table_id")
        bitable.client = mock_client

        attachment = bitable.upload_attachment("/path/to/test.pdf")

        assert isinstance(attachment, AttachmentFile)
        assert attachment.file_token == "file_token_123"
        assert attachment.name == "test.pdf"
        assert attachment.size == 2048
        mock_client.upload_file.assert_called_once()

    @patch("py_bitable.bitable.BitableApiClient")
    def test_create_records_batch(self, mock_client_class):
        """Test batch creating records."""
        # Setup mock
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_fields = [
            FieldMetadata(field_id="fld1", field_name="Name", type=1),
        ]
        mock_client.get_table_fields.return_value = mock_fields

        from py_bitable.models import BatchCreateRecordsResponse, BitableRecord

        mock_response = BatchCreateRecordsResponse(
            records=[
                BitableRecord(record_id="rec1", fields={"fld1": "Task 1"}),
                BitableRecord(record_id="rec2", fields={"fld1": "Task 2"}),
                BitableRecord(record_id="rec3", fields={"fld1": "Task 3"}),
            ]
        )
        mock_client.batch_create_records.return_value = mock_response

        # Test
        bitable = Bitable("app_id", "app_secret", "app_token", "table_id")
        bitable.client = mock_client

        records = bitable.create_records(
            [{"Name": "Task 1"}, {"Name": "Task 2"}, {"Name": "Task 3"}]
        )

        assert len(records) == 3
        assert records[0]["record_id"] == "rec1"
        assert records[1]["record_id"] == "rec2"
        assert records[2]["record_id"] == "rec3"
