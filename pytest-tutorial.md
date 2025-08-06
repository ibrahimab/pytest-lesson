# 🧪 Pytest Tutorial — Testing a Realistic `BankAccount` Class

This is a **narrative-based**, **demo-heavy**, and **pragmatic** Pytest tutorial built around a realistic Python class: `BankAccount`.

We’re not doing TDD — instead, we’ll write tests *after* implementing each method, just like most real projects. Our goal is deep behavioral coverage, not theoretical purity.

Each lesson includes:

- ✅ A narrative explanation of what we’re testing and why it matters
- ✅ Fully type-hinted test code
- ✅ A step-by-step walk through edge cases and side effects
- ✅ Clean project structure and repeatable `uv` workflows

---

## 🗂 Project Structure

This is how your files should be organized:

```
project/
├── bank/
│   └── account.py          # The BankAccount class implementation
├── tests/
│   └── test_account.py     # All test cases
├── pyproject.toml          # Dependency declaration
├── uv.lock                 # Auto-generated lock file
└── .python-version         # Python version hint for uv (e.g. 3.10)
```

We keep source code (`bank/`) separate from tests (`tests/`) — a good habit that mimics real projects.

---

## ⚙️ Environment Setup with `uv`

We use [`uv`](https://github.com/astral-sh/uv) to manage dependencies and virtual environments — no `.venv`, no activation steps.

### 📌 Step 1: Install `uv` (once)

```bash
curl -Ls https://astral.sh/uv/install.sh | sh
```

---

### 📌 Step 2: Define Python version

Create a `.python-version` file in your project root:

```
3.10
```

This tells `uv` which Python version to use.

---

### 📌 Step 3: Create `pyproject.toml`

```toml
[project]
name = "bankaccount"
version = "0.0.1"
dependencies = ["pytest"]
requires-python = ">= 3.10"

[tool.pytest.ini_options]
pythonpath = ["."]
```

You can add more dependencies here later — `uv` will handle locking and syncing.

---

### 📌 Step 4: Sync dependencies

```bash
uv sync
```

This installs everything from `pyproject.toml`, generates a `uv.lock`, and ensures repeatability.

---

## ▶️ Running Tests

Once tests are written, run them with:

```bash
uv run pytest
```

No need to activate anything — `uv` handles it all.

---

You’re now ready to write your `BankAccount` class and begin testing.

```python
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

```

## 🧪 Test 1: A new account starts with a balance of 0.0

Before testing deposits, withdrawals, or any features at all, we should verify one critical default behavior:

> ✅ When you create a new account, it should have a balance of `0.0`.

This might seem obvious — but it's also the kind of assumption that breaks silently if logic changes (e.g., adding a welcome bonus later).

```python
from bank.account import BankAccount

def test_new_account_has_zero_balance() -> None:
    account = BankAccount(name="Alice")
    assert account.get_balance() == 0.0
```

### 💬 What’s happening here?

- We instantiate a `BankAccount` with the name `"Alice"`.
- We call `get_balance()` to retrieve the current balance.
- We assert that it’s exactly `0.0`.

Even though this test is simple, it establishes a **baseline invariant** — the account must start empty. Future tests will assume this, so it's important to lock it down now.

## 🧪 Test 2: Depositing money increases the balance

Now that we’ve confirmed a new account starts with a balance of 0.0, it’s time to test a real-world action: depositing money.

This is the most fundamental operation in the lifecycle of a bank account — so we want to ensure:

- It works with expected values (like 100.0)
- The balance reflects the deposit
- No rounding, delay, or caching bugs exist

```python
from bank.account import BankAccount

def test_deposit_increases_balance() -> None:
    account = BankAccount(name="Alice")
    account.deposit(100.0)
    assert account.get_balance() == 100.0
```

### 💬 What this does

- We create a `BankAccount` named `"Alice"`.
- We deposit 100.0 units of currency.
- We check that `get_balance()` now returns `100.0`.

If this test fails, the `deposit()` method may not be correctly updating internal state — or `get_balance()` isn’t returning what we think it should.

🔍 **Pro tip**: By asserting against *exact* floats like `100.0`, we’re also implicitly verifying that no unintended precision issues exist here.

## 🧪 Test 3: Multiple deposits accumulate correctly

In real usage, a user will likely make multiple deposits over time. This test verifies that:

- The `deposit()` method **adds** to the existing balance
- It does **not overwrite**, reset, or miscalculate the total

```python
from bank.account import BankAccount

def test_multiple_deposits_accumulate() -> None:
    account = BankAccount(name="Alice")
    account.deposit(50.0)
    account.deposit(75.0)
    assert account.get_balance() == 125.0
```

### 💬 Explanation

- We make two deposits: 50.0 and 75.0
- The resulting balance should be the **sum**: 125.0
- We’re checking that the `deposit()` method doesn’t replace the previous balance, but **adds to it cumulatively**

🧠 This test protects against a common bug: accidentally reassigning `self._balance = amount` instead of `+= amount`.

## 🧪 Test 4: Withdrawing money decreases the balance

Withdrawing funds is a core operation, and we want to confirm that:

- Withdrawals reduce the balance
- The amount withdrawn is correctly subtracted
- The account remains accurate after the operation

```python
from bank.account import BankAccount

def test_withdraw_reduces_balance() -> None:
    account = BankAccount(name="Alice")
    account.deposit(200.0)
    account.withdraw(75.0)
    assert account.get_balance() == 125.0
```

### 💬 Explanation

- We first deposit 200.0 to ensure sufficient balance
- Then we withdraw 75.0
- We check that the final balance is `125.0` — the result of `200.0 - 75.0`

📌 This test is important because it involves **state mutation** — if `withdraw()` modifies the balance incorrectly (or not at all), this test will catch it.

💡 Also note: We’re not checking for overdraft or negative values here — that will come next. This test assumes a legal, valid withdrawal.

## 🧪 Test 5: Withdrawing more than the balance raises an error

An account should not allow you to withdraw more money than it holds — unless it supports overdraft, which ours doesn’t.

This test verifies that:

- Attempting to overdraw the account raises a `ValueError`
- The error message contains useful information (e.g. “Insufficient funds”)
- The balance remains unchanged

```python
import pytest
from bank.account import BankAccount

def test_withdraw_more_than_balance_raises() -> None:
    account = BankAccount(name="Alice")
    account.deposit(50.0)

    with pytest.raises(ValueError, match="Insufficient funds"):
        account.withdraw(100.0)

    assert account.get_balance() == 50.0
```

### 💬 Explanation

- We deposit 50.0 and then try to withdraw 100.0 — which should fail
- The test uses `pytest.raises()` to catch the `ValueError`
- We also assert that the balance hasn’t changed as a result of the failed operation

🧠 This is a **behavioral safeguard**. Even though the exception is expected, we’re also checking that the internal state is not corrupted by the failed attempt.

## 🧪 Test 6: Withdrawing zero or negative amounts raises an error

It should not be possible to withdraw `0.0`, `-1.0`, or any other non-positive amount. These aren’t valid operations in a real banking system, and our code should enforce that rule clearly.

We’ll use `pytest.mark.parametrize` to test multiple invalid values in one go.

```python
import pytest
from bank.account import BankAccount

@pytest.mark.parametrize("amount", [0.0, -1.0, -50.0])
def test_invalid_withdrawal_amounts_raise(amount: float) -> None:
    account = BankAccount(name="Alice")
    account.deposit(100.0)

    with pytest.raises(ValueError, match="positive"):
        account.withdraw(amount)

    assert account.get_balance() == 100.0
```

### 💬 Explanation

- We deposit 100.0 up front so we can focus solely on invalid input
- We test multiple bad values using `@pytest.mark.parametrize`
- In each case, we expect a `ValueError` with a message that mentions “positive”
- After the attempt, we confirm that the balance is **unchanged**

📌 This test protects against:
- Silent errors (e.g. withdrawing zero and getting no feedback)
- Logic holes that accidentally allow negative values to *add* to the balance
- Hidden state corruption after failed operations

## 🧪 Test 7: Depositing zero or negative amounts raises an error

Just like with withdrawals, deposits must be **strictly positive**. Accepting zero or negative amounts could lead to all kinds of logic errors, not to mention abuse in real systems.

Let’s test that these cases are handled properly.

```python
import pytest
from bank.account import BankAccount

@pytest.mark.parametrize("amount", [0.0, -5.0, -999.99])
def test_invalid_deposit_amounts_raise(amount: float) -> None:
    account = BankAccount(name="Alice")

    with pytest.raises(ValueError, match="positive"):
        account.deposit(amount)

    assert account.get_balance() == 0.0
```

### 💬 Explanation

- We don’t deposit anything valid first — the account starts at 0.0
- Each bad value is passed through `deposit()`, expecting a `ValueError`
- We check that the balance is still `0.0` after the failed attempt

This is essential for catching:
- Incorrect logic like `if amount < 0:` (should be `<= 0`)
- Future changes that might loosen validation unintentionally

✅ Validating input strictly = trustable core logic.

## 🧪 Test 8: Using a fixture for a funded account

So far, we’ve been writing:

```python
account = BankAccount(name="Alice")
account.deposit(100.0)
```

in almost every test. That works — but it’s repetitive, cluttered, and fragile if the setup ever changes.

Enter: `pytest` fixtures.

We’ll define a **reusable funded account fixture** that gives us a preloaded account with 100.0 in balance.

```python
import pytest
from bank.account import BankAccount

@pytest.fixture
def funded_account() -> BankAccount:
    account = BankAccount(name="Alice")
    account.deposit(100.0)
    return account
```

Now we can write tests like this:

```python
def test_withdraw_from_funded_account(funded_account: BankAccount) -> None:
    funded_account.withdraw(40.0)
    assert funded_account.get_balance() == 60.0
```

### 💬 Explanation

- The `@pytest.fixture` decorator tells Pytest to treat `funded_account()` as a reusable setup block
- Any test that has `funded_account` as a parameter will **automatically receive** the return value of that function
- It keeps tests focused on intent — e.g., “withdraw 40” — not on boilerplate

🔁 If you later decide that funded accounts should start with 500.0 instead of 100.0, you can just update the fixture — all dependent tests will adjust automatically.

🧠 Use fixtures for any repeated setup across multiple tests — not just objects, but even complex prep logic.

## 🧪 Test 9: Withdrawing from a frozen account raises an error

In our extended `BankAccount` class, an account can be “frozen.” This simulates a security lock or regulatory hold — any withdrawal or deposit during that time should be blocked.

Let’s test what happens when a withdrawal is attempted on a frozen account.

```python
import pytest
from bank.account import BankAccount

def test_cannot_withdraw_when_frozen() -> None:
    account = BankAccount(name="Alice")
    account.deposit(100.0)
    account.freeze()

    with pytest.raises(ValueError, match="frozen"):
        account.withdraw(50.0)

    assert account.get_balance() == 100.0
```

### 💬 Explanation

- We start by depositing 100.0 to ensure a legal withdrawal would normally succeed
- We then call `freeze()`, which should lock the account
- The attempt to withdraw should raise a `ValueError` — ideally with a helpful message
- We also confirm that the balance **did not change** despite the failed withdrawal

🔒 This test ensures our account is correctly enforcing **state-based access rules** — something you’ll see in all real systems with user roles, security locks, or flags.


## 🧪 Test 10: Depositing into a frozen account raises an error

Just like withdrawals, deposits should also be blocked when an account is frozen. This ensures consistency: the user can’t interact with the balance at all while the account is in a locked state.

```python
import pytest
from bank.account import BankAccount

def test_cannot_deposit_when_frozen() -> None:
    account = BankAccount(name="Alice")
    account.freeze()

    with pytest.raises(ValueError, match="frozen"):
        account.deposit(50.0)

    assert account.get_balance() == 0.0
```

### 💬 Explanation

- The account is frozen immediately, with no prior deposits
- A deposit attempt is made, which should raise `ValueError`
- We verify that the balance remains at `0.0` — no funds were added

🔍 This guards against any logic that might accidentally let a frozen account receive money — for example, during a race condition, concurrent transaction, or admin override.

By explicitly asserting **no balance change**, we catch state mutations even when exceptions are correctly raised.

## 🧪 Test 11: Transferring money between two accounts

The `transfer()` method is a major feature: it moves funds from one account to another.

This test verifies that:

- Money is deducted from the sender’s balance
- Money is added to the recipient’s balance
- Both accounts update their internal state accordingly

```python
from bank.account import BankAccount

def test_transfer_between_accounts_updates_both() -> None:
    alice = BankAccount(name="Alice")
    bob = BankAccount(name="Bob")

    alice.deposit(200.0)
    alice.transfer(bob, 75.0)

    assert alice.get_balance() == 125.0
    assert bob.get_balance() == 75.0
```

### 💬 Explanation

- We give Alice a balance of 200.0
- She transfers 75.0 to Bob
- We assert that Alice now has 125.0, and Bob has 75.0
- There are no exceptions, and the balances reflect the operation

This test proves that `transfer()` correctly mutates the state of **two separate objects** — not just one.

📌 Transferring between objects is where bugs like:
- partial state updates
- mismatched totals
- double-counting  
tend to happen — so this test is essential.


## 🧪 Test 12: Transferring more than available balance raises an error

Just like with withdrawals, transfers should be **blocked** if the sender tries to send more money than they currently have.

This test ensures:

- The transfer fails safely
- The balances of both accounts remain unchanged

```python
import pytest
from bank.account import BankAccount

def test_transfer_more_than_balance_raises() -> None:
    alice = BankAccount(name="Alice")
    bob = BankAccount(name="Bob")

    alice.deposit(50.0)

    with pytest.raises(ValueError, match="Insufficient funds"):
        alice.transfer(bob, 100.0)

    assert alice.get_balance() == 50.0
    assert bob.get_balance() == 0.0
```

### 💬 Explanation

- Alice has 50.0
- She attempts to transfer 100.0 to Bob — this should raise a `ValueError`
- We confirm that **neither** account’s balance was changed after the failed attempt

🧠 This test ensures that `transfer()` is **transactional** — it doesn’t make a partial change (e.g., subtract from Alice but fail to credit Bob).

You should treat operations like this as **atomic**: either they succeed completely, or they fail cleanly.

## 🧪 Test 13: Transferring to a frozen account raises an error

Even if the sender has funds and isn’t frozen, a transfer should still **fail** if the recipient account is frozen. Why?

> A frozen account should not be able to receive money — just like it can’t send or modify it.

```python
import pytest
from bank.account import BankAccount

def test_transfer_to_frozen_account_raises() -> None:
    alice = BankAccount(name="Alice")
    bob = BankAccount(name="Bob")

    alice.deposit(100.0)
    bob.freeze()

    with pytest.raises(ValueError, match="frozen"):
        alice.transfer(bob, 50.0)

    assert alice.get_balance() == 100.0
    assert bob.get_balance() == 0.0
```

### 💬 Explanation

- Alice has 100.0 and is allowed to send
- Bob is frozen, and **should not** be allowed to receive funds
- The transfer attempt raises a `ValueError`
- The balances of both accounts remain unchanged

📌 This test ensures that the **target account’s state** is validated inside `transfer()` — a common oversight in multi-object operations.

🧠 Good defensive logic means *all* participants are validated, not just the initiator.

## 🧪 Test 14: Deposits are recorded in transaction history

The `BankAccount` class maintains a transaction log via `get_transaction_history()`.

Let’s verify that depositing funds adds a properly structured record to that history.

```python
from bank.account import BankAccount

def test_deposit_creates_history_entry() -> None:
    account = BankAccount(name="Alice")
    account.deposit(100.0)

    history = account.get_transaction_history()
    assert len(history) == 1

    entry = history[0]
    assert entry["type"] == "deposit"
    assert entry["amount"] == 100.0
    assert entry["balance_after"] == 100.0
    assert "Deposit successful" in entry["note"]
```

### 💬 Explanation

- We perform a single deposit of 100.0
- We check that the history has **one entry**
- We then inspect the entry’s fields:
  - `"type"` is `"deposit"`
  - `"amount"` is accurate
  - `"balance_after"` reflects post-operation balance
  - `"note"` is human-readable and informative

🧠 This test confirms that every meaningful financial event is:
- Recorded
- Accurate
- Structured for downstream use (e.g. audit, reporting, user interfaces)

Up next, we’ll do the same for **withdrawals**, then test **transfers** (which generate logs in **both** sender and recipient accounts).

## 🧪 Test 15: Withdrawals are recorded in transaction history

Any money movement should be auditable — and that includes money going out. This test ensures that a `withdraw()` call creates a correct history entry.

```python
from bank.account import BankAccount

def test_withdraw_creates_history_entry() -> None:
    account = BankAccount(name="Alice")
    account.deposit(200.0)
    account.withdraw(75.0)

    history = account.get_transaction_history()
    assert len(history) == 2  # 1 deposit + 1 withdrawal

    withdraw_entry = history[1]
    assert withdraw_entry["type"] == "withdraw"
    assert withdraw_entry["amount"] == 75.0
    assert withdraw_entry["balance_after"] == 125.0
    assert "Withdrawal successful" in withdraw_entry["note"]
```

### 💬 Explanation

- We deposit 200.0 and then withdraw 75.0
- We expect two log entries in total
- We assert that the second one (`history[1]`) accurately describes the withdrawal

🧠 This test also ensures that:
- Entries are **in order** — we’re testing not just correctness, but **sequence**
- The history log reflects **post-action state**, not just the event itself

Up next, we’ll test **transfers**, which generate **two entries**: one for sender (`transfer_out`), and one for recipient (`transfer_in`).

## 🧪 Test 16: Transfers are logged in both sender and recipient history

Transfers affect two accounts, and **both should keep a record** — the sender logs a `transfer_out`, the recipient logs a `transfer_in`.

We’ll test that:

- Two accounts reflect the transfer in their own histories
- The entries are accurate and traceable
- The post-transfer balances are correct

```python
from bank.account import BankAccount

def test_transfer_creates_history_for_both_accounts() -> None:
    alice = BankAccount(name="Alice")
    bob = BankAccount(name="Bob")

    alice.deposit(150.0)
    alice.transfer(bob, 40.0)

    alice_history = alice.get_transaction_history()
    bob_history = bob.get_transaction_history()

    # Alice's history
    assert len(alice_history) == 2
    assert alice_history[1]["type"] == "transfer_out"
    assert alice_history[1]["amount"] == 40.0
    assert alice_history[1]["balance_after"] == 110.0
    assert "Transferred to Bob" in alice_history[1]["note"]

    # Bob's history
    assert len(bob_history) == 1
    assert bob_history[0]["type"] == "transfer_in"
    assert bob_history[0]["amount"] == 40.0
    assert bob_history[0]["balance_after"] == 40.0
    assert "Received from Alice" in bob_history[0]["note"]
```

### 💬 Explanation

- We deposit into Alice, then transfer to Bob
- We check **both** histories independently:
  - Alice logs a `transfer_out`
  - Bob logs a `transfer_in`
- Notes include references to the other party
- Balances after each event are correct

🧠 This test gives you confidence in:
- Bidirectional correctness
- Traceability (human-readable notes)
- Internal consistency across objects

✅ You now have complete behavioral coverage of all core `BankAccount+++` features.

## 🧪 Test 17: Using `conftest.py` to centralize fixtures

When you start using the same fixture in multiple test files — or want to share reusable test utilities across your suite — you should extract those fixtures into a special file:

```
tests/
├── conftest.py
├── test_account.py
```

This file is automatically discovered by `pytest`, and you don’t need to import anything from it.

---

### 🧱 Create `tests/conftest.py`

Here’s how we move our funded account fixture into `conftest.py`:

```python
# tests/conftest.py

import pytest
from bank.account import BankAccount

@pytest.fixture
def funded_account() -> BankAccount:
    account = BankAccount(name="Alice")
    account.deposit(100.0)
    return account
```

You can now delete this fixture from `test_account.py`.

---

### ✅ Reuse it like before

Even though the fixture now lives in a separate file, nothing changes about how you use it:

```python
def test_withdraw_from_funded_account(funded_account: BankAccount) -> None:
    funded_account.withdraw(25.0)
    assert funded_account.get_balance() == 75.0
```

---

### 💬 Why this matters

- You can define any number of shared fixtures, utilities, or plugins in `conftest.py`
- Pytest will automatically detect and inject them based on function arguments
- You avoid polluting test files with duplicated setup logic

🧠 Pro tip: Only put **reused**, **clean**, and **non-test-specific** helpers in `conftest.py`. If a fixture only makes sense for one test module, leave it there.

## 🧪 Test 18: Parameterized fixture in `conftest.py`

Sometimes you want to run the *same test* against accounts with different initial balances. You could parametrize the test itself — but if you need **customized setup logic** per value (e.g. different names, rules, or logging), a **parameterized fixture** is a cleaner approach.

Let’s build a fixture that gives us accounts with 0.0, 100.0, and 250.0 starting balances.

---

### 🧱 Add to `tests/conftest.py`

```python
# tests/conftest.py

import pytest
from bank.account import BankAccount

@pytest.fixture(params=[0.0, 100.0, 250.0])
def varied_account(request: pytest.FixtureRequest) -> BankAccount:
    balance: float = request.param
    account = BankAccount(name=f"TestUser{int(balance)}")
    if balance > 0.0:
        account.deposit(balance)
    return account
```

- `params=[...]` defines which values to loop over
- `request.param` is set to one of those values for each test run
- You can do *custom logic* depending on the param

---

### ✅ Example usage in a test

```python
def test_varied_account_initial_balances(varied_account: BankAccount) -> None:
    assert varied_account.get_balance() in [0.0, 100.0, 250.0]
```

### 💬 What this gives you

- The test runs **three times**, once for each configured balance
- Each time it uses a **fully initialized `BankAccount`** object
- You get the benefits of parametrization *without* stuffing all the logic into the test itself

🧠 Use parameterized fixtures when:
- You need *stateful setup* per parameter
- You want to test behavior across a range of inputs
- You want clean, reusable patterns for real-world testing

