from datetime import datetime, timedelta, timezone

# UTC+7 — không phụ thuộc tzdata (Windows)
VN_TZ = timezone(timedelta(hours=7))


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def to_iso_utc(dt: datetime | None) -> str:
    if dt is None:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def vn_today_str() -> str:
    return datetime.now(VN_TZ).strftime("%Y%m%d")


def to_vn_display(dt: datetime | None) -> str:
    if dt is None:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(VN_TZ).strftime("%H:%M:%S %d/%m/%Y")

