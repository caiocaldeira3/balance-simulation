import argparse
from datetime import datetime
from dateutil.relativedelta import relativedelta

import config
from structs.balance import Balance, SpreadType
from structs.payment import PaymentStatus
from balance_handler import BalanceHandler, read_balance

def parse_arguments():
    parser = argparse.ArgumentParser(description="Expense Manager")

    parser.add_argument('--init', action='store_true', help='Initialize the balance file')
    parser.add_argument('-a', type=int, help='Add `a` balance(s)')
    parser.add_argument('-u', type=int, help='Update `u` balance(s)')
    parser.add_argument('-d', type=int, help='Delete `d` balance(s)')

    return parser.parse_args()

def simulate_payment (
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

        if simulation[-1].payment_size >= payment_status.payment_size:
            return simulation

        curr_date = curr_date + relativedelta(months=1)
        month_it += 1

if __name__ == "__main__":
    args = parse_arguments()

    handler = BalanceHandler()

    handler.add_balances([ read_balance() for _ in range(args.a or 0) ])
    handler.update_balances_by_id([ read_balance() for _ in range(args.u or 0) ])
    handler.remove_balances_by_id([ input("expense_id: ") for _ in range(args.d or 0) ])

    # print(simulate_payment(config.DEBIT_SIZE, config.INVESTMENT_SIZE))

