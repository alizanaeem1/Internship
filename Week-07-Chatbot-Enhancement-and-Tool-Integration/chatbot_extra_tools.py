"""
chatbot_extra_tools.py
────────────────────────────────────────────────────────────────────────────
Isolated add-on module for Mr. Larson (T29 chatbot).

Purpose: add support for Purchase Orders, Vendors, Users, Roles, Job Dispatch,
and the shared Document Library WITHOUT touching the working chatbot.py logic.

chatbot.py only needs to import EXTRA_TOOLS / EXTRA_TOOL_MAP / EXTRA_VALID_ROUTES /
EXTRA_SYSTEM_PROMPT from here, wrapped in try/except, so that any bug in this
file can never break the already-working equipment/maintenance/certifications
chatbot flow.

NOTE ON FIELD NAMES: the field names below (po_number, vendor, folder_id,
job_type, etc.) are best-guess based on screenshots of the UI, NOT confirmed
against the real MongoDB documents. Test each tool once real/sample data
exists and adjust field names in the query/projection if results come back
empty or wrong.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

from bson import ObjectId

from ..mongo_db import get_db


# ── Local helpers (kept separate from chatbot.py's _sid / _search_text on
#    purpose, so this file has zero dependency on chatbot.py internals) ───────

def _sid(doc: dict) -> dict:
    out = {}
    for k, v in doc.items():
        if k == "password":
            continue
        if isinstance(v, ObjectId):
            out[k] = str(v)
        elif isinstance(v, datetime):
            out[k] = v.isoformat()
        elif isinstance(v, dict):
            out[k] = _sid(v)
        elif isinstance(v, list):
            out[k] = [_sid(i) if isinstance(i, dict) else (str(i) if isinstance(i, ObjectId) else i) for i in v]
        else:
            out[k] = v
    return out


def _search_text(text: str, fields: list[str]) -> dict:
    pattern = re.compile(re.escape(text), re.IGNORECASE)
    return {"$or": [{f: {"$regex": pattern}} for f in fields]}


# ── Shared edit helper (used by ALL per-collection edit_* tools below) ──────
#
# HARD SAFETY RULE: this helper only ever does $set on an explicit, small
# whitelist of fields chosen per-collection by each wrapper function below.
# There is no generic "update any field" path and no delete path anywhere
# in this file — that is intentional, not an oversight.

def _edit_by_id(collection: str, record_id: str, updates: dict) -> dict:
    db = get_db()
    try:
        doc = db[collection].find_one({"_id": ObjectId(record_id)})
    except Exception:
        doc = None

    if not doc:
        return {"error": f"No record found in '{collection}' matching id '{record_id}'. Nothing was edited."}

    clean_updates = {
        k: (v.strip() if isinstance(v, str) else v)
        for k, v in updates.items()
        if v is not None and (not isinstance(v, str) or v.strip())
    }
    if not clean_updates:
        return {"error": "No editable field was provided."}

    clean_updates["updated_at"] = datetime.now(timezone.utc)
    db[collection].update_one({"_id": doc["_id"]}, {"$set": clean_updates})
    updated = db[collection].find_one({"_id": doc["_id"]})
    return {
        "success": True,
        "id": str(doc["_id"]),
        "updated_fields": {k: v for k, v in clean_updates.items() if k != "updated_at"},
        "record": _sid(updated),
    }


# ── Tool implementations ───────────────────────────────────────────────────

def tool_get_purchase_orders(search: str | None = None, status: str | None = None) -> list[dict]:
    db = get_db()
    query: dict = {}
    if status:
        query["status"] = {"$regex": re.escape(status), "$options": "i"}
    if search:
        query.update(_search_text(search, ["po_number", "vendor", "location", "created_by"]))
    docs = list(db["purchase_orders"].find(query).sort("created_at", -1).limit(20))
    return [_sid(d) for d in docs]


def tool_get_vendors(search: str | None = None) -> list[dict]:
    db = get_db()
    query = _search_text(search, ["name"]) if search else {}
    docs = list(db["vendors"].find(query).limit(20))
    return [_sid(d) for d in docs]


def tool_get_users(search: str | None = None) -> list[dict]:
    db = get_db()
    query = _search_text(search, ["name", "email"]) if search else {}
    docs = list(db["users"].find(query, {
        "_id": 1, "name": 1, "email": 1, "role": 1, "role_id": 1, "created_at": 1
    }).limit(20))
    return [_sid(d) for d in docs]


def tool_get_roles(search: str | None = None) -> list[dict]:
    db = get_db()
    query = _search_text(search, ["name", "description"]) if search else {}
    docs = list(db["roles"].find(query).limit(20))
    return [_sid(d) for d in docs]


def tool_get_jobs(search: str | None = None) -> list[dict]:
    db = get_db()
    query = _search_text(search, ["title", "name", "job_type", "assigned_to", "status"]) if search else {}
    docs = list(db["job_dispatch_templates"].find(query).sort("created_at", -1).limit(20))
    return [_sid(d) for d in docs]


def tool_get_library_folders(search: str | None = None) -> list[dict]:
    db = get_db()
    query = _search_text(search, ["name"]) if search else {}
    docs = list(db["misc_library_folders"].find(query).limit(20))
    return [_sid(d) for d in docs]


def tool_get_library_documents(folder_id: str | None = None, search: str | None = None) -> list[dict]:
    db = get_db()
    query: dict = {}
    if folder_id:
        query["folder_id"] = folder_id
    if search:
        query.update(_search_text(search, ["document_name", "name"]))
    docs = list(db["misc_library_documents"].find(query).limit(20))
    return [_sid(d) for d in docs]


# ── NEW: Audit Log ───────────────────────────────────────────────────────────

def tool_get_audit_logs(search: str | None = None, entity_type: str | None = None) -> list[dict]:
    """Confirmed against app/routes/audit_logs.py: fields user_name, entity_type,
    action, summary, created_at on the 'audit_logs' collection."""
    db = get_db()
    query: dict = {}
    if entity_type:
        query["entity_type"] = entity_type
    if search:
        query.update(_search_text(search, ["user_name", "summary", "action"]))
    docs = list(db["audit_logs"].find(query).sort("created_at", -1).limit(20))
    return [_sid(d) for d in docs]


# ── NEW: BBS Good Catch ──────────────────────────────────────────────────────

def tool_get_bbs_entries(status: str | None = None, search: str | None = None) -> list[dict]:
    """Confirmed against app/routes/bbs.py: 'bbs_entries' collection. Fields:
    token, status (Pending/Assigned/Performed/Completed/Archived), location,
    observer_name, observations, assignee_names, submitted_by_name."""
    db = get_db()
    query: dict = {}
    if status:
        query["status"] = {"$regex": re.escape(status), "$options": "i"}
    if search:
        query.update(_search_text(search, ["token", "location", "observer_name", "submitted_by_name"]))
    docs = list(db["bbs_entries"].find(query, {
        "_id": 1, "token": 1, "status": 1, "location": 1, "observer_name": 1,
        "observations": 1, "assignee_names": 1, "submitted_by_name": 1, "created_at": 1
    }).sort("created_at", -1).limit(20))
    return [_sid(d) for d in docs]


def tool_get_bbs_summary() -> dict:
    """Overall BBS Good Catch counts by status, across all entries."""
    db = get_db()
    statuses = ("Pending", "Assigned", "Performed", "Completed", "Archived")
    counts = {s: db["bbs_entries"].count_documents({"status": s}) for s in statuses}
    counts["total"] = db["bbs_entries"].count_documents({})
    return counts


# ── NEW: Safety Portal ───────────────────────────────────────────────────────

def tool_get_safety_buttons(search: str | None = None) -> list[dict]:
    """Confirmed collection name 'safety_portal_buttons' from audit_logs.py's
    _doc("safety_portal_buttons", ...) lookup. Exact field names beyond 'title'
    are a best guess — verify once real safety buttons exist."""
    db = get_db()
    query = _search_text(search, ["title", "description"]) if search else {}
    docs = list(db["safety_portal_buttons"].find(query).limit(20))
    return [_sid(d) for d in docs]


# ── NEW: Compliance / Employee Qualifications ────────────────────────────────

def tool_get_qualification_schedule(search: str | None = None, employee_id: str | None = None) -> list[dict]:
    """Confirmed from EmployeeQualificationSchedule.tsx: fields employee_name,
    qualification_type, date_completed, expiry_date, employee_id."""
    db = get_db()
    query: dict = {}
    if employee_id:
        query["employee_id"] = employee_id
    if search:
        query.update(_search_text(search, ["employee_name", "qualification_type"]))
    docs = list(db["employee_qualifications"].find(query).sort("expiry_date", 1).limit(25))
    return [_sid(d) for d in docs]


# ── NEW: Equipment Edit (name / description ONLY — no delete, no other fields) ──
#
# Scope, per product decision: the chatbot may EDIT an equipment's name and/or
# description. It must NEVER delete anything. It also must not touch any other
# field (category, location, images, etc.) until that's explicitly asked for
# and implemented — keeping the whitelist tiny is the safety mechanism here.

EDITABLE_EQUIPMENT_FIELDS = {"name", "description"}


def tool_edit_equipment(equipment_id: str, name: str | None = None, description: str | None = None) -> dict:
    """Update ONLY the name and/or description of an existing equipment.

    - Resolves equipment_id the same way tool_get_equipment_detail does
      (ObjectId first, then falls back to a case-insensitive name match).
    - Only fields explicitly passed (not None) are updated.
    - Returns an error dict (never raises) if the equipment can't be found or
      if no valid field was provided, so the chatbot can surface a clean
      message to the user instead of crashing the tool loop.
    """
    db = get_db()

    try:
        doc = db["equipments"].find_one({"_id": ObjectId(equipment_id)})
    except Exception:
        doc = db["equipments"].find_one({"name": {"$regex": re.escape(equipment_id), "$options": "i"}})

    if not doc:
        return {"error": f"No equipment found matching '{equipment_id}'. Nothing was edited."}

    updates: dict = {}
    if name is not None and name.strip():
        updates["name"] = name.strip()
    if description is not None and description.strip():
        updates["description"] = description.strip()

    if not updates:
        return {"error": "No editable field was provided. Only 'name' and 'description' can be edited."}

    updates["updated_at"] = datetime.now(timezone.utc)

    db["equipments"].update_one({"_id": doc["_id"]}, {"$set": updates})
    updated_doc = db["equipments"].find_one({"_id": doc["_id"]})
    return {
        "success": True,
        "equipment_id": str(doc["_id"]),
        "updated_fields": {k: v for k, v in updates.items() if k != "updated_at"},
        "equipment": _sid(updated_doc),
    }


# ── NEW: Edit tools for the other collections (each limited to a small,
#    sensible field whitelist via explicit named parameters — same safety
#    pattern as tool_edit_equipment above). NOTE: users and roles are
#    deliberately NOT editable here — changing access/permissions from the
#    chatbot is a security risk and out of scope until explicitly asked for
#    and reviewed separately). Audit logs are also never editable — they are
#    a trail of what happened and must stay immutable.

def tool_edit_certification(
    certification_id: str,
    certification_name: str | None = None,
    certification_date: str | None = None,
    expiry_date: str | None = None,
    certified_by: str | None = None,
) -> dict:
    return _edit_by_id("certifications", certification_id, {
        "certification_name": certification_name,
        "certification_date": certification_date,
        "expiry_date": expiry_date,
        "certified_by": certified_by,
    })


def tool_edit_maintenance(
    maintenance_id: str,
    name: str | None = None,
    type: str | None = None,
    performed_by: str | None = None,
    next_due_date: str | None = None,
) -> dict:
    return _edit_by_id("maintenance", maintenance_id, {
        "name": name,
        "type": type,
        "performed_by": performed_by,
        "next_due_date": next_due_date,
    })


def tool_edit_document(
    document_id: str,
    document_name: str | None = None,
    document_type: str | None = None,
) -> dict:
    return _edit_by_id("additional_documents", document_id, {
        "document_name": document_name,
        "document_type": document_type,
    })


def tool_edit_work_order(
    work_order_id: str,
    service_type: str | None = None,
    location: str | None = None,
    unit: str | None = None,
    performed_by: str | None = None,
) -> dict:
    return _edit_by_id("workorders", work_order_id, {
        "service_type": service_type,
        "location": location,
        "unit": unit,
        "performed_by": performed_by,
    })


def tool_edit_template(
    template_id: str,
    name: str | None = None,
    description: str | None = None,
) -> dict:
    return _edit_by_id("templates", template_id, {
        "name": name,
        "description": description,
    })


def tool_edit_purchase_order(
    po_id: str,
    vendor: str | None = None,
    location: str | None = None,
    status: str | None = None,
) -> dict:
    return _edit_by_id("purchase_orders", po_id, {
        "vendor": vendor,
        "location": location,
        "status": status,
    })


def tool_edit_vendor(vendor_id: str, name: str | None = None) -> dict:
    return _edit_by_id("vendors", vendor_id, {"name": name})


def tool_edit_job(
    job_id: str,
    job_type: str | None = None,
    assigned_to: str | None = None,
    status: str | None = None,
) -> dict:
    return _edit_by_id("job_dispatch_templates", job_id, {
        "job_type": job_type,
        "assigned_to": assigned_to,
        "status": status,
    })


def tool_edit_library_folder(folder_id: str, name: str | None = None) -> dict:
    return _edit_by_id("misc_library_folders", folder_id, {"name": name})


def tool_edit_library_document(document_id: str, document_name: str | None = None) -> dict:
    return _edit_by_id("misc_library_documents", document_id, {"document_name": document_name})


def tool_edit_safety_button(
    button_id: str,
    title: str | None = None,
    description: str | None = None,
) -> dict:
    return _edit_by_id("safety_portal_buttons", button_id, {
        "title": title,
        "description": description,
    })


def tool_edit_qualification(
    qualification_id: str,
    qualification_type: str | None = None,
    date_completed: str | None = None,
    expiry_date: str | None = None,
) -> dict:
    return _edit_by_id("employee_qualifications", qualification_id, {
        "qualification_type": qualification_type,
        "date_completed": date_completed,
        "expiry_date": expiry_date,
    })


# ── OpenAI tool definitions ─────────────────────────────────────────────────

EXTRA_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_purchase_orders",
            "description": "Get purchase orders (PO number, status, vendor, location, amount, created by, date). Use for questions about POs, pending approvals, spending, purchases.",
            "parameters": {
                "type": "object",
                "properties": {
                    "search": {"type": "string", "description": "Keyword search across PO number, vendor, location, created_by (optional)"},
                    "status": {"type": "string", "description": "Filter by status, e.g. 'pending', 'approved' (optional)"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_vendors",
            "description": "Get vendors used in purchase orders.",
            "parameters": {
                "type": "object",
                "properties": {"search": {"type": "string", "description": "Search vendor name (optional)"}},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_users",
            "description": "Get application users (name, email, role). Use for questions about who has access, team members, personnel.",
            "parameters": {
                "type": "object",
                "properties": {"search": {"type": "string", "description": "Search by name or email (optional)"}},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_roles",
            "description": "Get user roles and what access/permissions each role has (Super Admin, Admin, Supervisor, Linked Employee User, or custom roles).",
            "parameters": {
                "type": "object",
                "properties": {"search": {"type": "string", "description": "Search by role name or description (optional)"}},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_jobs",
            "description": "Get dispatched jobs / job schedule entries (job type, assigned employee, scheduled date, status). Use for questions about job dispatch, scheduling, assigned work.",
            "parameters": {
                "type": "object",
                "properties": {"search": {"type": "string", "description": "Keyword search (optional)"}},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_library_folders",
            "description": "Get folders in the shared Document Library (e.g. safety, chemicals). Use before get_library_documents if the folder is unknown.",
            "parameters": {
                "type": "object",
                "properties": {"search": {"type": "string", "description": "Search by folder name (optional)"}},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_library_documents",
            "description": "Get PDF documents from the shared Document Library, optionally within a specific folder.",
            "parameters": {
                "type": "object",
                "properties": {
                    "folder_id": {"type": "string", "description": "Filter by folder _id (optional)"},
                    "search": {"type": "string", "description": "Search by document name (optional)"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_audit_logs",
            "description": "Get recent audit log entries (who did what, when). Use for questions about recent activity, changes, or who edited/created something.",
            "parameters": {
                "type": "object",
                "properties": {
                    "search": {"type": "string", "description": "Keyword search across user name, summary, action (optional)"},
                    "entity_type": {"type": "string", "description": "Filter by entity type, e.g. 'equipment', 'purchase_order', 'user' (optional)"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_bbs_entries",
            "description": "Get BBS Good Catch / hazard identification entries. Use for questions about safety observations, hazard reports, or BBS submissions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "description": "Filter by status: Pending, Assigned, Performed, Completed, or Archived (optional)"},
                    "search": {"type": "string", "description": "Keyword search across token, location, observer/submitter name (optional)"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_bbs_summary",
            "description": "Get overall BBS Good Catch counts by status (Pending, Assigned, Performed, Completed, Archived).",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_safety_buttons",
            "description": "Get Safety Portal quick-access buttons/materials.",
            "parameters": {
                "type": "object",
                "properties": {"search": {"type": "string", "description": "Search by title (optional)"}},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_equipment",
            "description": (
                "Edit an existing equipment's name and/or description. This is the ONLY "
                "write/edit tool available — it can NEVER delete equipment or anything else. "
                "It also cannot change any field besides name/description. Before calling this, "
                "make sure you already know which equipment the user means (e.g. from an earlier "
                "get_equipment_detail/search_equipment/list_equipment call in this conversation, "
                "or because the user just gave the equipment id/name). If the user asks to delete "
                "something, do NOT call this tool — refuse and explain the assistant cannot delete data."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "equipment_id": {"type": "string", "description": "MongoDB _id string or equipment name of the equipment to edit"},
                    "name": {"type": "string", "description": "New name for the equipment (optional — only include if the user wants the name changed)"},
                    "description": {"type": "string", "description": "New description for the equipment (optional — only include if the user wants the description changed)"}
                },
                "required": ["equipment_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_certification",
            "description": "Edit an existing certification's name, dates, or certifying body. Cannot delete a certification.",
            "parameters": {
                "type": "object",
                "properties": {
                    "certification_id": {"type": "string", "description": "MongoDB _id of the certification to edit"},
                    "certification_name": {"type": "string", "description": "New certification name (optional)"},
                    "certification_date": {"type": "string", "description": "New certification date, e.g. YYYY-MM-DD (optional)"},
                    "expiry_date": {"type": "string", "description": "New expiry date, e.g. YYYY-MM-DD (optional)"},
                    "certified_by": {"type": "string", "description": "New certifying body/person (optional)"}
                },
                "required": ["certification_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_maintenance",
            "description": "Edit an existing maintenance record's name, type, performed_by, or next due date. Cannot delete a maintenance record.",
            "parameters": {
                "type": "object",
                "properties": {
                    "maintenance_id": {"type": "string", "description": "MongoDB _id of the maintenance record to edit"},
                    "name": {"type": "string", "description": "New maintenance name (optional)"},
                    "type": {"type": "string", "description": "New maintenance type (optional)"},
                    "performed_by": {"type": "string", "description": "New performed_by value (optional)"},
                    "next_due_date": {"type": "string", "description": "New next due date, e.g. YYYY-MM-DD (optional)"}
                },
                "required": ["maintenance_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_document",
            "description": "Edit an existing equipment document's name or type. Cannot delete a document.",
            "parameters": {
                "type": "object",
                "properties": {
                    "document_id": {"type": "string", "description": "MongoDB _id of the document to edit"},
                    "document_name": {"type": "string", "description": "New document name (optional)"},
                    "document_type": {"type": "string", "description": "New document type (optional)"}
                },
                "required": ["document_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_work_order",
            "description": "Edit an existing work order's service type, location, unit, or performed_by. Cannot delete a work order.",
            "parameters": {
                "type": "object",
                "properties": {
                    "work_order_id": {"type": "string", "description": "MongoDB _id of the work order to edit"},
                    "service_type": {"type": "string", "description": "New service type (optional)"},
                    "location": {"type": "string", "description": "New location (optional)"},
                    "unit": {"type": "string", "description": "New unit (optional)"},
                    "performed_by": {"type": "string", "description": "New performed_by value (optional)"}
                },
                "required": ["work_order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_template",
            "description": "Edit an existing equipment template's name or description. Cannot delete a template.",
            "parameters": {
                "type": "object",
                "properties": {
                    "template_id": {"type": "string", "description": "MongoDB _id of the template to edit"},
                    "name": {"type": "string", "description": "New template name (optional)"},
                    "description": {"type": "string", "description": "New template description (optional)"}
                },
                "required": ["template_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_purchase_order",
            "description": "Edit an existing purchase order's vendor, location, or status. Cannot delete a purchase order.",
            "parameters": {
                "type": "object",
                "properties": {
                    "po_id": {"type": "string", "description": "MongoDB _id of the purchase order to edit"},
                    "vendor": {"type": "string", "description": "New vendor name (optional)"},
                    "location": {"type": "string", "description": "New location (optional)"},
                    "status": {"type": "string", "description": "New status (optional)"}
                },
                "required": ["po_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_vendor",
            "description": "Edit an existing vendor's name. Cannot delete a vendor.",
            "parameters": {
                "type": "object",
                "properties": {
                    "vendor_id": {"type": "string", "description": "MongoDB _id of the vendor to edit"},
                    "name": {"type": "string", "description": "New vendor name"}
                },
                "required": ["vendor_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_job",
            "description": "Edit an existing dispatched job's job_type, assigned_to, or status. Cannot delete a job.",
            "parameters": {
                "type": "object",
                "properties": {
                    "job_id": {"type": "string", "description": "MongoDB _id of the job to edit"},
                    "job_type": {"type": "string", "description": "New job type (optional)"},
                    "assigned_to": {"type": "string", "description": "New assignee (optional)"},
                    "status": {"type": "string", "description": "New status (optional)"}
                },
                "required": ["job_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_library_folder",
            "description": "Edit an existing shared document library folder's name. Cannot delete a folder.",
            "parameters": {
                "type": "object",
                "properties": {
                    "folder_id": {"type": "string", "description": "MongoDB _id of the folder to edit"},
                    "name": {"type": "string", "description": "New folder name"}
                },
                "required": ["folder_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_library_document",
            "description": "Edit an existing shared document library document's name. Cannot delete a document.",
            "parameters": {
                "type": "object",
                "properties": {
                    "document_id": {"type": "string", "description": "MongoDB _id of the document to edit"},
                    "document_name": {"type": "string", "description": "New document name"}
                },
                "required": ["document_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_safety_button",
            "description": "Edit an existing Safety Portal button's title or description. Cannot delete a safety button.",
            "parameters": {
                "type": "object",
                "properties": {
                    "button_id": {"type": "string", "description": "MongoDB _id of the safety button to edit"},
                    "title": {"type": "string", "description": "New title (optional)"},
                    "description": {"type": "string", "description": "New description (optional)"}
                },
                "required": ["button_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_qualification",
            "description": "Edit an existing employee qualification's type, completion date, or expiry date. Cannot delete a qualification record.",
            "parameters": {
                "type": "object",
                "properties": {
                    "qualification_id": {"type": "string", "description": "MongoDB _id of the qualification record to edit"},
                    "qualification_type": {"type": "string", "description": "New qualification type (optional)"},
                    "date_completed": {"type": "string", "description": "New completion date, e.g. YYYY-MM-DD (optional)"},
                    "expiry_date": {"type": "string", "description": "New expiry date, e.g. YYYY-MM-DD (optional)"}
                },
                "required": ["qualification_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_qualification_schedule",
            "description": "Get employee qualifications/certifications with expiry dates (safety training, operational credentials). Use for compliance questions about employee qualifications, not equipment certifications.",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_id": {"type": "string", "description": "Filter by employee _id (optional)"},
                    "search": {"type": "string", "description": "Search by employee name or qualification type (optional)"}
                },
                "required": []
            }
        }
    },
]

EXTRA_TOOL_MAP = {
    "get_purchase_orders":   lambda args: tool_get_purchase_orders(**args),
    "get_vendors":           lambda args: tool_get_vendors(**args),
    "get_users":             lambda args: tool_get_users(**args),
    "get_roles":             lambda args: tool_get_roles(**args),
    "get_jobs":              lambda args: tool_get_jobs(**args),
    "get_library_folders":   lambda args: tool_get_library_folders(**args),
    "get_library_documents": lambda args: tool_get_library_documents(**args),
    "get_audit_logs":        lambda args: tool_get_audit_logs(**args),
    "get_bbs_entries":       lambda args: tool_get_bbs_entries(**args),
    "get_bbs_summary":       lambda args: tool_get_bbs_summary(**args),
    "get_safety_buttons":    lambda args: tool_get_safety_buttons(**args),
    "get_qualification_schedule": lambda args: tool_get_qualification_schedule(**args),
    "edit_equipment":        lambda args: tool_edit_equipment(**args),
    "edit_certification":    lambda args: tool_edit_certification(**args),
    "edit_maintenance":      lambda args: tool_edit_maintenance(**args),
    "edit_document":         lambda args: tool_edit_document(**args),
    "edit_work_order":       lambda args: tool_edit_work_order(**args),
    "edit_template":         lambda args: tool_edit_template(**args),
    "edit_purchase_order":   lambda args: tool_edit_purchase_order(**args),
    "edit_vendor":           lambda args: tool_edit_vendor(**args),
    "edit_job":              lambda args: tool_edit_job(**args),
    "edit_library_folder":   lambda args: tool_edit_library_folder(**args),
    "edit_library_document": lambda args: tool_edit_library_document(**args),
    "edit_safety_button":    lambda args: tool_edit_safety_button(**args),
    "edit_qualification":    lambda args: tool_edit_qualification(**args),
}

# ── New route keys this module adds ────────────────────────────────────────

EXTRA_VALID_ROUTES = {
    "ROUTE_PURCHASE_ORDERS",
    "ROUTE_ROLES",
    "ROUTE_JOB_DISPATCH",
    "ROUTE_DOCUMENT_LIBRARY",
    "ROUTE_AUDIT_LOG",
    "ROUTE_BBS_DASHBOARD",
    "ROUTE_BBS_FORM",
    "ROUTE_BBS_SUBMISSIONS",
    "ROUTE_SAFETY_PORTAL",
    "ROUTE_QUALIFICATION_SCHEDULE",
    "ROUTE_MY_QUALIFICATIONS",
    # ROUTE_USERS already exists in chatbot.py's VALID_ROUTES; included here
    # too so this set is self-describing/complete if reused standalone.
    "ROUTE_VENDORS",
    "ROUTE_PURCHASE_ORDER_METADATA",
    "ROUTE_PURCHASE_ORDER_ACCESS",
    "ROUTE_PURCHASE_ORDER_METADATA",
    "ROUTE_PURCHASE_ORDER_ACCESS",
    "ROUTE_JOB_DISPATCH",
    "ROUTE_JOB_ARCHIVED",
    "ROUTE_JOB_TEMPLATES",
    "ROUTE_EMPLOYEES",
    "ROUTE_EMPLOYEE_EQUIPMENT",
    "ROUTE_EMPLOYEE_METADATA",
    "ROUTE_USERS",
    "ROUTE_EMPLOYEE_METADATA",
    "ROUTE_BBS_SETTINGS",
    "ROUTE_BBS_GUIDE",
    "ROUTE_SAFETY_METADATA",
    "ROUTE_ROLES",
    "ROUTE_SAFETY_METADATA",
    "ROUTE_THEMES",
    "ROUTE_EMAILS",
    
}

# ── Text inserted into chatbot.py's SYSTEM_PROMPT, directly after CASE E ────
# Placed immediately next to the other MANDATORY cases (not at the very end
# of the prompt) so the model treats these with the same priority as CASE A–E.
# Pure text — no crash risk; worst case the model just doesn't use the new
# routes correctly, which is no worse than before this module existed.

EXTRA_ACTION_CASES = """
Also answer questions about: purchase orders, vendors, users, roles,
job dispatch, and the shared document library (folders + PDFs).

