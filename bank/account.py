# bank/account.py

from typing import List, Literal, TypedDict

TransactionType = Literal["deposit", "withdraw", "transfer_out", "transfer_in"]

class Transaction(TypedDict):
    type: TransactionType
    amount: float
    balance_after: float
    note: str

class BankAccount:
    def __init__(self, name: str) -> None:
        self._balance: float = 0.0
        self._frozen: bool = False
        self._name: str = name
        self._history: List[Transaction] = []

    def deposit(self, amount: float) -> None:
        self._require_not_frozen()
        if amount <= 0:
            raise ValueError("Deposit must be positive.")
        self._balance += amount
        self._log_transaction("deposit", amount, "Deposit successful")

    def withdraw(self, amount: float) -> None:
        self._require_not_frozen()
        if amount <= 0:
            raise ValueError("Withdraw must be positive.")
        if amount > self._balance:
            raise ValueError("Insufficient funds.")
        self._balance -= amount
        self._log_transaction("withdraw", amount, "Withdrawal successful")

    def transfer(self, target: "BankAccount", amount: float) -> None:
        self._require_not_frozen()
        if target.is_frozen():
            raise ValueError("Target account is frozen.")
        if amount <= 0:
            raise ValueError("Transfer amount must be positive.")
        if amount > self._balance:
            raise ValueError("Insufficient funds.")
        self._balance -= amount
        target._balance += amount
        self._log_transaction("transfer_out", amount, f"Transferred to {target._name}")
        target._log_transaction("transfer_in", amount, f"Received from {self._name}")

    def freeze(self) -> None:
        self._frozen = True

    def unfreeze(self) -> None:
        self._frozen = False

    def is_frozen(self) -> bool:
        return self._frozen

    def get_balance(self) -> float:
        return self._balance

    def get_transaction_history(self) -> List[Transaction]:
        return self._history.copy()

    def _log_transaction(self, type_: TransactionType, amount: float, note: str) -> None:
        self._history.append({
            "type": type_,
            "amount": amount,
            "balance_after": self._balance,
            "note": note,
        })

    def _require_not_frozen(self) -> None:
        if self._frozen:
            raise ValueError("Account is frozen.")
