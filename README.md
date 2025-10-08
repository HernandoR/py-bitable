# py-bitable

Python library for uploading attachments and creating records in Feishu Bitable (飞书多维表格).

## Features

- **Upload attachments** to Feishu Bitable using multipart upload API
- **Create records** in Bitable tables with batch support
- **Schema validation** using Pydantic models
- **Automatic field mapping** between field names and field IDs
- **Type-safe** data models for API requests and responses

## Installation

Using uv (recommended):

```bash
uv add py-bitable
```

Or using pip:

```bash
pip install py-bitable
```

## Quick Start

### Basic Usage

```python
from py_bitable import Bitable

# Initialize Bitable client
bitable = Bitable(
    app_id="your_app_id",
    app_secret="your_app_secret",
    app_token="your_bitable_app_token",
    table_id="your_table_id"
)

# Get table schema
schema = bitable.get_table_schema()
for field in schema:
    print(f"{field.field_name}: {field.type}")

# Create a simple record
record = bitable.create_record({
    "Name": "John Doe",
    "Age": 30,
    "Email": "john@example.com"
})
print(f"Created record: {record['record_id']}")
```

### Upload Attachments

```python
# Upload attachment and create record
record = bitable.upload_and_create_record(
    record_data={
        "Name": "Project Document",
        "Description": "Important document"
    },
    attachment_files={
        "Attachments": "/path/to/file.pdf"  # Single file
    }
)

# Upload multiple attachments
record = bitable.upload_and_create_record(
    record_data={
        "Name": "Project Images"
    },
    attachment_files={
        "Images": [
            "/path/to/image1.png",
            "/path/to/image2.png"
        ]
    }
)
```

### Using Pydantic Models

```python
from pydantic import BaseModel
from typing import Optional

class ProjectRecord(BaseModel):
    Name: str
    Description: Optional[str] = None
    Status: str = "In Progress"
    Priority: int = 1

# Create record with validation
record_data = ProjectRecord(
    Name="New Project",
    Description="A new project",
    Priority=5
)

record = bitable.create_record(record_data)
```

### Batch Create Records

```python
# Create multiple records at once
records = bitable.create_records([
    {"Name": "Task 1", "Status": "Todo"},
    {"Name": "Task 2", "Status": "In Progress"},
    {"Name": "Task 3", "Status": "Done"}
])

print(f"Created {len(records)} records")
```

### Low-level API Client

For more control, use the `BitableApiClient` directly:

```python
from py_bitable import BitableApiClient

client = BitableApiClient(
    app_id="your_app_id",
    app_secret="your_app_secret"
)

# Upload a file
file_token = client.upload_file("/path/to/file.pdf")

# Get table fields
fields = client.get_table_fields(app_token, table_id)

# Create records
response = client.batch_create_records(
    app_token=app_token,
    table_id=table_id,
    records=[{"field_id_1": "value1", "field_id_2": "value2"}]
)
```

## API Reference

### Bitable

Main class for high-level operations.

**Methods:**
- `get_table_schema()` - Fetch table schema from Feishu API
- `get_field_id(field_name)` - Get field ID by field name
- `upload_attachment(file_path)` - Upload a file and get attachment info
- `create_record(record_data, use_field_names=True)` - Create a single record
- `create_records(records_data, use_field_names=True)` - Batch create records
- `upload_and_create_record(record_data, attachment_files, use_field_names=True)` - Upload files and create record

### BitableApiClient

Low-level API client for direct API calls.

**Methods:**
- `get_table_fields(app_token, table_id)` - Get table field metadata
- `upload_file(file_path, parent_type, parent_node)` - Upload a file completely
- `batch_create_records(app_token, table_id, records)` - Batch create records

## Configuration

The library requires Feishu app credentials:

- `app_id`: Your Feishu app ID
- `app_secret`: Your Feishu app secret
- `app_token`: The Bitable app token
- `table_id`: The table ID in the Bitable

You can find these in the Feishu Open Platform console.

## References

- [Feishu Python SDK Documentation](https://open.feishu.cn/document/server-side-sdk/python--sdk/invoke-server-api)
- [Bitable Field API](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-field/attachment)
- [Multipart Upload API](https://open.feishu.cn/document/server-docs/docs/drive-v1/media/multipart-upload-media/upload_prepare)
- [Batch Create Records API](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/batch_create)

## License

MIT
