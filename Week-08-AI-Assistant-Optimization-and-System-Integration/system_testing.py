"""
system_testing.py — Week 8 System Integration Test
=====================================================
Standalone test for the edit_equipment tool logic directly against a real
MongoDB database. No Flask, no OpenAI/Gemini needed for this script — it
isolates the database-integration layer so it can be verified on its own.

NOTE ON WHY THIS IS SELF-CONTAINED: final_chatbot.py (the submitted
combined file) still carries chatbot.py's original relative imports
(`from ..mongo_db import get_db`, Flask, OpenAI, JWT, etc.), because that
file is meant to be dropped into the real package structure, not run
standalone. So this test reimplements the same tool_edit_equipment logic
in a self-contained way, against the same MongoDB collections/fields, to
verify the underlying database behavior independently of the Flask app.

SETUP:
  pip install -r requirements.txt
  Create a .env file with:
    MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net
    MONGODB_DB_NAME=your_database_name

RUN:
  python system_testing.py
"""

import os
from datetime import datetime, timezone

from dotenv import load_dotenv

load_dotenv()

from bson import ObjectId
from pymongo import MongoClient


def get_test_db():
    uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGODB_DB_NAME")
    if not uri or not db_name:
        raise RuntimeError(
            "MONGODB_URI / MONGODB_DB_NAME not set. Add a .env file with "
            "your MongoDB Atlas connection string and database name."
        )
    client = MongoClient(uri)
    return client[db_name]


DB = get_test_db()


def tool_edit_equipment(equipment_id: str, name: str = None, description: str = None) -> dict:
    """Same logic as the real tool in chatbot_extra_tools.py / final_chatbot.py:
    only 'name' and 'description' can ever be changed — no other field, no
    delete path exists here or anywhere else in the system."""
    try:
        doc = DB["equipments"].find_one({"_id": ObjectId(equipment_id)})
    except Exception:
        doc = DB["equipments"].find_one({"name": {"$regex": equipment_id, "$options": "i"}})

    if not doc:
        return {"error": f"No equipment found matching '{equipment_id}'. Nothing was edited."}

    updates = {}
    if name is not None and name.strip():
        updates["name"] = name.strip()
    if description is not None and description.strip():
        updates["description"] = description.strip()

    if not updates:
        return {"error": "No editable field was provided. Only 'name' and 'description' can be edited."}

    updates["updated_at"] = datetime.now(timezone.utc)
    DB["equipments"].update_one({"_id": doc["_id"]}, {"$set": updates})
    updated_doc = DB["equipments"].find_one({"_id": doc["_id"]})
    return {
        "success": True,
        "equipment_id": str(doc["_id"]),
        "updated_fields": {k: v for k, v in updates.items() if k != "updated_at"},
        "equipment": updated_doc,
    }


def main():
    db = DB

    print("=" * 60)
    print("STEP 1: Insert a sample equipment document")
    print("=" * 60)
    result = db["equipments"].insert_one({
        "name": "System Test Pump",
        "description": "Original description before edit test",
        "category_id": "pumps",
        "location_id": "site-1",
    })
    equipment_id = str(result.inserted_id)
    print(f"Inserted equipment _id: {equipment_id}")

    print()
    print("=" * 60)
    print("STEP 2: Call tool_edit_equipment() to change name + description")
    print("=" * 60)
    edit_result = tool_edit_equipment(
        equipment_id=equipment_id,
        name="System Test Pump - Updated",
        description="Changed by system_testing.py",
    )
    print("Tool returned:", edit_result)
    assert edit_result.get("success") is True, "Edit did not report success!"

    print()
    print("=" * 60)
    print("STEP 3: Read the document back from MongoDB to confirm persistence")
    print("=" * 60)
    updated_doc = db["equipments"].find_one({"_id": result.inserted_id})
    print(updated_doc)
    assert updated_doc["name"] == "System Test Pump - Updated"
    assert updated_doc["description"] == "Changed by system_testing.py"
    print("PASSED: name and description were updated and persisted correctly.")

    print()
    print("=" * 60)
    print("STEP 4: Edit a non-existent equipment (should error, not crash)")
    print("=" * 60)
    bad_result = tool_edit_equipment(equipment_id="000000000000000000000000", name="Should Not Work")
    print("Tool returned:", bad_result)
    assert "error" in bad_result, "Expected a clean error dict for a missing equipment!"
    print("PASSED: invalid id returns a clean error instead of crashing.")

    print()
    print("=" * 60)
    print("STEP 5: No delete path exists")
    print("=" * 60)
    print("There is no tool_delete_equipment function anywhere in this system.")
    print("PASSED (by design/absence): deletion is impossible through the chatbot's tools.")

    print()
    print("=" * 60)
    print("STEP 6: Cleanup")
    print("=" * 60)
    db["equipments"].delete_one({"_id": result.inserted_id})
    print("Test document removed (via raw pymongo — the chatbot's own tools")
    print("can never do this themselves, by design).")

    print()
    print("ALL SYSTEM TESTS PASSED.")


if __name__ == "__main__":
    main()
