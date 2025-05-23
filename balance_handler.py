import pandas as pd

import config
from structs.balance import Balance, SpreadType
import dataclasses as dc


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
        return (self.df.spread_type == SpreadType.MONTHLY.value) & self.df.start_month == 0

    @property
    def yearly_balances_flag (self) -> pd.DataFrame:
        return (self.df.spread_type == SpreadType.YEARLY.value) & self.df.start_month == 0

    @property
    def inactive_monthly_balances_flag (self) -> pd.DataFrame:
        return (self.df.spread_type == SpreadType.MONTHLY.value) & self.df.start_month != 0

    @property
    def inactive_yearly_balances_flag (self) -> pd.DataFrame:
        return (self.df.spread_type == SpreadType.YEARLY.value) & self.df.start_month != 0

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

    def query_balance_by_id (self, balance_id: str) -> Balance | None:
        mask = self.df["id"] == balance_id
        if mask.any():
            return Balance(**self.df[mask].iloc[0].to_dict())

        return None
