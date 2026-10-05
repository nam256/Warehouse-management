# Thiết kế CSDL — Oxeyns Kho & SX

## Stack

- **SQLite** (mặc định): `backend/oxeyns.db`
- ORM: **SQLAlchemy 2** — `backend/app/models.py`
- PostgreSQL có trong `docker-compose.yml` nhưng **chưa kết nối** trong phiên bản báo cáo

## ERD (14 bảng)

Sơ đồ đầy đủ (cột + quan hệ FK):

| File | Mục đích |
|------|----------|
| `docs/bao-cao/erd.mmd` | Mermaid — render tại [mermaid.live](https://mermaid.live) |
| `docs/bao-cao/erd.dot` | Graphviz DOT |
| `docs/bao-cao/hinh-3-1-erd.png` | PNG cho Word (Hình 3.1) |

**Sinh lại từ models:**

```powershell
python scripts/generate_erd.py
```

(Cần [Graphviz](https://graphviz.org/download/) để xuất PNG.)

### Tóm tắt quan hệ

```
users ──< audit_logs, production_orders, operation_records, lab_tests,
         purchase_requests, stock_movements, mixing_reports, corrective_actions
materials ──< stock_batches, production_orders, purchase_requests
suppliers ──< stock_batches
warehouses ──< stock_batches
stock_batches ──< stock_movements, production_material_usages, lab_tests
production_orders ──< production_material_usages, operation_records,
                      lab_tests, mixing_reports, stock_movements
production_orders ──> stock_batches (output_batch_id, source_order_id)
corrective_actions (entity_type + entity_id — polymorphic)
```

## Bảng chính

### users
| Cột | Kiểu | Ghi chú |
|-----|------|---------|
| id | PK | |
| username | unique | |
| password_hash | | bcrypt |
| full_name | | |
| role | enum | admin, thu_kho, ky_thuat, lab, ql_nm, attp |
| is_active | bool | |

### materials
| Cột | Kiểu | Ghi chú |
|-----|------|---------|
| id | PK | |
| code | unique | Mã NVL/BTP/TP |
| name | | |
| type | enum | NVL, BTP, TP |
| unit | | kg, L |
| min_stock | decimal | Cảnh báo tồn |

### suppliers / warehouses
| id, code, name, ... |

### stock_batches
| id, batch_no, material_id, supplier_id, warehouse_id, quantity, ccp1_c14, ccp1_status, source_order_id |

### stock_movements
| id, movement_type (IN/OUT), batch_id, quantity, reference_no, production_order_id, created_by_id |

### production_orders
| id, order_no, product_material_id, planned_qty, actual_qty, status, order_type, output_batch_id |

### production_material_usages
| id, order_id, batch_id, quantity, movement_id |

### operation_records
| id, order_id, step, temperature, pressure, t_top, t_ca_percent, ccp2_status |

### lab_tests
| id, order_id, batch_id, test_type, gc_data, c14, t_ca_percent, result_status |

### mixing_reports / purchase_requests / audit_logs / corrective_actions
Xem `backend/app/models.py`.

## Quy tắc mã

| Loại | Mẫu | Ví dụ |
|------|-----|-------|
| Lô NVL | `NVL-YYYYMMDD-###` | NVL-20260620-001 |
| Phiếu nhập | `PN-YYYYMMDD-###` | PN-20260620-001 |
| Mẻ SX | `SX-YYYYMMDD-###` | SX-20260620-001 |
| Lô TP | `TP-YYYYMMDD-###` | TP-20260620-001 |
