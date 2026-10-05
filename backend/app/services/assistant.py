import json
import re
from datetime import date, timedelta
from typing import Any, Callable

import httpx
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.config import settings
from app.models import (
    CapaStatus,
    CorrectiveAction,
    Material,
    MaterialReservation,
    QualityStatus,
    ReservationStatus,
    StockBatch,
    User,
    UserRole,
)
from app.services.recall import simulate_recall as build_recall
from app.services.report_kb import (
    answer_report_question,
    is_report_howto_question,
    wants_issue_list,
)
from app.services.assistant_intent import canned_reply, classify_intent


class AssistantProviderError(RuntimeError):
    pass


ToolHandler = Callable[[dict[str, Any], Session, User], dict[str, Any]]


def _require_active_user(user: User) -> None:
    if not user or not user.is_active:
        raise PermissionError("Bạn không có quyền sử dụng công cụ này.")


def _get_inventory(params: dict[str, Any], db: Session, user: User) -> dict[str, Any]:
    _require_active_user(user)
    material_code = str(params.get("material_code") or "").strip()
    query = db.query(Material).filter(Material.is_active.is_(True))
    if material_code:
        query = query.filter(Material.code.ilike(f"%{material_code}%"))

    items = []
    for material in query.order_by(Material.code).limit(100).all():
        batches = db.query(StockBatch).filter(StockBatch.material_id == material.id).all()
        batch_ids = [batch.id for batch in batches]
        reservations = (
            db.query(MaterialReservation)
            .filter(
                MaterialReservation.batch_id.in_(batch_ids),
                MaterialReservation.status == ReservationStatus.active,
            )
            .all()
            if batch_ids
            else []
        )
        total = sum(float(batch.quantity) for batch in batches)
        reserved = sum(float(item.quantity) for item in reservations)
        items.append(
            {
                "material_code": material.code,
                "material_name": material.name,
                "unit": material.unit,
                "total_quantity": total,
                "reserved_quantity": reserved,
                "available_quantity": max(total - reserved, 0),
            }
        )
    return {"items": items}


def _get_batch_status(params: dict[str, Any], db: Session, user: User) -> dict[str, Any]:
    _require_active_user(user)
    batch_no = str(params.get("batch_no") or "").strip()
    query = db.query(StockBatch, Material).join(Material, StockBatch.material_id == Material.id)
    if batch_no:
        query = query.filter(StockBatch.batch_no.ilike(f"%{batch_no}%"))
    rows = query.order_by(StockBatch.created_at.desc()).limit(50).all()
    return {
        "batches": [
            {
                "batch_no": batch.batch_no,
                "material_code": material.code,
                "quantity": float(batch.quantity),
                "quality_status": batch.quality_status.value,
                "ccp1_status": batch.ccp1_status.value,
                "expiry_date": batch.expiry_date,
            }
            for batch, material in rows
        ]
    }


def _list_expiring_batches(
    params: dict[str, Any], db: Session, user: User
) -> dict[str, Any]:
    _require_active_user(user)
    allowed_roles = {
        UserRole.admin,
        UserRole.thu_kho,
        UserRole.ky_thuat,
        UserRole.ql_nm,
    }
    if user.role not in allowed_roles:
        raise PermissionError("Bạn không có quyền xem dữ liệu FEFO và hạn dùng.")
    try:
        days = min(max(int(params.get("days", 30)), 0), 365)
    except (TypeError, ValueError):
        days = 30
    cutoff = date.today() + timedelta(days=days)
    rows = (
        db.query(StockBatch, Material)
        .join(Material, StockBatch.material_id == Material.id)
        .filter(
            StockBatch.quantity > 0,
            StockBatch.expiry_date.is_not(None),
            StockBatch.expiry_date <= cutoff,
        )
        .order_by(StockBatch.expiry_date.asc())
        .limit(100)
        .all()
    )
    return {
        "days": days,
        "batches": [
            {
                "batch_no": batch.batch_no,
                "material_code": material.code,
                "quantity": float(batch.quantity),
                "expiry_date": batch.expiry_date,
                "expired": bool(batch.expiry_date and batch.expiry_date < date.today()),
                "quality_status": batch.quality_status.value,
            }
            for batch, material in rows
        ],
    }


