import pandas as pd

import config
from structs.balance import Balance, BalanceType, FrequencyType, SpreadType
from structs.payment import PaymentStatus
from dateutil.relativedelta import relativedelta
import dataclasses as dc


def read_balance() -> Balance:
    balance_id = input("Enter balance id: ")
    name = input("Enter name: ")
    value = float(input("Enter value: "))
    frequency = int(input("Enter frequency: "))
    frequency_unit = input("Enter frequency unit ({}): ".format(', '.join([e.value for e in FrequencyType]))),
    spread_prompt = "Enter spread type ({}): ".format(', '.join([e.value for e in SpreadType]))
    spread_type_str = input(spread_prompt)
    expiry = input("Enter expiry month (or leave empty): ")
    start_month_input = input("Enter start month (or leave empty): ")
    start_month = int(start_month_input) if start_month_input else None
    balance_type_prompt = "Enter balance type ({}): ".format(', '.join([e.value for e in BalanceType]))
    balance_type_str = input(balance_type_prompt)

    return Balance(
        id=balance_id,
        name=name,
        value=value,
        frequency=frequency,
        frequency_unit=FrequencyType(frequency_unit),
        spread_type=SpreadType(spread_type_str),
        expiry=expiry,
        start_month=start_month,
        type=BalanceType(balance_type_str)
    )

@dc.dataclass(kw_only=True)
class BalanceHandler:
    df: pd.DataFrame = dc.field(init=False)

    def __post_init__ (self) -> None:
        try:
            self.df = pd.read_csv(config.BALANCE_FILE_PATH)

        except FileNotFoundError:
            self._init_dataframe()

    def _init_dataframe (self) -> None:
        headers = [
            "id", "name", "value", "frequency", "frequency_unit",
            "spread_type", "expiry", "start_month", "type"
        ]

        self.df = pd.DataFrame(columns=headers)

    @property
    def monthly_balances_flag (self) -> pd.DataFrame:
        return (self.df.spread_type == SpreadType.MONTHLY.value) & self.df.start_month.isna()

    @property
    def yearly_balances_flag (self) -> pd.DataFrame:
        return (self.df.spread_type == SpreadType.YEARLY.value) & self.df.start_month.isna()

    @property
    def inactive_monthly_balances_flag (self) -> pd.DataFrame:
        return (self.df.spread_type == SpreadType.MONTHLY.value) & self.df.start_month.notna()

    @property
    def inactive_yearly_balances_flag (self) -> pd.DataFrame:
        return (self.df.spread_type == SpreadType.YEARLY.value) & self.df.start_month.notna()

    def add_balances (self, balances: list[Balance]) -> None:
        if len(balances) == 0:
            return

        df_new = pd.DataFrame([balance.to_csv() for balance in balances])
        self.df = pd.concat([self.df, df_new], ignore_index=True)

    def update_balances_by_id (self, balances: list[Balance]) -> None:
        if len(balances) == 0:
            return

        for balance in balances:
            mask = self.df["id"] == balance.id
            if mask.any():
                new_data = balance.to_csv()
                self.df.loc[mask, list(new_data.keys())] = list(new_data.values())

            else:
                raise ValueError(f"Balance with id {balance.id} not found")

    def remove_balances_by_id (self, balances_id: list[str]) -> None:
        if len(balances_id) == 0:
            return

        self.df = self.df[~self.df["id"].isin(balances_id)]
