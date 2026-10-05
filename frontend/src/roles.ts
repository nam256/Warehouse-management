import type { User } from "./api";
import { VAI_TRO } from "./labels";

const WRITE: Record<string, string[]> = {
  "stock-in": ["admin", "thu_kho"],
  "stock-out": ["admin", "thu_kho", "ky_thuat"],
  production: ["admin", "ky_thuat", "ql_nm"],
  "production-approve": ["admin", "ql_nm"],
  lab: ["admin", "lab", "attp"],
  audit: ["admin", "attp"],
  purchase: ["admin", "thu_kho", "ql_nm"],
};

const MODULE_NAME: Record<keyof typeof WRITE, string> = {
  "stock-in": "Nhập kho",
  "stock-out": "Xuất kho",
  production: "Sản xuất",
  "production-approve": "Duyệt mẻ sản xuất",
  lab: "Phòng kiểm nghiệm",
  audit: "Nhật ký kiểm toán",
  purchase: "Yêu cầu mua hàng",
};

export function canWrite(user: User, module: keyof typeof WRITE): boolean {
  return WRITE[module].includes(user.role) || user.role === "admin";
}

export function roleHint(module: keyof typeof WRITE): string {
  const roles = WRITE[module]
    .filter((r) => r !== "admin")
    .map((r) => VAI_TRO[r] ?? r)
    .join(", ");
  return `Bạn không có quyền ${MODULE_NAME[module]}. Vui lòng đăng nhập bằng tài khoản: ${roles} hoặc Quản trị viên.`;
}
