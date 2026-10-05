import json
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:8001/api/v1"


def post_form(path, data):
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(
        BASE + path,
        data=body,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return json.loads(urllib.request.urlopen(req).read())


def post_json(path, data, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(BASE + path, data=json.dumps(data).encode(), method="POST", headers=headers)
    return json.loads(urllib.request.urlopen(req).read())


def get(path, token):
    req = urllib.request.Request(BASE + path, headers={"Authorization": "Bearer " + token})
    return json.loads(urllib.request.urlopen(req).read())


def main():
    tok = post_form("/auth/login", {"username": "thu_kho", "password": "kho123"})["access_token"]
    mats = get("/materials", tok)
    nvl = next(m for m in mats if m["code"] == "NVL-QUE")
    tp = next(m for m in mats if m["code"] == "TP-TCA")
    batch = post_json(
        "/stock/receipts",
        {"material_id": nvl["id"], "quantity": 200, "ccp1_c14": 13.5, "warehouse_id": 1},
        tok,
    )
    print("batch", batch["batch_no"], batch["ccp1_status"])

    tok2 = post_form("/auth/login", {"username": "ky_thuat", "password": "kt123"})["access_token"]
    order = post_json("/production/orders", {"product_material_id": tp["id"], "planned_qty": 80}, tok2)
    print("order", order["order_no"])
    tok3 = post_form("/auth/login", {"username": "ql_nm", "password": "ql123"})["access_token"]
    post_json(f"/production/orders/{order['id']}/approve", {}, tok3)
    started = post_json(
        f"/production/orders/{order['id']}/start",
        {"materials": [{"batch_id": batch["id"], "quantity": 50}]},
        tok2,
    )
    print("started", started["status"])
    op = post_json(
        f"/production/orders/{order['id']}/operations",
        {"step": "chung_cat", "t_top": 108, "t_ca_percent": 99.5},
        tok2,
    )
    print("ccp2", op["ccp2_status"])
    done = post_json(f"/production/orders/{order['id']}/complete", {"actual_qty": 75}, tok2)
    print("done", done["output_batch_no"])
    trace = get(f"/reports/trace/{done['output_batch_no']}", tok2)
    print("trace inputs", len(trace["input_batches"]), "orders", len(trace["production_orders"]))
    print("E2E OK")


if __name__ == "__main__":
    main()
