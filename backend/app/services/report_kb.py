"""Hỏi–đáp vận hành / báo cáo — câu ngắn, dễ bảo vệ, không dump tồn kho."""

from __future__ import annotations

# Mỗi topic: (ưu tiên khi hòa điểm, từ khóa, đáp án).
# Đáp án dùng xuống dòng — khung chat white-space: pre-wrap.
TOPICS: list[tuple[int, tuple[str, ...], str]] = [
    (
        1,
        (
            "phiếu xuất",
            "phieu xuat",
            "in phiếu xuất",
            "in phieu xuat",
            "px-",
            "xem trước phiếu",
            "in lại phiếu",
            "in lai phieu",
        ),
        "In phiếu xuất kho (PX)\n"
        "1. Vào Xuất kho, chọn lô đã giải phóng, đạt CCP1, còn hạn, còn khả dụng — lưu phiếu.\n"
        "2. Bấm Xem trước, đối chiếu số kg, rồi Tải PDF.\n"
        "3. In lại phiếu cũ: Báo cáo → Phiếu xuất kho → chọn số PX (PX-001…).\n"
        "Mỗi lần lưu = một lô, một phiếu. Vượt khả dụng, lô cách ly hoặc hết hạn thì không tạo phiếu.\n"
        "Đây là biểu mẫu số hóa nội bộ, không thay phiếu giấy pháp lý.",
    ),
    (
        2,
        (
            "sổ xuất",
            "so xuat",
            "danh sách phiếu",
            "danh sach phieu",
            "lọc ngày xuất",
            "loc ngay xuat",
            "kỳ không có xuất",
            "ky khong co xuat",
        ),
        "Sổ xuất kho\n"
        "Vào Báo cáo → Sổ xuất kho. Chọn từ ngày–đến ngày (để trống = toàn bộ) rồi Xem trước / CSV / PDF.\n"
        "Cột: số PX, giờ Việt Nam, lô, vật tư, kg, loại (xuất tay hoặc xuất cho mẻ SX-…), người lập.\n"
        "Kỳ không có phiếu: file vẫn tải, bảng trống, tổng 0 kg. Hai lần xuất cùng lô = hai số PX, tồn giảm lần lượt.",
    ),
    (
        3,
        (
            "theo kỳ",
            "theo ky",
            "tồn đầu",
            "ton dau",
            "nhập trong kỳ",
            "xuất trong kỳ",
            "tồn cuối",
            "ton cuoi",
            "bm-02",
        ),
        "Báo cáo tồn theo kỳ (BM-02/GMP01)\n"
        "Vào Báo cáo → Tồn kho theo kỳ. Chọn khoảng ngày (từ > đến thì hệ thống đảo lại).\n"
        "Công thức: tồn cuối = tồn hiện tại; tồn đầu = cuối − nhập − hoàn tồn + xuất trong kỳ.\n"
        "Đây là tính ngược từ sổ movement, không phải khóa sổ kế toán. Vật tư không còn lô vẫn hiện dòng 0.",
    ),
    (
        4,
        (
            "khả dụng",
            "kha dung",
            "vật lý",
            "vat ly",
            "giữ chỗ",
            "giu cho",
            "cách ly",
            "cach ly",
            "hold-release",
            "hold release",
            "quarantine",
        ),
        "Ba số tồn — cùng công thức trên màn Tồn kho và trên file\n"
        "• Vật lý = kg đang nằm trên lô.\n"
        "• Giữ chỗ = reservation đang active (mẻ đã duyệt, chưa xuất).\n"
        "• Khả dụng = 0 nếu lô chưa giải phóng, CCP1 chưa đạt hoặc hết hạn; không thì max(vật lý − giữ chỗ, 0).\n"
        "Lô vừa nhập (cách ly) hoặc Lab đạt nhưng ATTP chưa giải phóng: thấy vật lý, không xuất được.\n"
        "Cảnh báo tồn thấp so khả dụng với mức tối thiểu, không so vật lý.",
    ),
    (
        5,
        (
            "xuất tay",
            "xuat tay",
            "thủ công",
            "thu cong",
            "xuất cho mẻ",
            "xuat cho me",
            "hoàn tồn",
            "hoan ton",
            "hủy mẻ",
            "huy me",
        ),
        "Xuất tay và xuất cho mẻ\n"
        "• Xuất tay: lập trên trang Xuất kho, phiếu ghi “Xuất kho thủ công”, không gắn mẻ.\n"
        "• Xuất cho mẻ: khi bắt đầu sản xuất, phiếu gắn mã SX-…\n"
        "Hủy mẻ đang chạy tạo phiếu hoàn tồn (HT). Phiếu PX gốc không bị xóa. Sổ xuất ghi rõ loại.",
    ),
    (
        6,
        (
            "theo lô",
            "theo lo",
            "báo cáo fefo",
            "bao cao fefo",
            "ccp1 không đạt",
            "lô hết hạn còn",
        ),
        "Báo cáo tồn theo lô\n"
        "Báo cáo → tồn theo lô: mỗi mã lô một dòng (HSD, CCP1, chất lượng, vật lý / giữ chỗ / khả dụng).\n"
        "Dùng khi hỏi FEFO hoặc Hold-Release. Lô hết hạn hoặc CCP1 không đạt: khả dụng 0, vẫn thấy vật lý nếu còn kg.\n"
        "Trang Xuất kho gợi ý lô HSD sớm; mỗi lần lưu vẫn một lô (chưa xuất nhiều lô một phiếu).",
    ),
    (
        7,
        (
            "phiếu nhập",
            "phieu nhap",
            "sl lúc nhập",
            "số lượng nhập",
            "in phiếu nhập",
        ),
        "Phiếu nhập kho (PN)\n"
        "Báo cáo → chọn lô → Xem trước phiếu nhập.\n"
        "Số kg trên phiếu là lúc nhập, không phải tồn hiện tại nếu lô đã xuất bớt.",
    ),
    (
        8,
        (
            "mã ngắn",
            "ma ngan",
            "sx-001",
            "rút ngắn",
            "rut ngan",
        ),
        "Mã trên báo cáo\n"
        "SX-001, NVL-001, PX-001 (bỏ phần ngày). Danh sách xếp theo số. Mã vật tư NVL-QUE giữ nguyên.",
    ),
    (
        9,
        (
            "utf",
            "xem trước",
            "xem truoc",
            "tải file",
            "tai file",
            "mở excel",
            "mo excel",
            "mất dấu pdf",
        ),
        "Xuất file\n"
        "CSV UTF-8 BOM — mở Excel không lỗi font. PDF tiếng Việt, có dấu.\n"
        "Luôn Xem trước rồi mới Tải xuống. Trang Báo cáo gồm: tồn hiện tại, tồn theo kỳ, sổ xuất, phiếu PX/PN, vận hành, cân đối, pha trộn, GC.",
    ),
    (
        10,
        (
            "ai được xuất",
            "ai duoc xuat",
            "không được xuất",
            "khong duoc xuat",
            "403",
            "quyền xuất",
            "quyen xuat",
        ),
        "Quyền\n"
        "Mọi tài khoản đăng nhập xem và in báo cáo.\n"
        "Lập phiếu xuất: thủ kho, kỹ thuật, admin. Vai trò khác bị từ chối (403).\n"
        "Trợ lý chỉ đọc — không xuất kho, không phê duyệt lô.",
    ),
    (
        11,
        (
            "chưa xuất",
            "10 kg",
            "10kg",
            "kho trống",
            "kho trong",
            "reset_db",
            "không có phiếu",
        ),
        "Số ảo và kho trống\n"
        "Ô “Đã xuất” trên form = tổng phiếu OUT thật. Form trống không hiện 10 kg ảo.\n"
        "Sau reset dữ liệu: 3 vật tư mẫu, tồn 0, không cảnh báo ảo. Kỳ không xuất: sổ vẫn tải, bảng trống.",
    ),
    (
        12,
        (
            "nhật ký thao tác",
            "nhat ky thao tac",
            "người lập",
            "nguoi lap",
            "ai xuất",
            "ai xuat",
        ),
        "Ai xuất — nhật ký\n"
        "Phiếu PX ghi người lập. Nhật ký thao tác có sự kiện xuất kèm số PX.\n"
        "In lại cùng số phiếu, có thời điểm in.",
    ),
    (
        13,
        (
            "thành phẩm",
            "thanh pham",
            "bán thành phẩm",
            "ban thanh pham",
            "nvl / btp",
        ),
        "NVL, BTP, TP\n"
        "Báo cáo tách loại nguyên liệu / bán thành phẩm / thành phẩm.\n"
        "Thành phẩm xuất cùng luồng OUT; Hold-Release giống nguyên liệu.",
    ),
    (
        14,
        (
            "chỉ đọc",
            "chi doc",
            "duyệt lô",
            "duyet lo",
            "được xuất kho",
            "duoc xuat kho",
            "bịa số",
            "bia so",
            "phê duyệt lô",
            "phe duyet lo",
        ),
        "Phạm vi trợ lý\n"
        "Trợ lý chỉ đọc: không xuất kho, không phê duyệt lô, không đóng CAPA, không bịa số kg.\n"
        "Hỏi số liệu thì đọc từ công cụ (tồn, lô, phiếu). Không có dữ liệu thì nói không tìm thấy.",
    ),
    (
        15,
        (
            "mất chat",
            "mat chat",
            "đoạn chat",
            "doan chat",
            "tắt khung",
            "tat khung",
            "lưu chat",
            "luu chat",
            "timeout",
            "treo chat",
        ),
        "Chat có mất không?\n"
        "Đóng khung chỉ ẩn — hội thoại còn. F5 đọc lại trên máy này theo tài khoản.\n"
        "Nút Mới mới xóa chat trên trình duyệt; nhật ký câu hỏi trên máy chủ vẫn giữ.\n"
        "Tắc mạng: Hủy hoặc hết 25 giây; tin đã gửi vẫn còn. Kéo góc trên-trái để phóng to khung.",
    ),
    (
        16,
        (
            "lớn hơn khả dụng",
            "lon hon kha dung",
            "vượt khả dụng",
            "vuot kha dung",
            "sl >",
            "không chọn được lô",
            "khong chon duoc lo",
        ),
        "Xuất khi không đủ điều kiện\n"
        "Số kg lớn hơn khả dụng → không ghi phiếu.\n"
        "Lô cách ly, CCP1 chưa đạt, hết hạn: không chọn được / bị từ chối.\n"
        "Không có phiếu ảo trên sổ xuất.",
    ),
    (
        17,
        (
            "ui khác file",
            "tồn trên file",
            "ton tren file",
            "cùng công thức",
            "cung cong thuc",
            "đối chiếu tồn",
            "doi chieu ton",
        ),
        "Tồn trên màn hình và trên file\n"
        "Cùng một công thức: khả dụng = vật lý − giữ chỗ (và 0 nếu chưa được xuất).\n"
        "In snapshot tại thời điểm đó (giờ Việt Nam). Không nhập tay trên Excel.",
    ),
    (
        18,
        (
            "nhập kho",
            "nhap kho",
            "làm sao nhập",
            "lam sao nhap",
        ),
        "Nhập kho\n"
        "Trang Nhập kho: chọn vật tư, số kg, hạn dùng — lưu phiếu PN, tạo lô đang cách ly.\n"
        "Lô này tăng tồn vật lý, khả dụng = 0 cho đến khi Lab đạt và ATTP giải phóng.",
    ),
    (
        19,
        (
            "tạo mẻ",
            "tao me",
            "duyệt mẻ",
            "duyet me",
            "bắt đầu sản xuất",
            "bat dau san xuat",
            "giữ chỗ fefo",
        ),
        "Sản xuất\n"
        "Tạo mẻ trên trang Sản xuất. Khi quản lý duyệt, hệ thống giữ chỗ FEFO — tồn vật lý chưa giảm, khả dụng giảm.\n"
        "Bắt đầu sản xuất mới xuất kho (phiếu gắn SX-…). Hủy mẻ đang chạy → hoàn tồn HT, không xóa PX gốc.",
    ),
    (
        20,
        (
            "kiểm nghiệm",
            "kiem nghiem",
            "kết quả lab",
            "ket qua lab",
            "ccp1",
        ),
        "Kiểm nghiệm (Lab)\n"
        "Trang Kiểm nghiệm: nhập kết quả, đạt/không đạt CCP1.\n"
        "Đạt rồi vẫn chưa xuất được — ATTP phải giải phóng lô trên Phê duyệt chất lượng.",
    ),
    (
        21,
        (
            "phê duyệt chất lượng",
            "phe duyet chat luong",
            "attp",
            "chữ ký giải phóng",
            "chu ky giai phong",
        ),
        "Phê duyệt chất lượng\n"
        "ATTP / quản trị giải phóng hoặc từ chối lô sau khi Lab đạt.\n"
        "Chỉ lô đã giải phóng mới vào khả dụng và mới lập được phiếu xuất.",
    ),
    (
        22,
        (
            "mua hàng",
            "mua hang",
            "yêu cầu mua",
            "yeu cau mua",
        ),
        "Yêu cầu mua hàng\n"
        "Khi tồn khả dụng thấp, thủ kho / quản lý tạo yêu cầu mua trên trang Yêu cầu mua hàng.\n"
        "Đây là đề nghị nội bộ, không phải đơn đặt hàng nhà cung cấp.",
    ),
    (
        23,
        (
            "điểm kiểm soát",
            "diem kiem soat",
            "haccp",
            "hồ sơ haccp",
        ),
        "Giám sát điểm kiểm soát\n"
        "Trang Giám sát điểm kiểm soát (HACCP) theo dõi CCP. Xuất file khi cần nộp hồ sơ vận hành.\n"
        "Không thay chứng nhận FSSC giấy.",
    ),
    (
        24,
        (
            "tồn thấp",
            "ton thap",
            "dưới mức",
            "duoi muc",
            "chuông",
            "chuong",
        ),
        "Cảnh báo chuông\n"
        "So khả dụng với mức tối thiểu — lô cách ly còn kg không báo hết hàng.\n"
        "Thêm: lô hết hạn / sắp hết hạn (30 ngày), chờ giải phóng, CCP1/CCP2 không đạt, khắc phục quá hạn hoặc sắp hạn, yêu cầu mua chờ duyệt.\n"
        "Cảnh báo mới: chuông kêu, rung máy (nếu trình duyệt cho phép), làm mới khoảng 60 giây. Bấm chuông một lần để mở tiếng.",
    ),
    (
        25,
        (
            "kế toán",
            "ke toan",
            "hóa đơn",
            "hoa don",
            "giá vốn",
            "gia von",
        ),
        "Không phải báo cáo kế toán\n"
        "Đây là hồ sơ vận hành / GMP số hóa cho nhà máy tinh dầu: thẩm tra CCP và truy xuất lô.\n"
        "Không có hóa đơn VAT, giá vốn hay khóa sổ tài chính.",
    ),
    (
        26,
        (
            "nhiều lô một lần",
            "nhieu lo mot lan",
            "xuất 120",
            "xuat 120",
            "một phiếu nhiều dòng",
        ),
        "Xuất nhiều lô một lần\n"
        "Hiện tại mỗi lần lưu xuất tay = một lô. Sản xuất đã FEFO lúc duyệt mẻ.\n"
        "Nếu cần 120 kg mà lô gần hạn chỉ 80 kg: xuất lần lượt hai phiếu, hoặc xuất qua mẻ đã duyệt.",
    ),
]


