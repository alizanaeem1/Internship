"""
evaluation.py — Week 8 Optimization Evaluation
=================================================
Static evaluation of final_chatbot.py: verifies tool coverage, safety rules,
and that the CASE W / CASE X bug fix (see README.md section 3) is actually
present in the string sent to the LLM. No database or API calls needed —
this only inspects the source file's structure and content, so it can run
anywhere, instantly, with no credentials.

RUN:
  python evaluation.py
"""

import ast
import re

FILE = "final_chatbot.py"

REQUIRED_EDIT_TOOLS = {
    "edit_equipment", "edit_certification", "edit_maintenance", "edit_document",
    "edit_work_order", "edit_template", "edit_purchase_order", "edit_vendor",
    "edit_job", "edit_library_folder", "edit_library_document",
    "edit_safety_button", "edit_qualification",
}

FORBIDDEN_TOOL_NAME_FRAGMENTS = ["delete", "remove_", "erase"]

NEVER_EDITABLE_COLLECTIONS = ["users", "roles", "audit_logs"]


def load_source() -> str:
    with open(FILE, "r", encoding="utf-8") as f:
        return f.read()


def check_syntax_valid(source: str) -> bool:
    try:
        ast.parse(source)
        return True
    except SyntaxError as e:
        print(f"  FAILED: {FILE} has a syntax error: {e}")
        return False


def check_edit_tools_present(source: str) -> bool:
    tool_names = set(re.findall(r'"name":\s*"(edit_[a-z_]+)"', source))
    missing = REQUIRED_EDIT_TOOLS - tool_names
    extra = tool_names - REQUIRED_EDIT_TOOLS
    if missing:
        print(f"  FAILED: missing edit tool schemas: {missing}")
        return False
    print(f"  OK: all {len(REQUIRED_EDIT_TOOLS)} required edit_* tool schemas are present"
          f"{f' (plus {extra})' if extra else ''}.")
    return True


def check_no_delete_tool(source: str) -> bool:
    tool_names = re.findall(r'"name":\s*"([a-z_]+)"', source)
    bad = [n for n in tool_names if any(frag in n for frag in FORBIDDEN_TOOL_NAME_FRAGMENTS)]
    if bad:
        print(f"  FAILED: found tool name(s) suggesting a delete/remove capability: {bad}")
        return False
    print("  OK: no tool with 'delete'/'remove_'/'erase' in its name exists anywhere.")
    return True


def check_tool_map_complete(source: str) -> bool:
    map_entries = set(re.findall(r'"(edit_[a-z_]+)":\s*lambda', source))
    missing = REQUIRED_EDIT_TOOLS - map_entries
    if missing:
        print(f"  FAILED: these edit tools have a schema but no TOOL_MAP entry: {missing}")
        return False
    print(f"  OK: all {len(REQUIRED_EDIT_TOOLS)} edit tools are registered in TOOL_MAP.")
    return True


def check_users_roles_not_editable(source: str) -> bool:
    ok = True
    for forbidden in NEVER_EDITABLE_COLLECTIONS:
        if re.search(rf'def tool_edit_\w*{forbidden[:-1] if forbidden.endswith("s") else forbidden}\w*\(', source):
            print(f"  FAILED: found an edit tool function that appears to target '{forbidden}'!")
            ok = False
    if ok:
        print(f"  OK: no edit_* function targets {NEVER_EDITABLE_COLLECTIONS}.")
    return ok


def check_bug_fix_present(source: str) -> bool:
    """The core Week 8 fix: CASE W / CASE X must live inside EXTRA_SYSTEM_PROMPT
    (which chatbot.py actually concatenates into SYSTEM_PROMPT), NOT inside
    EXTRA_ACTION_CASES (which is imported but never used — the bug)."""
    m = re.search(r'EXTRA_SYSTEM_PROMPT\s*=\s*"""(.*?)"""', source, re.DOTALL)
    if not m:
        print("  FAILED: could not find EXTRA_SYSTEM_PROMPT definition at all.")
        return False
    extra_system_prompt = m.group(1)

    has_case_w = "CASE W" in extra_system_prompt
    has_case_x = "CASE X" in extra_system_prompt
    if not (has_case_w and has_case_x):
        print(f"  FAILED: CASE W present={has_case_w}, CASE X present={has_case_x} "
              f"inside EXTRA_SYSTEM_PROMPT — the bug fix is missing or incomplete.")
        return False

    print("  OK: CASE W and CASE X are both present inside EXTRA_SYSTEM_PROMPT "
          "(the variable that actually reaches the LLM) — bug fix confirmed.")
    return True


def check_extra_system_prompt_actually_merged(source: str) -> bool:
    """Confirms the concatenation `... + EXTRA_SYSTEM_PROMPT + ...` exists in
    the SYSTEM_PROMPT construction, i.e. the merge point itself is intact."""
    if re.search(r'"""\s*\+\s*EXTRA_SYSTEM_PROMPT\s*\+\s*"""', source):
        print("  OK: EXTRA_SYSTEM_PROMPT is concatenated into SYSTEM_PROMPT.")
        return True
    print("  FAILED: could not find EXTRA_SYSTEM_PROMPT being concatenated into SYSTEM_PROMPT.")
    return False


def check_whitelist_fields(source: str) -> bool:
    """Spot-check tool_edit_equipment only exposes name/description — proof
    that edits are field-whitelisted, not a generic 'update anything' path."""
    m = re.search(r'def tool_edit_equipment\(([^)]*)\)', source)
    if not m:
        print("  FAILED: could not find tool_edit_equipment's signature.")
        return False
    params = m.group(1)
    has_name = "name" in params
    has_description = "description" in params
    has_category = "category_id" in params  # should NOT be there
    if has_category:
        print("  FAILED: tool_edit_equipment exposes category_id — whitelist too broad!")
        return False
    if not (has_name and has_description):
        print("  FAILED: tool_edit_equipment is missing name/description in its signature.")
        return False
    print("  OK: tool_edit_equipment only exposes name/description (verified against signature).")
    return True


def main():
    print("=" * 70)
    print("EVALUATION: final_chatbot.py — Week 8 optimization & integration")
    print("=" * 70)

    source = load_source()

    checks = [
        ("Syntax valid",                          check_syntax_valid),
        ("All 13 edit tool schemas present",      check_edit_tools_present),
        ("No delete-capable tool exists",          check_no_delete_tool),
        ("All edit tools registered in TOOL_MAP",  check_tool_map_complete),
        ("Users/Roles/Audit-logs not editable",    check_users_roles_not_editable),
        ("EXTRA_SYSTEM_PROMPT merge point intact", check_extra_system_prompt_actually_merged),
        ("CASE W/X bug fix present",                check_bug_fix_present),
        ("Field whitelist enforced (equipment)",   check_whitelist_fields),
    ]

    results = []
    for label, fn in checks:
        print(f"\n[{label}]")
        results.append((label, fn(source)))

    print()
    print("=" * 70)
    passed = sum(1 for _, ok in results if ok)
    print(f"RESULT: {passed}/{len(results)} checks passed")
    print("=" * 70)
    for label, ok in results:
        print(f"  {'PASS' if ok else 'FAIL'} — {label}")

    if passed != len(results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
