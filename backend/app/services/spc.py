from dataclasses import dataclass
from math import sqrt
from statistics import fmean, pstdev


@dataclass(frozen=True)
class SpcPoint:
    value: float
    out_of_control: bool


@dataclass(frozen=True)
class SpcResult:
    status: str
    mean: float | None
    std_dev: float | None
    ucl: float | None
    lcl: float | None
    points: list[SpcPoint]


def calculate_spc(values: list[float]) -> SpcResult:
    numeric_values = [float(value) for value in values]
    if len(numeric_values) < 10:
        return SpcResult(
            status="insufficient_data",
            mean=None,
            std_dev=None,
            ucl=None,
            lcl=None,
            points=[SpcPoint(value=value, out_of_control=False) for value in numeric_values],
        )

    # The newest measurement is evaluated against the preceding process baseline.
    # This avoids allowing the point under evaluation to widen its own control limits.
    baseline = numeric_values[:-1]
    mean = fmean(baseline)
    std_dev = pstdev(baseline)
    spread = 3 * std_dev
    ucl = mean + spread
    lcl = mean - spread

    if std_dev == 0:
        points = [
            SpcPoint(value=value, out_of_control=not _is_close(value, mean))
            for value in numeric_values
        ]
    else:
        points = [
            SpcPoint(value=value, out_of_control=value < lcl or value > ucl)
            for value in numeric_values
        ]

    return SpcResult(
        status="ok",
        mean=mean,
        std_dev=std_dev,
        ucl=ucl,
        lcl=lcl,
        points=points,
    )


def _is_close(left: float, right: float) -> bool:
    tolerance = sqrt(2.220446049250313e-16) * max(1.0, abs(left), abs(right))
    return abs(left - right) <= tolerance