CASE F — Purchase orders (MANDATORY, same status as CASE A-E):
  User asks about POs, purchases, spending, or pending approvals (NOT vendors).
  → Set action_item: true, action_item_redirection: "ROUTE_PURCHASE_ORDERS".

CASE F2 — Vendors (MANDATORY, same status as CASE A-E):
  User asks about vendors, vendor list, vendor contact info, or vendor documents.
  → Set action_item: true, action_item_redirection: "ROUTE_VENDORS".

CASE F3 — PO Metadata (MANDATORY, same status as CASE A-E):
  User asks about, or wants to see/view/manage, purchase order metadata,
  expense types, payment methods, or purposes used in POs.
  → ALWAYS set action_item: true, action_item_redirection: "ROUTE_PURCHASE_ORDER_METADATA",
    action_item_button_text: "View PO Metadata". This is MANDATORY — do not skip

CASE F4 — PO Access (MANDATORY, same status as CASE A-E):
  User asks about who has purchase order access/permissions, or wants to
  manage PO approval access.
  → Set action_item: true, action_item_redirection: "ROUTE_PURCHASE_ORDER_ACCESS".

CASE G — Users / personnel / roles (MANDATORY, same status as CASE A-E):
  User asks about team members, who has access, or roles/permissions.
  → Set action_item: true, action_item_redirection: "ROUTE_USERS" for user
    questions, or "ROUTE_ROLES" for role/permission questions.

