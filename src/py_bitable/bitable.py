"""High-level Bitable class for user-facing operations."""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

from py_bitable.client import BitableApiClient
from py_bitable.models import AttachmentFile, FieldMetadata


class Bitable:
    """High-level interface for Feishu Bitable operations.

    This class provides a user-friendly interface for interacting with Feishu Bitable,
    including uploading attachments and creating records with schema validation.
    """

    def __init__(
        self,
        app_id: str,
        app_secret: str,
        app_token: str,
        table_id: str,
        base_url: str = "https://open.feishu.cn/open-apis",
    ):
        """Initialize Bitable client.

        Args:
            app_id: Feishu app ID
            app_secret: Feishu app secret
            app_token: Bitable app token
            table_id: Table ID in the Bitable
            base_url: Feishu API base URL
        """
        self.app_token = app_token
        self.table_id = table_id
        self.client: BitableApiClient = BitableApiClient(app_id, app_secret, base_url)
        self._field_metadata: Optional[List[FieldMetadata]] = None
        self._field_name_to_id: Optional[Dict[str, str]] = None

    def create_table(
        self,
        table_name: str,
        field_metadata_list: List[FieldMetadata] = None,
    ):
        """
        Create a new table in the Bitable app.
        ref: https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-field/guide
        """
        d = {
            "table": {"name": table_name},
        }
        if field_metadata_list is not None:
            d["table"]["fields"] = [
                field.model_dump(exclude_none=True) for field in field_metadata_list
            ]
        return self.client.create_table(self.app_token, d)

    def get_table_schema(self) -> List[FieldMetadata]:
        """Fetch table schema from Feishu API.

        Returns:
            List of field metadata for the table
        """
        if self._field_metadata is None:
            self._field_metadata = self.client.get_table_fields(
                self.app_token, self.table_id
            )
            # Build name to ID mapping
            self._field_name_to_id = {
                field.field_name: field.field_id for field in self._field_metadata
            }

        return self._field_metadata

    def get_field_id(self, field_name: str) -> Optional[str]:
        """Get field ID by field name.

        Args:
            field_name: Name of the field

        Returns:
            Field ID or None if not found
        """
        if self._field_name_to_id is None:
            self.get_table_schema()

        return self._field_name_to_id.get(field_name)

    def upload_attachment_buffer(
        self, file_buffer: bytes, file_name: str, parent_type: str = "bitable_image"
    ) -> AttachmentFile:
        """Upload an attachment file from a byte buffer.

        Args:
            file_buffer: Byte content of the file to upload
            file_name: Name of the file
            parent_type: Parent type for the upload
        Returns:
            AttachmentFile with file token
        """
        # first write buffer to a temp file with name $filename in memory
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(file_buffer)
            tmp_file_path = tmp_file.name
        try:
            file_token = self.client.upload_file(
                tmp_file_path,
                parent_type=parent_type,
                parent_node=self.app_token,
                file_name=file_name,
            )
            print(f"  Uploaded file '{file_name}' with token: {file_token}")

            return AttachmentFile(
                file_token=file_token,
                name=file_name,
                size=len(file_buffer),
            )
        except Exception as e:
            print(f"  Failed to upload file '{file_name}': {e}")
            return None
        finally:
            os.remove(tmp_file_path)

    def upload_attachment(
        self, file_path: str, parent_type: str = "bitable_image"
    ) -> AttachmentFile:
        """Upload an attachment file.

        Args:
            file_path: Path to the file to upload
            parent_type: Parent type for the upload

        Returns:
            AttachmentFile with file token
        """
        import os

        try:
            file_token = self.client.upload_file(
                file_path, parent_type=parent_type, parent_node=self.app_token
            )
            print(f"  Uploaded file '{file_path}' with token: {file_token}")
        except Exception as e:
            print(f"  Failed to upload file '{file_path}': {e}")
            return None

        return AttachmentFile(
            file_token=file_token,
            name=os.path.basename(file_path),
            size=os.path.getsize(file_path),
        )

    def create_record(
        self,
        record_data: Union[Dict[str, Any], BaseModel],
    ) -> Dict[str, Any]:
        """Create a single record in the table.

        Args:
            record_data: Record data as dict or Pydantic model

        Returns:
            Created record data
        """
        # Convert Pydantic model to dict if needed
        if isinstance(record_data, BaseModel):
            record_dict = record_data.model_dump(exclude_none=True)
        else:
            record_dict = record_data

        # Create record
        response = self.client.batch_create_records(
            self.app_token, self.table_id, [record_dict]
        )

        if response.records:
            return response.records[0].model_dump()
        return {}

    def create_records(
        self,
        records_data: List[Union[Dict[str, Any], BaseModel]],
    ) -> List[Dict[str, Any]]:
        """Batch create records in the table.

        Args:
            records_data: List of record data (dicts or Pydantic models)

        Returns:
            List of created record data
        """
        # Convert all records
        records_list = []
        for record_data in records_data:
            # Convert Pydantic model to dict if needed
            if isinstance(record_data, BaseModel):
                record_dict = record_data.model_dump(exclude_none=True)
            else:
                record_dict = record_data

            records_list.append(record_dict)

        # Create records
        response = self.client.batch_create_records(
            self.app_token, self.table_id, records_list
        )

        return [record.model_dump() for record in response.records]

    def upload_and_create_record(
        self,
        record_data: Union[Dict[str, Any], BaseModel],
        attachment_files: Optional[Dict[str, Union[str, List[str]]]] = None,
    ) -> Dict[str, Any]:
        """Upload attachments and create a record with them.

        Args:
            record_data: Record data as dict or Pydantic model
            attachment_files: Dict mapping field names to file paths
                             (can be single path or list of paths)

        Returns:
            Created record data
        """
        # Convert Pydantic model to dict if needed
        if isinstance(record_data, BaseModel):
            record_dict = record_data.model_dump(exclude_none=True)
        else:
            record_dict = dict(record_data)

        # Upload attachments and add to record
        if attachment_files:
            for field_name, file_paths in attachment_files.items():
                # Ensure file_paths is a list
                if isinstance(file_paths, str):
                    file_paths = [file_paths]

                # Upload each file
                attachments = []
                for file_path in file_paths:
                    attachment = self.upload_attachment(file_path)
                    attachments.append(attachment.model_dump())

                # Add to record data
                record_dict[field_name] = attachments

        # Create the record
        return self.create_record(record_dict)