def _list_open_capa(params: dict[str, Any], db: Session, user: User) -> dict[str, Any]:
    _require_active_user(user)
    rows = (
        db.query(CorrectiveAction)
        .filter(CorrectiveAction.status != CapaStatus.closed)
        .order_by(CorrectiveAction.created_at.desc())
        .limit(100)
        .all()
    )
    today = date.today()
    return {
        "items": [
            {
                "id": item.id,
                "title": item.title,
                "reason": item.reason,
                "status": item.status.value
                if isinstance(item.status, CapaStatus)
                else str(item.status),
                "due_date": item.due_date,
                "overdue": bool(item.due_date and item.due_date < today),
            }
            for item in rows
        ]
    }


def _explain_stock_reports(params: dict[str, Any], db: Session, user: User) -> dict[str, Any]:
    _require_active_user(user)
    question = str(params.get("question") or "").strip()
    return {"answer": answer_report_question(question)}


def _list_stock_issues(params: dict[str, Any], db: Session, user: User) -> dict[str, Any]:
    _require_active_user(user)
    from app.core.timezone import to_vn_display
    from app.services.audit import short_ref
    from app.services.inventory_report import list_issue_rows

    rows = list_issue_rows(db)[:15]
    return {
        "issues": [
            {
                "reference_no": short_ref(row.reference_no),
                "batch_no": short_ref(row.batch_no),
                "quantity": row.quantity,
                "issue_kind": row.issue_kind,
                "created_at_vn": to_vn_display(row.created_at),
            }
            for row in rows
        ]
    }


def _simulate_recall(params: dict[str, Any], db: Session, user: User) -> dict[str, Any]:
    _require_active_user(user)
    batch_no = str(params.get("batch_no") or "").strip()
    if not batch_no:
        raise ValueError("Cần cung cấp mã lô để mô phỏng thu hồi.")
    batch = db.query(StockBatch).filter(StockBatch.batch_no == batch_no).first()
    if not batch:
        return {"found": False, "batch_no": batch_no, "message": "Không tìm thấy lô."}
    result = build_recall(db, batch.id)
    return {"found": True, **result.to_dict()}


ALLOWED_TOOLS: dict[str, ToolHandler] = {
    "get_inventory": _get_inventory,
    "get_batch_status": _get_batch_status,
    "list_expiring_batches": _list_expiring_batches,
    "list_open_capa": _list_open_capa,
    "simulate_recall": _simulate_recall,
    "explain_stock_reports": _explain_stock_reports,
    "list_stock_issues": _list_stock_issues,
}


TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_inventory",
            "description": "Tra cứu tồn kho hiện tại, có thể lọc theo mã vật tư.",
            "parameters": {
                "type": "object",
                "properties": {"material_code": {"type": "string"}},
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_batch_status",
            "description": "Tra cứu trạng thái chất lượng và CCP1 của lô.",
            "parameters": {
                "type": "object",
                "properties": {"batch_no": {"type": "string"}},
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_expiring_batches",
            "description": "Liệt kê lô hết hạn hoặc sắp hết hạn trong số ngày chỉ định.",
            "parameters": {
                "type": "object",
                "properties": {
                    "days": {"type": "integer", "minimum": 0, "maximum": 365}
                },
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_open_capa",
            "description": "Liệt kê hành động khắc phục đang mở và tình trạng quá hạn.",
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "simulate_recall",
            "description": "Mô phỏng phạm vi thu hồi downstream của một lô, không lưu hay sửa dữ liệu.",
            "parameters": {
                "type": "object",
                "properties": {"batch_no": {"type": "string"}},
                "required": ["batch_no"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "explain_stock_reports",
            "description": (
                "Giải thích cách dùng báo cáo tồn kho, tồn theo kỳ, sổ xuất kho, phiếu PX/PN, "
                "công thức khả dụng, Hold-Release, xuất tay/xuất mẻ. Truyền nguyên câu hỏi."
            ),
            "parameters": {
                "type": "object",
                "properties": {"question": {"type": "string"}},
                "required": ["question"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_stock_issues",
            "description": "Liệt kê phiếu xuất kho PX gần đây (chỉ đọc).",
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        },
    },
]


def run_tool(
    name: str,
    params: dict[str, Any],
    *,
    db: Session,
    user: User,
) -> dict[str, Any]:
    handler = ALLOWED_TOOLS.get(name)
    if handler is None:
        raise ValueError(f"Công cụ '{name}' không được phép.")
    return jsonable_encoder(handler(params, db, user))


def _system_prompt() -> str:
    return (
        "Bạn là trợ lý vận hành Digital QMS chỉ đọc. Chỉ trả lời bằng tiếng Việt. "
        "Chào / cảm ơn / ngoài QMS: trả lời ngắn, không gọi tool tồn kho. "
        "Câu hỏi về báo cáo tồn/xuất, phiếu PX, sổ xuất, tồn theo kỳ, khả dụng, Hold-Release, "
        "trợ lý có được xuất kho không, chat có mất không: "
        "gọi explain_stock_reports với nguyên câu hỏi; nếu hỏi phiếu/sổ xuất đang có thì gọi thêm list_stock_issues. "
        "Mọi số liệu phải lấy từ công cụ; không suy đoán. Không tìm thấy thì nói rõ. "
        "Không phê duyệt lô, không đóng CAPA, không sửa dữ liệu."
    )


def _extract_batch_no(question: str) -> str | None:
    match = re.search(
        r"\b(?:TP|NVL|BB|LO|BATCH|PX|SX|PN|HT)[-_]?(?:\d{8}[-_])?\d+\b",
        question,
        flags=re.IGNORECASE,
    )
    return match.group(0).upper() if match else None


def _extract_material_code(question: str) -> str | None:
    match = re.search(r"\bNVL[-_][A-Z0-9]+\b", question, flags=re.IGNORECASE)
    return match.group(0).upper() if match else None


def _route_local_tools(question: str) -> list[tuple[str, dict[str, Any]]]:
    """Heuristic tool selection for offline/demo without an LLM provider."""
    text = question.lower()
    batch_no = _extract_batch_no(question)
    material_code = _extract_material_code(question)

    if any(k in text for k in ("thu hồi", "thu hoi", "recall")):
        if not batch_no:
            raise ValueError("Cần cung cấp mã lô để mô phỏng thu hồi.")
        return [("simulate_recall", {"batch_no": batch_no})]

    if any(k in text for k in ("capa", "ncr", "khắc phục", "khac phuc")):
        return [("list_open_capa", {})]

    if is_report_howto_question(question):
        calls: list[tuple[str, dict[str, Any]]] = [
            ("explain_stock_reports", {"question": question})
        ]
        if wants_issue_list(question):
            calls.append(("list_stock_issues", {}))
        return calls

    if any(
        k in text
        for k in ("hết hạn", "het han", "hạn dùng", "han dung", "fefo", "expiry")
    ):
        days = 30
        days_match = re.search(r"(\d+)\s*ngày", text)
        if days_match:
            days = int(days_match.group(1))
        return [("list_expiring_batches", {"days": days})]

    if any(
        k in text
        for k in (
            "trạng thái lô",
            "trang thai lo",
            "giải phóng",
            "giai phong",
            "quality",
            "ccp1",
            "quarantine",
        )
    ) or (batch_no and "tồn" not in text and "ton" not in text):
        params: dict[str, Any] = {}
        if batch_no:
            params["batch_no"] = batch_no
        return [("get_batch_status", params)]

    if any(k in text for k in ("tồn kho", "ton kho", "inventory", "còn bao nhiêu", "con bao nhieu")):
        params = {}
        if material_code:
            params["material_code"] = material_code
        return [("get_inventory", params)]

    return []


def _format_local_answer(tool: str, result: dict[str, Any]) -> str:
    if tool == "get_inventory":
        items = result.get("items") or []
        if not items:
            return "Không tìm thấy dữ liệu tồn kho phù hợp."
        lines = [
            f"- {item['material_code']}: sẵn {item['available_quantity']} {item.get('unit') or ''} "
            f"(tổng {item['total_quantity']}, giữ chỗ {item['reserved_quantity']})".strip()
            for item in items[:15]
        ]
        return "Tồn kho hiện tại:\n" + "\n".join(lines)

    if tool == "explain_stock_reports":
        return str(result.get("answer") or "Không tìm thấy hướng dẫn báo cáo phù hợp.")

    if tool == "list_stock_issues":
        issues = result.get("issues") or []
        if not issues:
            return "Chưa có phiếu xuất trong hệ thống. Lập phiếu trên trang Xuất kho rồi in lại ở Báo cáo."
        lines = [
            f"- {item['reference_no']} · lô {item['batch_no']} · {item['quantity']} kg · "
            f"{item['issue_kind']} ({item['created_at_vn']})"
            for item in issues
        ]
        return "Phiếu xuất gần đây:\n" + "\n".join(lines)

    if tool == "get_batch_status":
        batches = result.get("batches") or []
        if not batches:
            return "Không tìm thấy lô phù hợp."
        quality_vi = {
            "quarantine": "cách ly",
            "awaiting_lab": "chờ kiểm nghiệm",
            "awaiting_release": "chờ giải phóng",
            "released": "đã giải phóng",
            "rejected": "từ chối",
        }
        ccp_vi = {"pass": "đạt", "fail": "không đạt", "pending": "chưa có"}
        lines = [
            f"- {item['batch_no']} ({item['material_code']}): "
            f"{quality_vi.get(str(item['quality_status']), item['quality_status'])}, "
            f"CCP1 {ccp_vi.get(str(item['ccp1_status']), item['ccp1_status'])}, "
            f"{item['quantity']} kg"
            for item in batches[:15]
        ]
        return "Trạng thái lô:\n" + "\n".join(lines)

    if tool == "list_expiring_batches":
        batches = result.get("batches") or []
        days = result.get("days", 30)
        if not batches:
            return f"Không có lô hết hạn / sắp hết hạn trong {days} ngày."
        lines = [
            f"- {item['batch_no']} ({item['material_code']}): HSD {item['expiry_date']}, "
            f"SL={item['quantity']}"
            + (" (đã hết hạn)" if item.get("expired") else "")
            for item in batches[:15]
        ]
        return f"Lô hết hạn / sắp hết hạn (≤ {days} ngày):\n" + "\n".join(lines)

    if tool == "list_open_capa":
        items = result.get("items") or []
        if not items:
            return (
                "Hiện không có hành động khắc phục đang mở.\n"
                "Khi Lab không đạt hoặc lô bị từ chối, tạo phiếu trên trang Khắc phục sai lệch "
                "(điều tra → hành động → xác nhận → đóng)."
            )
        status_vi = {
            "open": "Mới mở",
            "investigating": "Đang điều tra",
            "action_pending": "Chờ thực hiện",
            "verification": "Chờ xác nhận",
            "closed": "Đã đóng",
        }
        lines = [
            "Hành động khắc phục đang mở (trang Khắc phục sai lệch):\n"
            "Trợ lý chỉ đọc — không đóng phiếu giúp."
        ]
        for item in items[:15]:
            status = status_vi.get(str(item.get("status") or ""), str(item.get("status") or ""))
            title = item.get("title") or item.get("reason") or "Chưa ghi nội dung"
            due = f", hạn {item['due_date']}" if item.get("due_date") else ""
            late = " — quá hạn" if item.get("overdue") else ""
            lines.append(f"• Số {item['id']}: {status}{due}{late}\n  {title}")
        return "\n".join(lines)

    if tool == "simulate_recall":
        if not result.get("found"):
            return result.get("message") or "Không tìm thấy lô để mô phỏng thu hồi."
        affected = result.get("affected_batches") or result.get("downstream") or []
        count = result.get("affected_count")
        if count is None:
            count = len(affected) if isinstance(affected, list) else "?"
        return (
            f"Mô phỏng thu hồi lô {result.get('root_batch_no') or result.get('batch_no')}: "
            f"{count} lô liên quan downstream (chỉ đọc, không thay đổi dữ liệu)."
        )

    return "Không tìm thấy dữ liệu phù hợp để trả lời."


def _answer_with_local(
    question: str,
    *,
    db: Session,
    user: User,
) -> tuple[str, list[str], list[dict[str, Any]]]:
    canned = canned_reply(classify_intent(question))
    if canned:
        return canned, [], []

    try:
        calls = _route_local_tools(question)
    except ValueError as exc:
        hint = str(exc).strip()
        if "mã lô" in hint.lower():
            hint = f"{hint} Ví dụ: Mô phỏng thu hồi lô TP-001 hoặc NVL-001."
        return hint, [], []

    if not calls:
        return canned_reply("out_of_scope") or "Câu này ngoài phạm vi trợ lý QMS.", [], []

    tools_called: list[str] = []
    data: list[dict[str, Any]] = []
    answers: list[str] = []
    try:
        for name, params in calls:
            result = run_tool(name, params, db=db, user=user)
            tools_called.append(name)
            data.append({"tool": name, "result": result})
            answers.append(_format_local_answer(name, result))
    except PermissionError as exc:
        return str(exc), tools_called, data
    return "\n\n".join(answers), tools_called, data


def _provider_details() -> tuple[str, str, dict[str, str]]:
    provider = settings.ai_provider.lower().strip()
    if provider == "openai":
        if not settings.ai_api_key:
            raise AssistantProviderError("Trợ lý chưa được cấu hình khóa API.")
        base_url = (settings.ai_base_url or "https://api.openai.com/v1").rstrip("/")
        return provider, f"{base_url}/chat/completions", {
            "Authorization": f"Bearer {settings.ai_api_key}"
        }
    if provider == "ollama":
        base_url = (settings.ai_base_url or "http://localhost:11434").rstrip("/")
        return provider, f"{base_url}/api/chat", {}
    raise AssistantProviderError("Chưa cấu hình nhà cung cấp AI cho trợ lý.")


def _post_provider(
    provider: str,
    url: str,
    headers: dict[str, str],
    messages: list[dict[str, Any]],
    *,
    tools: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {"model": settings.ai_model, "messages": messages}
    if provider == "openai":
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        payload["temperature"] = 0
    else:
        payload["stream"] = False
        if tools:
            payload["tools"] = tools
    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            body = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise AssistantProviderError(
            "Trợ lý tạm thời không khả dụng. Vui lòng thử lại sau."
        ) from exc
    try:
        return body["choices"][0]["message"] if provider == "openai" else body["message"]
    except (KeyError, IndexError, TypeError) as exc:
        raise AssistantProviderError("Nhà cung cấp AI trả về dữ liệu không hợp lệ.") from exc


def _parse_tool_calls(message: dict[str, Any]) -> list[tuple[str, dict[str, Any], str]]:
    calls = []
    for index, call in enumerate(message.get("tool_calls") or []):
        function = call.get("function") or {}
        name = str(function.get("name") or "")
        raw_args = function.get("arguments") or {}
        if isinstance(raw_args, str):
            try:
                args = json.loads(raw_args)
            except json.JSONDecodeError as exc:
                raise AssistantProviderError("Tham số công cụ từ AI không hợp lệ.") from exc
        elif isinstance(raw_args, dict):
            args = raw_args
        else:
            raise AssistantProviderError("Tham số công cụ từ AI không hợp lệ.")
        calls.append((name, args, str(call.get("id") or f"tool-{index}")))
    return calls[:5]


def answer_question(
    question: str,
    *,
    db: Session,
    user: User,
) -> tuple[str, list[str], list[dict[str, Any]]]:
    provider = settings.ai_provider.lower().strip()
    if provider == "local":
        return _answer_with_local(question, db=db, user=user)

    provider, url, headers = _provider_details()
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": _system_prompt()},
        {"role": "user", "content": question},
    ]
    selection = _post_provider(
        provider, url, headers, messages, tools=TOOL_SCHEMAS
    )
    calls = _parse_tool_calls(selection)
    if not calls:
        return "Không tìm thấy dữ liệu phù hợp để trả lời.", [], []

    tools_called: list[str] = []
    data: list[dict[str, Any]] = []
    messages.append(selection)
    for name, params, call_id in calls:
        try:
            result = run_tool(name, params, db=db, user=user)
        except ValueError as exc:
            raise AssistantProviderError(str(exc)) from exc
        tools_called.append(name)
        data.append({"tool": name, "result": result})
        tool_message = {
            "role": "tool",
            "content": json.dumps(result, ensure_ascii=False),
        }
        if provider == "openai":
            tool_message["tool_call_id"] = call_id
        messages.append(tool_message)

    final_message = _post_provider(provider, url, headers, messages, tools=None)
    answer = str(final_message.get("content") or "").strip()
    return answer or "Không tìm thấy dữ liệu phù hợp để trả lời.", tools_called, data
