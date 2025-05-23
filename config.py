import os
from typing import Final


BALANCE_FILE_PATH: Final = os.getenv("BALANCE_FILE_PATH", "balance.csv")

# DEBIT VARIABLES
DEBIT_SIZE: float = float(os.getenv("DEBIT_SIZE", 0))

# CREDIT VARIABLES
INVESTMENT_SIZE: float = float(os.getenv("INVESTMENT_SIZE", 0))
INVESTMENT_INTERST_RATE: float = float(os.getenv("INVESTMENT_INTEREST_RATE", 0))
PAYMENT_INTEREST_RATE: float = float(os.getenv("PAYMENT_INTEREST_RATE", 0))
