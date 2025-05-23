import pprint
import matplotlib.pyplot as plt
from datetime import datetime
from dateutil.relativedelta import relativedelta

import config
from structs.balance import Balance
from structs.payment import PaymentStatus
from balance_handler import BalanceHandler


def get_payment_status_list (
    handler: BalanceHandler, payment_size: float, investment_size: float, *,
    initial_payment: float = 0, profit_tax: float = 0.0,
    investment_yearly_percentage: float = 0,
) -> list[PaymentStatus]:
    monthly_balances = handler.df[handler.monthly_balances_flag]
    yearly_balances = handler.df[handler.yearly_balances_flag]
    inactive_monthly_balances = handler.df[handler.inactive_monthly_balances_flag]
    inactive_yearly_balances = handler.df[handler.inactive_yearly_balances_flag]

    payment_status = PaymentStatus(
        payment_size=payment_size - initial_payment,
        investment_size=investment_size - initial_payment,
        monthly_balances=[Balance(**row) for row in monthly_balances.to_dict(orient="records")],
        yearly_balances=[Balance(**row) for row in yearly_balances.to_dict(orient="records")],
        inactive_monthly_balances=[Balance(**row) for row in inactive_monthly_balances.to_dict(orient="records")],
        inactive_yearly_balances=[Balance(**row) for row in inactive_yearly_balances.to_dict(orient="records")],
    )

    simulation = [payment_status.copy()]

    month_it = 0
    year_it = 0
    curr_date = datetime.now()
    while payment_status.payment_size > 0:
        payment_status.payment_size += payment_status.payment_size * config.PAYMENT_INTEREST_RATE
        investment_earnings = (
            payment_status.investment_size * config.INVESTMENT_INTERST_RATE
        )

        payment_status.update_curr_month(month_it)

        month_breakdown = payment_status.monthly_breakdown.copy()

        if curr_date.month == 12:
            month_breakdown += payment_status.yearly_breakdown
            payment_status.make_yearly_payment(investment_yearly_percentage)

            year_it += 1
            payment_status.update_curr_year(year_it)

        month_breakdown.debit += (investment_earnings + month_breakdown.credit) * profit_tax
        month_breakdown.investment += investment_earnings

        payment_status.update_status(month_breakdown)
        simulation.append(payment_status.copy())

        if simulation[-2].payment_size <= payment_status.payment_size:
            break

        curr_date = curr_date + relativedelta(months=1)
        month_it += 1

    return simulation

def get_payment_simulation_plot (
    handler: BalanceHandler, payment_size: float, investment_size: float, *,
    initial_payment: float = 0, profit_tax: float = 0.0,
    investment_yearly_percentage: float = 0,
) -> plt.Figure:
    payment_status = get_payment_status_list(
        handler, payment_size, investment_size,
        initial_payment=initial_payment,
        profit_tax=profit_tax,
        investment_yearly_percentage=investment_yearly_percentage,
    )

    # pp = pprint.PrettyPrinter(indent=2)
    # # Convert each payment status to a dictionary for easier reading
    # pretty_list = [s.__dict__ for s in payment_status]
    # pp.pprint(pretty_list)

    months = list(range(len(payment_status)))
    payments = [s.payment_size for s in payment_status]
    investments = [s.investment_size for s in payment_status]
    net_credits = [s.total_breakdown.extra_credit for s in payment_status]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(months, payments, label="Pagamento", marker='o')
    ax.plot(months, investments, label="Investimento", marker='o')
    ax.plot(months, net_credits, label="Crédito Líquido", marker='o', linestyle='--')
    ax.set_xlabel("Mês")
    ax.set_ylabel("Valor")
    ax.set_title("Evolução do Pagamento, Investimento e Crédito Líquido ao Longo do Tempo")
    ax.legend()
    ax.grid(True)
    fig.tight_layout()

    return fig

if __name__ == "__main__":
    handler = BalanceHandler()
    fig = get_payment_simulation_plot(
        handler, config.DEBIT_SIZE, config.INVESTMENT_SIZE,
        initial_payment=0.0,
        profit_tax=0.0,
        investment_yearly_percentage=0.0,
    )
    fig.show()

    input()