def is_quantity_question(text: str) -> bool:
    lowered = text.lower()
    return any(
        token in lowered
        for token in (
            "còn bao nhiêu",
            "con bao nhieu",
            "bao nhiêu kg",
            "bao nhieu kg",
        )
    )


def is_report_howto_question(question: str) -> bool:
    text = question.lower()
    if is_quantity_question(text) and not any(
        token in text for token in ("khả dụng", "kha dung", "báo cáo", "bao cao", "phiếu", "phieu")
    ):
        return False
    needles = (
        "báo cáo",
        "bao cao",
        "phiếu xuất",
        "phieu xuat",
        "sổ xuất",
        "so xuat",
        "theo kỳ",
        "theo ky",
        "khả dụng",
        "kha dung",
        "giữ chỗ",
        "giu cho",
        "in phiếu",
        "in phieu",
        "in pdf",
        "biểu mẫu",
        "bieu mau",
        "cách ly",
        "cach ly",
        "xuất tay",
        "xuat tay",
        "xuất cho mẻ",
        "xuat cho me",
        "hoàn tồn",
        "hoan ton",
        "phiếu nhập",
        "phieu nhap",
        "xem trước",
        "xem truoc",
        "hold",
        "tồn đầu",
        "ton dau",
        "tồn cuối",
        "bm-02",
        "px-",
        "chỉ đọc",
        "chi doc",
        "duyệt lô",
        "duyet lo",
        "được xuất kho",
        "duoc xuat kho",
        "bịa",
        "bia so",
        "mất chat",
        "mat chat",
        "đoạn chat",
        "doan chat",
        "tắt khung",
        "tat khung",
        "lưu chat",
        "luu chat",
        "timeout",
        "treo chat",
        "nhập kho",
        "nhap kho",
        "tạo mẻ",
        "tao me",
        "kiểm nghiệm",
        "kiem nghiem",
        "phê duyệt chất lượng",
        "yêu cầu mua",
        "yeu cau mua",
        "điểm kiểm soát",
        "haccp",
        "tồn thấp",
        "ton thap",
        "kế toán",
        "ke toan",
        "vượt khả dụng",
        "vuot kha dung",
        "cùng công thức",
        "doi chieu",
        "đối chiếu",
        "nhiều lô",
        "nhieu lo",
        "tồn trên file",
        "ton tren file",
        "làm sao nhập",
        "lam sao nhap",
    )
    if any(token in text for token in needles):
        return True
    return "xuất kho" in text and any(
        token in text for token in ("in", "báo", "phiếu", "sổ", "cách", "làm sao", "lam sao")
    )


