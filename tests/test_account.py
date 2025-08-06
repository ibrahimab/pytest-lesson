from bank.account import BankAccount

def test_new_account_has_zero_balance() -> None:
    account = BankAccount(name="Alice")
    assert account.get_balance() == 0.0