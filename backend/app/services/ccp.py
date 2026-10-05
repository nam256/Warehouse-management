CCP1_MIN = 13.02
CCP1_MAX = 14.39
CCP2_TTOP_MIN = 107.0
CCP2_TTOP_MAX = 110.0
CCP2_TCA_MIN = 99.0


def evaluate_ccp1(c14: float | None) -> str:
    if c14 is None:
        return "pending"
    if CCP1_MIN <= c14 <= CCP1_MAX:
        return "pass"
    return "fail"


def evaluate_ccp2(t_top: float | None, t_ca_percent: float | None) -> str:
    if t_top is None and t_ca_percent is None:
        return "pending"
    if t_top is not None and not (CCP2_TTOP_MIN <= t_top <= CCP2_TTOP_MAX):
        return "fail"
    if t_ca_percent is not None and t_ca_percent <= CCP2_TCA_MIN:
        return "fail"
    if t_top is not None and t_ca_percent is not None:
        return "pass"
    return "pending"
