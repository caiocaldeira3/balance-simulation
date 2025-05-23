import dataclasses as dc

from structs.balance import Balance, BalanceType


@dc.dataclass(kw_only=True)
class FinancialBreakdown:
    credit: float = 0
    debit: float = 0
    investment: float = 0
    payment: float = 0

    def add_finance (self, balance: Balance) -> None:
        if balance.type is BalanceType.EXPENSE:
            self.debit += Balance.balance_value

        elif balance.type is BalanceType.CREDIT:
            self.credit += balance.balance_value

        if balance.type is BalanceType.PAYMENT:
            self.payment += balance.balance_value

        elif balance.type is BalanceType.INVESTMENT:
            self.investment += balance.balance_value

    def __iadd__ (self, other: "FinancialBreakdown") -> "FinancialBreakdown":
        self.credit += other.credit
        self.debit += other.debit
        self.investment += other.investment
        self.payment += other.payment
        return self

    def __add__ (self, other: "FinancialBreakdown") -> "FinancialBreakdown":
        return FinancialBreakdown(
            credit=self.credit + other.credit,
            debit=self.debit + other.debit,
            investment=self.investment + other.investment,
            payment=self.payment + other.payment,
        )

    def __sub__ (self, other: "FinancialBreakdown") -> "FinancialBreakdown":
        return FinancialBreakdown(
            credit=self.credit - other.debit,
            debit=self.debit - other.debit,
            investment=self.investment - other.investment,
            payment=self.payment - other.payment,
        )

    def copy (self) -> "FinancialBreakdown":
        return FinancialBreakdown(
            credit=self.credit,
            debit=self.debit,
            investment=self.investment,
            payment=self.payment,
        )

@dc.dataclass(kw_only=True)
class PaymentStatus:
    payment_size: float
    investment_size: float

    monthly_balances: list[Balance]
    yearly_balances: list[Balance]
    inactive_monthly_balances: list[Balance]
    inactive_yearly_balances: list[Balance]

    monthly_breakdown: FinancialBreakdown = dc.field(init=False)
    yearly_breakdown: FinancialBreakdown = dc.field(init=False)

    total_breakdown: FinancialBreakdown = dc.field(init=False)

    def __post_init__ (self) -> None:
        self.monthly_balances.sort(key=lambda balance: balance._expiry, reverse=True)
        self.yearly_balances.sort(key=lambda balance: balance._expiry, reverse=True)

        self.inactive_monthly_balances.sort(key=lambda balance: balance._start_month, reverse=True)
        self.inactive_yearly_balances.sort(key=lambda balance: balance._start_month, reverse=True)

        self.monthly_breakdown = self.compute_active_metric(self.monthly_balances)
        self.yearly_breakdown = self.compute_active_metric(self.yearly_balances)
        self.total_breakdown = FinancialBreakdown()

    @classmethod
    def compute_active_metric (cls, metric: list[Balance]) -> FinancialBreakdown:
        metric_breakdown = FinancialBreakdown()

        for balance in metric:
            metric_breakdown.add_finance(balance)

        return metric_breakdown

    @classmethod
    def update_metric (cls, metric: list[Balance], occ: int) -> FinancialBreakdown:
        metric_breakdown = FinancialBreakdown()

        while len(metric) > 0 and occ == metric[-1][0]:
            metric_breakdown.add_finance(metric.pop())

        return metric_breakdown

    def update_curr_year (self, new_year: int) -> None:
        removal_breakdown = self.update_metric(self.yearly_balances, new_year)
        activation_breakdown = self.update_metric(self.inactive_yearly_balances, new_year)

        self.yearly_breakdown += activation_breakdown - removal_breakdown

    def update_curr_month (self, new_month: int) -> None:
        removal_breakdown = self.update_metric(self.monthly_balances, new_month)
        activation_breakdown = self.update_metric(self.inactive_monthly_balances, new_month)

        self.monthly_breakdown += activation_breakdown - removal_breakdown

    def update_status (self, total_breakdown: FinancialBreakdown) -> None:
        self.payment_size -= total_breakdown.payment
        self.investment_size += total_breakdown.investment

        self.total_breakdown = total_breakdown

    def make_yearly_payment (self, investment_percentage: float) -> None:
        self.investment_size -= self.investment_size * investment_percentage

    def copy (self) -> "PaymentStatus":
        return PaymentStatus(
            payment_size=self.payment_size,
            investment_size=self.investment_size,
            monthly_balances=self.monthly_balances.copy(),
            yearly_balances=self.yearly_balances.copy(),
            inactive_monthly_balances=self.inactive_monthly_balances.copy(),
            inactive_yearly_balances=self.inactive_yearly_balances.copy(),
        )
