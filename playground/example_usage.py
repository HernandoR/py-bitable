"""Example usage of py-bitable library.

This example demonstrates how to use the Bitable class to:
1. Get table schema
2. Create records
3. Upload attachments
"""

import os
from typing import Optional

from dotenv import find_dotenv, load_dotenv
from pydantic import BaseModel, Field

from py_bitable import Bitable
from py_bitable.models import FieldMetadata

load_dotenv(find_dotenv())


# Define a custom Pydantic schema for your records
class TaskRecord(BaseModel):
    """Custom schema for task records."""

    Name: str = Field(..., description="Task name")
    Description: Optional[str] = Field(None, description="Task description")
    Status: str = Field(default="Todo", description="Task status")
    Priority: int = Field(default=1, description="Task priority (1-5)")
    Assignee: Optional[str] = Field(None, description="Person assigned to task")

    @classmethod
    def get_fields_list(cls):
        return [
            FieldMetadata(field_name="Name", type=1),
            FieldMetadata(field_name="Description", type=1),
            FieldMetadata(field_name="Status", type=1),
            FieldMetadata(field_name="Priority", type=2),
            FieldMetadata(field_name="Assignee", type=1),
        ]


def main():
    """Main example function."""
    # Get credentials from environment variables
    # You should set these before running:
    # export FEISHU_APP_ID="your_app_id"
    # export FEISHU_APP_SECRET="your_app_secret"
    # export FEISHU_APP_TOKEN="your_bitable_app_token"
    # export FEISHU_TABLE_ID="your_table_id"

    app_id = os.getenv("FEISHU_APP_ID", "")
    app_secret = os.getenv("FEISHU_APP_SECRET", "")
    app_token = os.getenv("FEISHU_APP_TOKEN", "")
    table_id = os.getenv("FEISHU_TABLE_ID", "")

    if not all([app_id, app_secret, app_token, table_id]):
        print("Please set all required environment variables:")
        print("  FEISHU_APP_ID")
        print("  FEISHU_APP_SECRET")
        print("  FEISHU_APP_TOKEN")
        print("  FEISHU_TABLE_ID")
        return

    # Initialize Bitable client
    bitable = Bitable(
        app_id=app_id,
        app_secret=app_secret,
        app_token=app_token,
        table_id=table_id,
    )
    print("=== Creating table with specified fields ===")

    create_table_response = bitable.create_table(
        "recons_test",
        TaskRecord.get_fields_list(),
    )
    pass
    table_id = create_table_response.get("table_id")
    assert table_id is not None, (
        f"Table ID should not be None in response: {create_table_response}"
    )
    print(f"  Created table with ID: {table_id}")
    bitable.table_id = table_id

    # Example 1: Get table schema
    print("=== Getting table schema ===")
    schema = bitable.get_table_schema()
    for field in schema:
        print(f"  {field.field_name} (ID: {field.field_id}, Type: {field.type})")
    print()

    # Example 2: Create a simple record using dict
    print("=== Creating a simple record ===")
    record = bitable.create_record(
        {"Name": "Test Task", "Description": "This is a test task", "Status": "Todo"}
    )
    print(f"  Created record ID: {record.get('record_id')}")
    print()

    # Example 3: Create a record using Pydantic model
    print("=== Creating record with Pydantic model ===")
    task = TaskRecord(
        Name="Important Task",
        Description="This task uses Pydantic validation",
        Status="In Progress",
        Priority=5,
        Assignee="John Doe",
    )
    record = bitable.create_record(task)
    print(f"  Created record ID: {record.get('record_id')}")
    print()

    # Example 4: Batch create records
    print("=== Batch creating records ===")
    tasks = [
        {"Name": "Task 1", "Status": "Todo", "Priority": 1},
        {"Name": "Task 2", "Status": "In Progress", "Priority": 2},
        {"Name": "Task 3", "Status": "Done", "Priority": 3},
    ]
    records = bitable.create_records(tasks)
    print(f"  Created {len(records)} records")
    for i, record in enumerate(records, 1):
        print(f"    {i}. Record ID: {record.get('record_id')}")
    print()

    # Example 5: Upload attachment and create record
    # Note: This requires an actual file to upload
    print("=== Upload attachment example (disabled) ===")
    print("  To enable, create a test file and uncomment the code below")
    print()

    # Uncomment to test file upload:
    test_file = "output/file.txt"
    with open(test_file, "w") as f:
        f.write("This is a test file for attachment upload.\n")

    record = bitable.upload_and_create_record(
        record_data={
            "Name": "Task with attachment",
            "Description": "This task has a file attached",
        },
        attachment_files={"Attachments": test_file},
    )
    print(f"  Created record with attachment: {record.get('record_id')}")

    print("=== Examples completed ===")


if __name__ == "__main__":
    main()