def wants_issue_list(question: str) -> bool:
    """Chỉ liệt kê phiếu khi user hỏi danh sách, không kèm hướng dẫn in."""
    text = question.lower()
    listing = any(
        token in text
        for token in (
            "phiếu gần đây",
            "phieu gan day",
            "danh sách phiếu xuất",
            "danh sach phieu xuat",
            "những phiếu xuất",
            "nhung phieu xuat",
            "px mới",
            "px moi",
        )
    )
    return listing


def answer_report_question(question: str) -> str:
    text = question.lower()
    scored: list[tuple[int, int, str]] = []
    for priority, keywords, body in TOPICS:
        score = sum(1 for keyword in keywords if keyword in text)
        if score:
            scored.append((score, priority, body))
    scored.sort(key=lambda item: (-item[0], item[1]))
    bodies = [body for _, _, body in scored[:2]]
    if not bodies:
        bodies = [
            "Trợ lý hướng dẫn thao tác và đọc số liệu QMS.\n"
            "Hỏi: in phiếu PX, sổ xuất, tồn theo kỳ, khả dụng, phiếu nhập, sản xuất, Lab, CAPA.\n"
            "Bấm gợi ý dưới ô nhập, hoặc kéo góc trên-trái để xem cho rõ."
        ]
    return "\n\n".join(bodies)