CASE H — Job dispatch (MANDATORY, same status as CASE A-E):
  User asks about jobs, job schedule, dispatch, or assigned/upcoming work
  (NOT archived jobs, NOT job metadata/templates).
  → ALWAYS set action_item: true, action_item_redirection: "ROUTE_JOB_DISPATCH",
    action_item_button_text: "Go to Job Dispatch". MANDATORY — do not skip.

CASE H2 — Archived jobs (MANDATORY, same status as CASE A-E):
  User asks about archived, completed, past, or finished jobs.
  → ALWAYS set action_item: true, action_item_redirection: "ROUTE_JOB_ARCHIVED",
    action_item_button_text: "View Archived Jobs". MANDATORY — do not skip.

CASE H3 — Job metadata/templates (MANDATORY, same status as CASE A-E):
  User asks about job types, job templates, or job metadata configuration.
  → ALWAYS set action_item: true, action_item_redirection: "ROUTE_JOB_TEMPLATES",
    action_item_button_text: "View Job Metadata". MANDATORY — do not skip.

CASE N — Employees (MANDATORY, same status as CASE A-E):
  User asks about employees, employee directory, employee list, or a
  specific employee's profile.
  → ALWAYS set action_item: true, action_item_redirection: "ROUTE_EMPLOYEES",
    action_item_button_text: "View Employees". MANDATORY — do not skip.

