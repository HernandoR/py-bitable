"""Integration test example for py-bitable.

This file demonstrates how to run integration tests against a real Feishu Bitable.
To run these tests, you need to set up environment variables with valid credentials.

Setup:
    export FEISHU_APP_ID="your_app_id"
    export FEISHU_APP_SECRET="your_app_secret"
    export FEISHU_APP_TOKEN="your_bitable_app_token"
    export FEISHU_TABLE_ID="your_table_id"

Run:
    python tests/integration_test.py
"""

import os
import sys

from py_bitable import Bitable


def test_connection():
    """Test basic connection and authentication."""
    print("Testing connection...")

    app_id = os.getenv("FEISHU_APP_ID")
    app_secret = os.getenv("FEISHU_APP_SECRET")
    app_token = os.getenv("FEISHU_APP_TOKEN")
    table_id = os.getenv("FEISHU_TABLE_ID")

    if not all([app_id, app_secret, app_token, table_id]):
        print("⚠ Skipping integration test - credentials not configured")
        print("Set FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_APP_TOKEN, FEISHU_TABLE_ID")
        return False

    try:
        bitable = Bitable(
            app_id=app_id,
            app_secret=app_secret,
            app_token=app_token,
            table_id=table_id,
        )

        # Test getting schema
        schema = bitable.get_table_schema()
        print(f"✓ Successfully retrieved {len(schema)} fields from table")

        for field in schema[:5]:  # Show first 5 fields
            print(f"  - {field.field_name} (Type: {field.type})")

        return True
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        return False


def test_create_record():
    """Test creating a record (commented out to avoid accidental writes)."""
    print("\nTest create record (disabled by default)")
    print("Uncomment the code in integration_test.py to enable record creation")

    # Uncomment below to test record creation:
    # app_id = os.getenv("FEISHU_APP_ID")
    # app_secret = os.getenv("FEISHU_APP_SECRET")
    # app_token = os.getenv("FEISHU_APP_TOKEN")
    # table_id = os.getenv("FEISHU_TABLE_ID")
    #
    # if not all([app_id, app_secret, app_token, table_id]):
    #     return False
    #
    # try:
    #     bitable = Bitable(
    #         app_id=app_id,
    #         app_secret=app_secret,
    #         app_token=app_token,
    #         table_id=table_id,
    #     )
    #
    #     # Create a test record
    #     record = bitable.create_record({
    #         "Name": "Integration Test Record",
    #         "Description": "Created by integration test"
    #     })
    #     print(f"✓ Created record: {record.get('record_id')}")
    #     return True
    # except Exception as e:
    #     print(f"✗ Failed to create record: {e}")
    #     return False


def main():
    """Run integration tests."""
    print("=" * 60)
    print("py-bitable Integration Tests")
    print("=" * 60)
    print()

    results = []

    # Test 1: Connection and schema retrieval
    results.append(("Connection Test", test_connection()))

    # Test 2: Record creation (disabled by default)
    test_create_record()

    # Summary
    print()
    print("=" * 60)
    print("Summary:")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print("=" * 60)

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
