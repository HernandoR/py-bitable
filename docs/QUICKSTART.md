# Quick Start Guide

## Installation

```bash
pip install py-bitable
```

Or using uv:

```bash
uv add py-bitable
```

## Getting Your Credentials

1. Go to [Feishu Open Platform](https://open.feishu.cn/)
2. Create an application or use an existing one
3. Get your `app_id` and `app_secret` from the app credentials page
4. Get the `app_token` from your Bitable URL (it's the part after `/base/`)
   - Example: `https://example.feishu.cn/base/XYZ123abc` → app_token is `XYZ123abc`
5. Get the `table_id` from the table URL
   - Example: table URL contains `&table=tblABC123` → table_id is `tblABC123`

## Your First Program

```python
from py_bitable import Bitable

# Initialize the client
bitable = Bitable(
    app_id="cli_a1b2c3d4e5f6g7h8",
    app_secret="your_app_secret_here",
    app_token="bascnABCDEFGHIJKLMN",
    table_id="tblXYZ123456",
)

# Create a record
record = bitable.create_record({
    "Name": "My First Record",
    "Status": "Active",
})

print(f"Created record: {record['record_id']}")
```

## Common Tasks

### 1. Get Table Schema

```python
schema = bitable.get_table_schema()

for field in schema:
    print(f"{field.field_name} ({field.field_id}): Type {field.type}")
```

### 2. Create Multiple Records

```python
records = bitable.create_records([
    {"Name": "Alice", "Department": "Engineering"},
    {"Name": "Bob", "Department": "Sales"},
    {"Name": "Charlie", "Department": "Marketing"},
])

print(f"Created {len(records)} records")
```

### 3. Upload a File

```python
record = bitable.upload_and_create_record(
    record_data={
        "Name": "Project Report",
        "Description": "Q4 2024 Report"
    },
    attachment_files={
        "Attachments": "/path/to/report.pdf"
    }
)
```

### 4. Using Pydantic for Validation

```python
from pydantic import BaseModel, Field
from typing import Optional

class Employee(BaseModel):
    Name: str
    Email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    Department: str
    Salary: Optional[int] = Field(None, ge=0)

# This will validate the data before creating the record
employee = Employee(
    Name="John Doe",
    Email="john@company.com",
    Department="IT",
    Salary=75000
)

record = bitable.create_record(employee)
```

### 5. Error Handling

```python
try:
    record = bitable.create_record({
        "Name": "Test Record"
    })
except ValueError as e:
    print(f"API Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Environment Variables

For security, store credentials in environment variables:

```python
import os
from py_bitable import Bitable

bitable = Bitable(
    app_id=os.getenv("FEISHU_APP_ID"),
    app_secret=os.getenv("FEISHU_APP_SECRET"),
    app_token=os.getenv("FEISHU_APP_TOKEN"),
    table_id=os.getenv("FEISHU_TABLE_ID"),
)
```

Set environment variables:

```bash
export FEISHU_APP_ID="your_app_id"
export FEISHU_APP_SECRET="your_secret"
export FEISHU_APP_TOKEN="your_app_token"
export FEISHU_TABLE_ID="your_table_id"
```

Or use a `.env` file with `python-dotenv`:

```
FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_secret
FEISHU_APP_TOKEN=your_app_token
FEISHU_TABLE_ID=your_table_id
```

```python
from dotenv import load_dotenv
import os

load_dotenv()

bitable = Bitable(
    app_id=os.getenv("FEISHU_APP_ID"),
    app_secret=os.getenv("FEISHU_APP_SECRET"),
    app_token=os.getenv("FEISHU_APP_TOKEN"),
    table_id=os.getenv("FEISHU_TABLE_ID"),
)
```

## Next Steps

- Read the [Architecture Guide](ARCHITECTURE.md) for deeper understanding
- Check out the [example_usage.py](../playground/example_usage.py) for more examples
- See the [API Reference](../README.md#api-reference) for all available methods
- Run the integration tests to verify your setup

## Troubleshooting

### "Failed to get access token"

- Verify your `app_id` and `app_secret` are correct
- Check that your app has the necessary permissions in Feishu

### "Failed to get table fields"

- Verify the `app_token` and `table_id` are correct
- Ensure your app has permission to access the Bitable

### "Failed to create records"

- Check that field names match exactly (case-sensitive)
- Verify the data types match the field types in the table
- Make sure required fields are provided

### Import Errors

```python
# If you get import errors, try:
pip install --upgrade py-bitable

# Or reinstall:
pip uninstall py-bitable
pip install py-bitable
```