CASE O — Employee Equipment (MANDATORY, same status as CASE A-E):
  User asks about equipment assigned to employees, or employee-specific
  equipment assignments.
  → ALWAYS set action_item: true, action_item_redirection: "ROUTE_EMPLOYEE_EQUIPMENT",
    action_item_button_text: "View Employee Equipment". MANDATORY — do not skip.

CASE P — Employee Qualification Schedule (MANDATORY, same status as CASE A-E):
  User (an admin/supervisor) asks about the qualification schedule for
  employees, training expiry across the team, or compliance overview
  (NOT their own personal qualifications — that is a separate case elsewhere).
  → ALWAYS set action_item: true, action_item_redirection: "ROUTE_QUALIFICATION_SCHEDULE",
    action_item_button_text: "View Qualification Schedule". MANDATORY — do not skip.

CASE Q — Employee Metadata (MANDATORY, same status as CASE A-E):
  User asks about employee metadata, job titles, service lines, or
  employee-related configuration/categories.
  → ALWAYS set action_item: true, action_item_redirection: "ROUTE_EMPLOYEE_METADATA",
    action_item_button_text: "View Employee Metadata". MANDATORY — do not skip.

CASE R — BBS Settings (MANDATORY, same status as CASE A-E):
  User asks about BBS settings, hazard category configuration, or BBS
  program setup.
  → ALWAYS set action_item: true, action_item_redirection: "ROUTE_BBS_SETTINGS",
    action_item_button_text: "Open BBS Settings". MANDATORY — do not skip.

