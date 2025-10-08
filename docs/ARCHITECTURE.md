# Architecture Guide

## Overview

`py-bitable` is a Python library for interacting with Feishu Bitable (飞书多维表格). It provides both low-level and high-level APIs for common operations like uploading attachments and creating records.

## Architecture

The library is structured in three main layers:

```
┌─────────────────────────────────────────┐
│           User Application              │
│  (Custom Pydantic schemas, business     │
│   logic)                                │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│         Bitable (High-level)            │
│  - Schema management                    │
│  - Field name ↔ ID mapping             │
│  - Batch operations                     │
│  - Pydantic model support               │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│     BitableApiClient (Low-level)        │
│  - Authentication                       │
│  - Direct API calls                     │
│  - Request/Response handling            │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│         Feishu Open API                 │
│  - Bitable API                          │
│  - Drive API (file upload)              │
└─────────────────────────────────────────┘
```

### Layer 1: BitableApiClient (Low-level)

The `BitableApiClient` class provides direct access to Feishu APIs:

- **Authentication**: Manages tenant access tokens
- **File Upload**: Implements multipart upload protocol
  - `upload_file_prepare()`: Prepare upload session
  - `upload_file_part()`: Upload file chunks
  - `upload_file_finish()`: Finalize upload
  - `upload_file()`: Complete upload workflow
- **Table Operations**:
  - `get_table_fields()`: Retrieve table schema
  - `batch_create_records()`: Create multiple records

**Use this layer when:**
- You need fine-grained control over API calls
- You want to implement custom retry logic
- You're building your own abstraction layer

### Layer 2: Bitable (High-level)

The `Bitable` class provides a user-friendly interface:

- **Schema Management**:
  - Automatic fetching and caching of table schema
  - Field name to field ID mapping
- **Record Operations**:
  - `create_record()`: Create single record
  - `create_records()`: Batch create records
  - Support for both dicts and Pydantic models
- **Attachment Handling**:
  - `upload_attachment()`: Upload files
  - `upload_and_create_record()`: Combined operation

**Use this layer when:**
- You want simple, straightforward operations
- You prefer using field names over field IDs
- You want automatic schema validation with Pydantic

### Layer 3: Data Models

Pydantic models ensure type safety and validation:

- **API Models**: Mirror Feishu API structures
  - `FieldMetadata`: Table field information
  - `BitableRecord`: Record data
  - `AttachmentFile`: File metadata
- **Request/Response Models**: API communication
  - `UploadPrepareResponse`
  - `BatchCreateRecordsResponse`
- **User Models**: Extensible base classes
  - `RecordField`: Base for custom schemas

## Usage Patterns

### Pattern 1: Simple Record Creation

```python
from py_bitable import Bitable

bitable = Bitable(app_id, app_secret, app_token, table_id)

# Using field names (automatic conversion to field IDs)
record = bitable.create_record({
    "Name": "John Doe",
    "Email": "john@example.com"
})
```

### Pattern 2: Typed Records with Pydantic

```python
from pydantic import BaseModel, Field
from typing import Optional

class UserRecord(BaseModel):
    Name: str
    Email: str
    Age: Optional[int] = None
    Department: str = "Engineering"

# Automatic validation
user = UserRecord(Name="Jane", Email="jane@example.com", Age=30)
record = bitable.create_record(user)
```

### Pattern 3: Batch Operations

```python
# Create multiple records efficiently
records = bitable.create_records([
    {"Name": "User 1", "Status": "Active"},
    {"Name": "User 2", "Status": "Active"},
    {"Name": "User 3", "Status": "Pending"},
])
```

### Pattern 4: Attachments

```python
# Upload file and create record
record = bitable.upload_and_create_record(
    record_data={"Name": "Document", "Type": "PDF"},
    attachment_files={
        "Attachments": "/path/to/file.pdf"
    }
)

# Multiple attachments
record = bitable.upload_and_create_record(
    record_data={"Name": "Project Assets"},
    attachment_files={
        "Images": ["/path/to/img1.png", "/path/to/img2.png"],
        "Documents": "/path/to/doc.pdf"
    }
)
```

### Pattern 5: Schema Introspection

```python
# Get table structure
schema = bitable.get_table_schema()

for field in schema:
    print(f"{field.field_name}: Type {field.type}")
    if field.is_primary:
        print(f"  → Primary key")

# Get field ID for a specific field
field_id = bitable.get_field_id("Email")
```

### Pattern 6: Low-level API Access

```python
from py_bitable import BitableApiClient

client = BitableApiClient(app_id, app_secret)

# Direct API calls with field IDs
response = client.batch_create_records(
    app_token=app_token,
    table_id=table_id,
    records=[
        {"fld1234": "value1", "fld5678": "value2"}
    ]
)
```

## Field Name vs Field ID

Feishu Bitable uses field IDs internally, but displays field names to users.

**Field Names** (e.g., "Name", "Email"):
- Human-readable
- Can change over time
- Used in the UI

**Field IDs** (e.g., "fld1234", "fld5678"):
- Machine-readable
- Permanent identifiers
- Used in API calls

The `Bitable` class automatically handles the conversion:

```python
# You write:
bitable.create_record({"Name": "John", "Email": "john@example.com"})

# Library converts to:
# {"fld1234": "John", "fld5678": "john@example.com"}
```

To disable automatic conversion:

```python
bitable.create_record(
    {"fld1234": "John", "fld5678": "john@example.com"},
    use_field_names=False
)
```

## Best Practices

### 1. Reuse Bitable Instances

```python
# Good: Reuse instance (schema cached)
bitable = Bitable(app_id, app_secret, app_token, table_id)
for item in items:
    bitable.create_record(item)

# Bad: Create new instance each time
for item in items:
    bitable = Bitable(app_id, app_secret, app_token, table_id)
    bitable.create_record(item)  # Re-fetches schema every time
```

### 2. Use Batch Operations

```python
# Good: Batch create
bitable.create_records(items)

# Less efficient: Individual creates
for item in items:
    bitable.create_record(item)
```

### 3. Define Pydantic Schemas

```python
# Good: Type-safe with validation
class TaskRecord(BaseModel):
    name: str
    priority: int = Field(ge=1, le=5)  # Validates 1-5
    status: str = Field(pattern="^(Todo|Done)$")  # Enum-like

# Bad: No validation
record = {"name": "Task", "priority": 100, "status": "Invalid"}
```

## Security

- **Credentials**: Never hardcode app_id and app_secret
- **Environment Variables**: Use environment variables for credentials
- **Token Management**: Access tokens are cached but not persisted
- **File Validation**: Validate file types and sizes before upload
