import numpy as np
import dataclasses as dc
from enum import StrEnum


class BalanceType (StrEnum):
    CREDIT = "credit"
    PAYMENT = "pay"
    INVESTMENT = "investment"
    EXPENSE = "expense"

    def is_investment (self) -> bool:
        return self is BalanceType.INVESTMENT

    def is_payment (self) -> bool:
        return self is BalanceType.PAYMENT

class SpreadType (StrEnum):
    MONTHLY = "monthly"
    YEARLY = "yearly"

class FrequencyType (StrEnum):
    MONTH = "/month"
    YEAR = "/year"

@dc.dataclass(kw_only=True)
class Balance:
    id: str
    name: str
    value: float
    frequency: float
    frequency_unit: FrequencyType
    spread_type: SpreadType
    expiry: dc.InitVar[int | None] = None
    start_month: dc.InitVar[int | None] = None
    type: BalanceType

    _expiry: int = dc.field(init=False)
    _start_month: int = dc.field(init=False)

    def __post_init__ (self, expiry: int | None, start_month: int | None) -> None:
        self._expiry = expiry if expiry is not None else np.inf
        self._start_month = self.start_month if start_month is not None else 0

        if isinstance(self.frequency_unit, str):
            self.frequency_unit = FrequencyType(self.frequency_unit)

        if isinstance(self.spread_type, str):
            self.spread_type = SpreadType(self.spread_type)

        if isinstance(self.type, str):
            self.type = BalanceType(self.type)

    def to_csv (self) -> dict[str, str | float]:
        return {
            "id": self.id,
            "name": self.name,
            "value": self.value,
            "frequency": self.frequency,
            "frequency_unit": self.frequency_unit.value,
            "spread_type": self.spread_type.value,
            "expiry": self._expiry,
            "start_month": self._start_month,
            "type": self.type.value
        }

    @property
    def balance_ratio (self) -> float:
        if (
            (self.spread_type is SpreadType.MONTHLY and self.frequency_unit is FrequencyType.MONTH)
            or (self.spread_type is SpreadType.YEARLY and self.frequency_unit is FrequencyType.YEAR)
        ):
            return self.frequency

        elif self.frequency_unit is FrequencyType.YEAR:
            return self.frequency / 12

        else:
            return self.frequency * 12

    @property
    def balance_value (self) -> float:
        return self.value * self.balance_ratio * (
            -1 if self.type in [BalanceType.EXPENSE, BalanceType.PAYMENT] else 1
        )