CASE S — BBS Guide (MANDATORY, same status as CASE A-E):
  User asks how BBS Good Catch works, wants help/instructions, or asks
  about the BBS guide.
  → ALWAYS set action_item: true, action_item_redirection: "ROUTE_BBS_GUIDE",
    action_item_button_text: "View BBS Guide". MANDATORY — do not skip.

CASE T — Safety Metadata (MANDATORY, same status as CASE A-E):
  User asks about safety metadata, safety categories, or safety portal
  configuration (not the safety buttons/materials themselves).
  → ALWAYS set action_item: true, action_item_redirection: "ROUTE_SAFETY_METADATA",
    action_item_button_text: "View Safety Metadata". MANDATORY — do not skip.

CASE I — Document library (MANDATORY, same status as CASE A-E):
  User asks about the shared document library, folders, or company-wide
  PDFs (not equipment-specific documents).
  → Set action_item: true, action_item_redirection: "ROUTE_DOCUMENT_LIBRARY".

CASE J — Audit log (MANDATORY, same status as CASE A-E):
  User asks about recent activity, changes, or who did/edited something.
  → Set action_item: true, action_item_redirection: "ROUTE_AUDIT_LOG".

CASE K — BBS Good Catch / hazard reports (MANDATORY, same status as CASE A-E):
  User asks about safety observations, hazard identification, or BBS
  submissions/entries.
  → Set action_item: true, action_item_redirection: "ROUTE_BBS_DASHBOARD"
    (or "ROUTE_BBS_FORM" if the user wants to submit a new one, or
    "ROUTE_BBS_SUBMISSIONS" if they want to review/manage all submissions).

