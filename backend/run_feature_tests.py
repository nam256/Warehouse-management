#!/usr/bin/env python
"""45 test cases — 15 chức năng × 3 trường hợp. Kết quả → test_results.json"""
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:8000/api/v1"
RESULTS: list[dict] = []


def record(tc_id: str, feature: str, name: str, expect: str, ok: bool, detail: str = ""):
    RESULTS.append({"id": tc_id, "feature": feature, "name": name, "expect": expect, "pass": ok, "detail": detail})
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {tc_id} {name}" + (f" ({detail})" if detail else ""))


def post_form(path: str, data: dict) -> tuple[int, dict]:
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(
        BASE + path, data=body, method="POST", headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")


def req(method: str, path: str, token: str | None = None, data: dict | None = None, raw: bool = False):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = None
    if data is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(data).encode()
    r = urllib.request.Request(BASE + path, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(r, timeout=15) as resp:
            content = resp.read()
            if raw:
                return resp.status, content
            ct = resp.headers.get("Content-Type", "")
            if "json" in ct:
                return resp.status, json.loads(content)
            return resp.status, content.decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        try:
            payload = json.loads(e.read().decode() or "{}")
        except json.JSONDecodeError:
            payload = {"detail": e.reason}
        return e.code, payload


def token(user: str, pwd: str) -> str:
    code, data = post_form("/auth/login", {"username": user, "password": pwd})
    if code != 200:
        raise RuntimeError(f"Login failed {user}: {code}")
    return data["access_token"]


def main() -> int:
    print("=== Feature tests (45 cases) ===\n")

    # Shared setup
    tok_kho = token("thu_kho", "kho123")
    tok_kt = token("ky_thuat", "kt123")
    tok_ql = token("ql_nm", "ql123")
    tok_lab = token("lab", "lab123")
    tok_attp = token("attp", "attp123")
    tok_admin = token("admin", "admin123")
    mats = req("GET", "/materials", tok_kho)[1]
    nvl = next(m for m in mats if m["code"] == "NVL-QUE")
    tp = next(m for m in mats if m["code"] == "TP-TCA")

    F = "Dang nhap"
    code, _ = post_form("/auth/login", {"username": "admin", "password": "admin123"})
    record("AUTH-01", F, "Dang nhap dung", "200", code == 200)
    code, _ = post_form("/auth/login", {"username": "admin", "password": "sai"})
    record("AUTH-02", F, "Sai mat khau", "401", code == 401)
    code, me = req("GET", "/auth/me", tok_kho)
    record("AUTH-03", F, "Token hop le", "role thu_kho", code == 200 and me.get("role") == "thu_kho")

    F = "Dashboard"
    code, d = req("GET", "/dashboard/summary", tok_kho)
    record("DASH-01", F, "Tai dashboard", "200", code == 200 and "material_count" in d)
    code, _ = req("GET", "/dashboard/summary", None)
    record("DASH-02", F, "Khong token", "401", code == 401)
    code, d2 = req("GET", "/dashboard/summary", tok_kt)
    record("DASH-03", F, "Ky thuat xem", "orders_running", code == 200 and "orders_running" in d2)

    F = "Ton kho"
    code, inv = req("GET", "/stock/inventory", tok_kho)
    record("INV-01", F, "Danh sach ton", "array", code == 200 and isinstance(inv, list))
    code, inv2 = req("GET", "/stock/inventory", tok_kho)
    record("INV-02", F, "Co canh bao ton thap", "low_stock field", code == 200 and inv2 and "low_stock" in inv2[0])
    code, b = req("GET", "/stock/batches?fifo=true", tok_kho)
    record("INV-03", F, "FIFO sap xep", "200", code == 200)

    F = "Nhap kho"
    code, batch_ok = req("POST", "/stock/receipts", tok_kho, {"material_id": nvl["id"], "quantity": 40, "ccp1_c14": 13.5, "warehouse_id": 1})
    record("STIN-01", F, "Nhap CCP1 pass", "pass", code == 201 and batch_ok.get("ccp1_status") == "pass")
    code, batch_fail = req("POST", "/stock/receipts", tok_kho, {"material_id": nvl["id"], "quantity": 5, "ccp1_c14": 12.0, "warehouse_id": 1})
    record("STIN-02", F, "Nhap CCP1 fail", "fail", code == 201 and batch_fail.get("ccp1_status") == "fail")
    code, _ = req("POST", "/stock/receipts", tok_lab, {"material_id": nvl["id"], "quantity": 1, "warehouse_id": 1})
    record("STIN-03", F, "Lab khong nhap kho", "403", code == 403)

    bid_ok, bid_fail = batch_ok["id"], batch_fail["id"]

    F = "Xuat kho"
    code, _ = req("POST", "/stock/issues", tok_kho, {"batch_id": bid_ok, "quantity": 3})
    record("STOUT-01", F, "Xuat lo pass", "201", code == 201)
    code, _ = req("POST", "/stock/issues", tok_kho, {"batch_id": bid_fail, "quantity": 1})
    record("STOUT-02", F, "Chan xuat lo fail", "400", code == 400)
    code, _ = req("POST", "/stock/issues", tok_kho, {"batch_id": bid_ok, "quantity": 99999})
    record("STOUT-03", F, "Chan vuot ton", "400", code == 400)

    F = "San xuat"
    code, order = req("POST", "/production/orders", tok_kt, {"product_material_id": tp["id"], "planned_qty": 20})
    oid = order["id"]
    record("PROD-01", F, "Tao me SX", "draft", code == 201 and order.get("status") == "draft")
    code, _ = req("POST", f"/production/orders/{oid}/start", tok_kt, {"materials": [{"batch_id": bid_ok, "quantity": 5}]})
    record("PROD-02", F, "Chan start chua duyet", "400", code == 400)
    req("POST", f"/production/orders/{oid}/approve", tok_ql, {})
    code, started = req("POST", f"/production/orders/{oid}/start", tok_kt, {"materials": [{"batch_id": bid_ok, "quantity": 5}]})
    req("POST", f"/production/orders/{oid}/operations", tok_kt, {"step": "chung_cat", "t_top": 108, "t_ca_percent": 99.5})
    code, done = req("POST", f"/production/orders/{oid}/complete", tok_kt, {"actual_qty": 4})
    record("PROD-03", F, "Duyet+SX+hoan thanh", "lo TP", code == 200 and done.get("output_batch_no"))
    tp_batch = done.get("output_batch_no", "")

    F = "Lab"
    code, t1 = req("POST", "/lab/tests", tok_lab, {"batch_id": bid_ok, "c14": 13.8, "test_type": "GC"})
    record("LAB-01", F, "GC CCP1 pass", "pass", code == 201 and t1.get("result_status") == "pass")
    code, t2 = req("POST", "/lab/tests", tok_lab, {"batch_id": bid_fail, "c14": 11.0, "test_type": "GC"})
    record("LAB-02", F, "GC CCP1 fail", "fail", code == 201 and t2.get("result_status") == "fail")
    code, _ = req("POST", "/lab/tests", tok_kt, {"batch_id": bid_ok, "c14": 13.5})
    record("LAB-03", F, "Ky thuat khong nhap lab", "403", code == 403)

    F = "Truy xuat"
    if tp_batch:
        code, tr = req("GET", f"/reports/trace/{tp_batch}", tok_kt)
        record("TRACE-01", F, "Truy xuat lo TP", "co me SX", code == 200 and len(tr.get("production_orders", [])) >= 1)
    else:
        record("TRACE-01", F, "Truy xuat lo TP", "co me SX", False, "khong co lo TP")
    code, _ = req("GET", "/reports/trace/LO-XXX", tok_kt)
    record("TRACE-02", F, "Lo khong ton tai", "404", code == 404)
    code, _ = req("GET", f"/reports/trace/{batch_ok['batch_no']}", tok_kt)
    record("TRACE-03", F, "Truy xuat lo NVL", "200", code == 200)

    F = "YCMH"
    code, _ = req("POST", "/stock/purchase-requests", tok_kho, {"material_id": nvl["id"], "requested_qty": 50, "reason": "test"})
    record("YCMH-01", F, "Tao YCMH", "201", code == 201)
    code, prs = req("GET", "/stock/purchase-requests", tok_kho)
    record("YCMH-02", F, "List YCMH", ">=1", code == 200 and len(prs) >= 1)
    code, _ = req("POST", "/stock/purchase-requests", tok_lab, {"material_id": nvl["id"], "requested_qty": 1})
    record("YCMH-03", F, "Lab khong tao YCMH", "403", code == 403)

    F = "CCP / HACCP"
    code, h = req("GET", "/reports/haccp-monitor?days=14", tok_lab)
    record("CCP-01", F, "Monitor 14 ngay", "ccp1_records", code == 200 and "ccp1_records" in h)
    code, s = req("GET", "/reports/ccp-summary", tok_kho)
    record("CCP-02", F, "Tong hop CCP", "200", code == 200 and "ccp2_fail" in s)
    code, pdf = req("GET", "/reports/haccp-monitor/export?days=14", tok_lab, raw=True)
    record("CCP-03", F, "Export PDF CCP", "PDF", code == 200 and pdf[:4] == b"%PDF")

    F = "Audit"
    code, logs = req("GET", "/reports/audit?limit=5", tok_attp)
    record(
        "AUDIT-01",
        F,
        "ATTP xem audit",
        "200",
        code == 200 and isinstance(logs, dict) and isinstance(logs.get("items"), list),
    )
    code, _ = req("GET", "/reports/audit", tok_kho)
    record("AUDIT-02", F, "Thu kho bi chan", "403", code == 403)
    code, page = req("GET", "/reports/audit?entity=stock_batch&page=1&page_size=10", tok_admin)
    record(
        "AUDIT-03",
        F,
        "Loc theo entity",
        "200",
        code == 200 and isinstance(page, dict) and "total" in page,
    )

    F = "Bao cao Export"
    code, csv = req("GET", "/reports/inventory/export", tok_kho, raw=True)
    record("RPT-01", F, "Export CSV", "CSV bytes", code == 200 and len(csv) > 10)
    code, pdf2 = req("GET", "/reports/inventory/export/pdf", tok_kho, raw=True)
    record("RPT-02", F, "Export PDF ton", "PDF", code == 200 and pdf2[:4] == b"%PDF")
    code, pdf3 = req("GET", f"/reports/receipt/{bid_ok}/pdf", tok_kho, raw=True)
    record("RPT-03", F, "PDF phieu nhap", "PDF", code == 200 and pdf3[:4] == b"%PDF")

    F = "Can doi & Mixing"
    code, bal = req("GET", f"/production/orders/{oid}/balance", tok_kt)
    record("BAL-01", F, "Material balance", "input>0", code == 200 and bal.get("input_total", 0) > 0)
    code, _ = req("POST", "/production/mixing-reports", tok_kt, {"order_id": oid, "mixed_qty": 4, "formula": "A"})
    record("BAL-02", F, "Mixing report", "201", code == 201)
    code, _ = req("GET", f"/reports/balance/{oid}/pdf", tok_kt, raw=True)
    record("BAL-03", F, "PDF balance", "PDF", code == 200 and _[:4] == b"%PDF")

    F = "Corrective action"
    code, _ = req(
        "POST",
        "/quality/corrective-actions",
        tok_attp,
        {"entity_type": "stock_batch", "entity_id": bid_fail, "reason": "CCP1 không đạt"},
    )
    record("CA-01", F, "Ghi CA", "201", code == 201)
    code, cas = req("GET", "/quality/corrective-actions", tok_attp)
    record("CA-02", F, "List CA", ">=1", code == 200 and len(cas) >= 1)
    code, _ = req("POST", "/quality/corrective-actions", tok_kho, {"entity_type": "x", "entity_id": 1, "reason": "x"})
    record("CA-03", F, "Thu kho bi chan", "403", code == 403)

    F = "Master data"
    code, _ = req(
        "POST",
        "/materials",
        tok_admin,
        {"code": "VT-TEST-A", "name": "Vật tư kiểm thử A", "type": "NVL", "unit": "kg"},
    )
    record("MAT-01", F, "Admin tao VT", "201", code == 201)
    code, _ = req(
        "POST",
        "/materials",
        tok_kho,
        {"code": "VT-TEST-B", "name": "Vật tư kiểm thử B", "type": "NVL", "unit": "kg"},
    )
    record("MAT-02", F, "Thu kho tao VT", "201", code == 201)
    code, _ = req("POST", "/materials", tok_kt, {"code": "VT-TEST-C", "name": "Vật tư kiểm thử C", "type": "NVL"})
    record("MAT-03", F, "Ky thuat bi chan", "403", code == 403)

    passed = sum(1 for r in RESULTS if r["pass"])
    total = len(RESULTS)
    print(f"\n=== {passed}/{total} PASS ===")
    out = {"passed": passed, "total": total, "results": RESULTS}
    with open("test_results.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    with open("../test_results.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