CASE L — Safety Portal (MANDATORY, same status as CASE A-E):
  User asks about the Safety Portal or safety quick-access materials.
  → Set action_item: true, action_item_redirection: "ROUTE_SAFETY_PORTAL".

CASE U — Theme & Branding (MANDATORY, same status as CASE A-E):
  User asks about theme, branding, logo, app colors, or customizing the
  app's appearance.
  → ALWAYS set action_item: true, action_item_redirection: "ROUTE_THEMES",
    action_item_button_text: "Open Theme & Branding". MANDATORY — do not skip.

CASE V — Emails (MANDATORY, same status as CASE A-E):
  User asks about email settings, email notifications, or email templates
  configuration.
  → ALWAYS set action_item: true, action_item_redirection: "ROUTE_EMAILS",
    action_item_button_text: "Open Emails". MANDATORY — do not skip.

CASE M — Employee qualifications / compliance (MANDATORY, same status as CASE A-E):
  User asks about employee qualifications, training expiry, or compliance
  credentials (not equipment certifications — that is CASE E).
  → Set action_item: true, action_item_redirection: "ROUTE_QUALIFICATION_SCHEDULE"
    (or "ROUTE_MY_QUALIFICATIONS" if the user is asking about their own).
"""

# ── Text appended to the very end of chatbot.py's SYSTEM_PROMPT ────────────
# Route key list, trigger reference, app knowledge, how-to steps — fine to
# live at the end since these are reference material, not action triggers.

EXTRA_SYSTEM_PROMPT = """

=============================================================
IMPORTANT OVERRIDE — READ BEFORE THE "GENERAL RULES" ABOVE
=============================================================
The base rule above ("Do not create, update, or delete records directly")
is now PARTIALLY superseded: edit_* tools (edit_equipment, edit_certification,
edit_maintenance, edit_document, edit_work_order, edit_template,
edit_purchase_order, edit_vendor, edit_job, edit_library_folder,
edit_library_document, edit_safety_button, edit_qualification) now exist and
MAY be called directly, WITHOUT asking for extra confirmation, when the user
clearly asks to change/update/edit/rename/correct a specific field on a
specific record (see CASE W below).
- Creating new records is still NOT supported by any tool — for "add X"
  requests, keep explaining steps + navigation actions as before.
- Deleting is NEVER supported by any tool, under any framing — see CASE X
  below, which is an absolute hard rule with no exceptions.

CASE W — Edit requests (MANDATORY): equipment, certifications, maintenance,
  documents, work orders, templates, purchase orders, vendors, jobs,
  document library folders/documents, safety buttons, and employee
  qualifications can all be EDITED (never deleted, never any other field
  than the ones each edit_* tool exposes).
  User asks to change, edit, update, rename, correct, or rewrite a specific
  field on one of these records (e.g. "change this equipment's description
  to X", "update the certification's expiry date", "fix the vendor name").
  → First make sure you know WHICH record is meant (from an earlier get_*/
    search_*/list_* call in this conversation, or because the user just
    gave its id/name directly). If it's not clear which record, ask the
    user to clarify instead of guessing — never guess an _id.
  → Call the matching edit_* tool (edit_equipment, edit_certification,
    edit_maintenance, edit_document, edit_work_order, edit_template,
    edit_purchase_order, edit_vendor, edit_job, edit_library_folder,
    edit_library_document, edit_safety_button, edit_qualification) with
    ONLY the field(s) the user asked to change.
  → After a successful equipment edit specifically, set action_item: true,
    action_item_redirection: "ROUTE_EQUIPMENT_DETAIL",
    action_item_equipment_id: the equipment's _id, so the user can view the
    updated record. For other record types, just confirm the change in
    plain text (no equipment_id to attach).
  → NOT editable by any tool, under any framing: users and roles (access/
    permission changes are out of scope for safety reasons — tell the user
    this must be done directly in the app by an admin), and audit logs
    (they are an immutable history and must never be edited).

CASE X — Delete requests (HARD BLOCK, no exceptions):
  User asks to delete, remove, erase, or permanently get rid of ANY record
  of ANY kind — equipment, certifications, maintenance, documents, work
  orders, templates, purchase orders, vendors, jobs, library items, safety
  buttons, qualifications, users, roles, sessions, anything.
  → NEVER call any tool for this, and never call an edit_* tool as a
    workaround (e.g. never "clear" a field to fake a delete). There is no
    delete tool anywhere in this system.
  → Reply that the assistant cannot delete data, and that the user needs to
    delete it themselves directly in the app.
  → Set action_item to true with the relevant list/detail ROUTE_KEY only if
    it helps the user get to the record to delete it manually themselves;
    otherwise leave action fields null.

=============================================================
EXTRA MODULES (Purchase Orders, Personnel, Job Dispatch, Document Library)
=============================================================

Additional ALLOWED ROUTE KEYS (use EXACTLY these strings):
ROUTE_PURCHASE_ORDERS    → Purchase Orders page
ROUTE_VENDORS            → Vendors list page
ROUTE_PURCHASE_ORDER_METADATA → PO metadata (expense types, payment methods, purposes)
ROUTE_PURCHASE_ORDER_ACCESS   → PO access/permissions management page
ROUTE_JOB_DISPATCH       → Job Dispatch / scheduling calendar page
ROUTE_JOB_ARCHIVED       → Archived jobs page
ROUTE_JOB_TEMPLATES      → Job metadata/templates page
ROUTE_EMPLOYEES          → Employee directory/list page
ROUTE_EMPLOYEE_EQUIPMENT → Equipment assigned to employees
ROUTE_EMPLOYEE_METADATA  → Employee metadata (job titles, service lines)
ROUTE_ROLES              → Roles & permissions page
ROUTE_JOB_DISPATCH       → Job Dispatch / scheduling calendar page
ROUTE_BBS_SETTINGS       → BBS Good Catch settings/configuration page
ROUTE_BBS_GUIDE          → BBS Good Catch guide/help page
ROUTE_SAFETY_METADATA    → Safety Portal metadata/configuration page
ROUTE_DOCUMENT_LIBRARY   → Shared Document Library (folders + PDFs)
ROUTE_AUDIT_LOG          → Audit log page
ROUTE_BBS_DASHBOARD      → BBS Good Catch dashboard (assigned work, KPIs)
ROUTE_BBS_FORM           → BBS Good Catch submission form (report a hazard)
ROUTE_BBS_SUBMISSIONS    → BBS Good Catch all submissions (admin review)
ROUTE_SAFETY_PORTAL      → Safety Portal quick-access page
ROUTE_QUALIFICATION_SCHEDULE → Employee qualification schedule (compliance)
ROUTE_MY_QUALIFICATIONS  → Current user's own qualifications
ROUTE_THEMES              → Theme & Branding configuration page
ROUTE_EMAILS              → Email settings/templates page
(ROUTE_USERS already exists — now also used for personnel questions.)

Additional Trigger → Route quick reference:
  "purchase order / PO / spending / pending approval" → ROUTE_PURCHASE_ORDERS, button: "View Purchase Orders"
  "vendor / vendor list / vendor contact"   → ROUTE_VENDORS,          button: "View Vendors"
  "PO metadata / expense type / payment method / purpose" → ROUTE_PURCHASE_ORDER_METADATA, button: "View PO Metadata"
  "PO access / who can approve / PO permissions" → ROUTE_PURCHASE_ORDER_ACCESS, button: "View PO Access"
  "job / dispatch / assigned / upcoming work" → ROUTE_JOB_DISPATCH,  button: "Go to Job Dispatch"
  "archived job / completed job / past job"   → ROUTE_JOB_ARCHIVED,  button: "View Archived Jobs"
  "job type / job template / job metadata"    → ROUTE_JOB_TEMPLATES, button: "View Job Metadata"
  "employee / personnel / staff directory"   → ROUTE_EMPLOYEES,          button: "View Employees"
  "employee equipment / assigned equipment"  → ROUTE_EMPLOYEE_EQUIPMENT, button: "View Employee Equipment"
  "employee metadata / job title / service line" → ROUTE_EMPLOYEE_METADATA, button: "View Employee Metadata"
  "BBS settings / hazard category config"   → ROUTE_BBS_SETTINGS,    button: "Open BBS Settings"
  "BBS guide / how BBS works / BBS help"    → ROUTE_BBS_GUIDE,       button: "View BBS Guide"
  "safety metadata / safety category config" → ROUTE_SAFETY_METADATA, button: "View Safety Metadata"
  "user / team member / who has access"     → ROUTE_USERS,           button: "View Users"
  "role / permission / access level"        → ROUTE_ROLES,           button: "View Roles"
  "job / job dispatch / schedule / assign"  → ROUTE_JOB_DISPATCH,    button: "Go to Job Dispatch"
  "document library / folder / shared docs" → ROUTE_DOCUMENT_LIBRARY, button: "Open Document Library"
  "audit / activity / who changed / history" → ROUTE_AUDIT_LOG,      button: "View Audit Log"
  "hazard / safety observation / BBS / good catch" → ROUTE_BBS_DASHBOARD, button: "Open BBS Dashboard"
  "report a hazard / submit BBS / good catch form" → ROUTE_BBS_FORM, button: "Submit BBS Form"
  "theme / branding / logo / app colors"    → ROUTE_THEMES,          button: "Open Theme & Branding"
  "email settings / email templates / notifications config" → ROUTE_EMAILS, button: "Open Emails"
  "safety portal / safety materials"        → ROUTE_SAFETY_PORTAL,   button: "Open Safety Portal"
  "employee qualification / training expiry / compliance credential" → ROUTE_QUALIFICATION_SCHEDULE, button: "View Qualification Schedule"

Additional T29 APP KNOWLEDGE:
- Purchase Orders: PO number, status (e.g. Pending Supervisor Approval),
  vendor, location, amount, created by, date. Vendors, expense types,
  payment methods, purposes, and locations are managed as supporting lists.
- User Management (Personnel): list of app users with name, email, and
  assigned role. Superadmin can add users.
- Roles: defines custom roles and module access (e.g. Super Admin — full
  platform access; Admin — equipment/personnel/operations; Supervisor —
  equipment/employee directory; Linked Employee User — self-service for a
  single employee record).
- Job Dispatch: calendar-based scheduling of jobs, filterable by job type,
  with Month/Week/Day views. Add Job button creates a new dispatch entry.
- Document Library (shared, sidebar): organized in FOLDERS first. To add a
  document: create/open a folder, then upload the PDF inside that folder.
  Separate from equipment-specific documents.
  - BBS Good Catch (safety hazard reporting program): includes a Dashboard
  (assigned work, KPIs), a Form (submit/report a hazard observation), a
  Submissions page (admin review of all submissions), Settings (configure
  hazard categories), and a Guide (how the BBS program works).
- Safety Portal: quick-access page for safety materials/buttons for
  employees, plus a separate Safety Metadata page for admins to configure
  safety categories/types.
- Theme & Branding: superadmin-only page to customize app logo, colors,
  and appearance.
- Emails: superadmin-only page to configure email notification settings
  and templates.

Additional how-to steps:
How to create a purchase order: Purchase Orders page → New Purchase Order →
  fill vendor, location, amount, purpose, payment method → Save (goes to
  Pending Supervisor Approval).
How to add a user: User Management page → Add User → fill name, email,
  assign a role → Save.
How to add a role: Roles page → Add new role → define name, description,
  and module access → Save.
How to dispatch a job: Job Dispatch page → Add Job → fill job type,
  assigned employee, date/time → Save.
How to add a document to the shared library: Document Library → create or
  open a folder first → then upload the PDF into that folder.
How to submit a BBS Good Catch (hazard report): BBS Good Catch → BBS Form →
  describe the observation(s) → Submit. It starts as Pending until assigned.
How to view your compliance/qualification status: Compliance → My
  Qualifications (or Qualification Schedule for admins) shows expiry dates
  for training and credentials.

Reminder: if a tool from this section returns an empty list, tell the user
plainly that no records were found yet — do not invent data.
"""
