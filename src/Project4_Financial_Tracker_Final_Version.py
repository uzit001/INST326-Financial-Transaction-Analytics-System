"""
Project 4 Financial Tracker (Fixed + CSV Compatible)
Combined single-file program with:
- Accounts (Account ABC, CheckingAccount, SavingsAccount, CreditAccount)
- Transactions + validation
- TransactionCleaner + StatementMonitor alert rules
- CSV loader + insight reporting

Compatible with the sample statement.csv columns:
Date,Amount,Description,Category,Account
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Union, Tuple
import csv
import os
import re

# =============================================================================
# VALIDATION FUNCTIONS (from your Project work, preserved)
# =============================================================================

def validate_transaction_amount(amount: Union[int, float]) -> bool:
    """
    Validate that a transaction amount is positive and within reasonable bounds.
    """
    if not isinstance(amount, (int, float)):
        raise TypeError(f"Amount must be a number, got {type(amount).__name__}")
    if amount <= 0:
        return False
    if amount > 1_000_000:
        return False
    return True


def validate_date_format(date_str: str) -> bool:
    """
    Validate date is in YYYY-MM-DD format and not in the future.
    """
    if not isinstance(date_str, str):
        raise TypeError("Date must be a string")

    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return False

    # not in the future (local time)
    today = datetime.now().date()
    return dt.date() <= today


def validate_category(category: str, allow_custom: bool = True) -> bool:
    """
    Validate category string (allows custom by default).
    """
    if not isinstance(category, str):
        return False
    cat = category.strip()
    if not cat:
        return False
    # If you want to restrict categories, do it here when allow_custom=False
    return True


def validate_transaction_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate an incoming transaction dict. Returns (is_valid, errors).
    """
    errors: List[str] = []

    # Required fields
    required = ["amount", "date", "category", "account_id"]
    for field in required:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    if "amount" in data:
        try:
            ok = validate_transaction_amount(float(data["amount"]))
            if not ok:
                errors.append("Amount must be > 0 and <= 1,000,000")
        except Exception as e:
            errors.append(str(e))

    if "date" in data:
        try:
            if not validate_date_format(str(data["date"])):
                errors.append("Date must be YYYY-MM-DD and not in the future")
        except Exception as e:
            errors.append(str(e))

    if "category" in data:
        if not validate_category(str(data["category"]), allow_custom=True):
            errors.append("Category cannot be empty")

    if "account_id" in data:
        acct = str(data["account_id"]).strip()
        if not acct:
            errors.append("Account cannot be empty")

    if "description" in data and data["description"] is not None:
        desc = str(data["description"])
        if len(desc) > 500:
            errors.append("Description max 500 characters")

    return (len(errors) == 0, errors)

# =============================================================================
# TRANSACTION
# =============================================================================

class Transaction:
    """
    Represents a single financial transaction.

    Note: amount is ALWAYS stored as a positive float.
          signed_amount gives + for credit and - for debit.
    """

    _transaction_count = 0

    def __init__(
        self,
        transaction_id: str,
        amount: float,
        date: str,
        category: str,
        account_id: str,
        transaction_type: str = "debit",
        description: str = "",
    ):
        if not isinstance(transaction_id, str) or not transaction_id.strip():
            raise ValueError("Transaction ID cannot be empty")

        if not validate_transaction_amount(amount):
            raise ValueError(f"Invalid amount: {amount}")

        if not validate_date_format(date):
            raise ValueError(f"Invalid date: {date}")

        if not validate_category(category, allow_custom=True):
            raise ValueError(f"Invalid category: {category}")

        if not isinstance(account_id, str) or not account_id.strip():
            raise ValueError("Account ID cannot be empty")

        if transaction_type not in ("debit", "credit"):
            raise ValueError("Transaction type must be 'debit' or 'credit'")

        if description and not isinstance(description, str):
            raise TypeError("Description must be a string")
        if isinstance(description, str) and len(description) > 500:
            raise ValueError("Description cannot exceed 500 characters")

        self._transaction_id = transaction_id.strip()
        self._amount = float(amount)
        self._date = date
        self._category = category.strip()
        self._account_id = account_id.strip()
        self._transaction_type = transaction_type
        self._description = (description or "").strip()

        Transaction._transaction_count += 1

    @property
    def transaction_id(self) -> str:
        return self._transaction_id

    @property
    def amount(self) -> float:
        return self._amount

    @property
    def date(self) -> str:
        return self._date

    @property
    def category(self) -> str:
        return self._category

    @property
    def description(self) -> str:
        return self._description

    @property
    def account_id(self) -> str:
        return self._account_id

    @property
    def transaction_type(self) -> str:
        return self._transaction_type

    @property
    def signed_amount(self) -> float:
        return self._amount if self._transaction_type == "credit" else -self._amount

    def __str__(self) -> str:
        sign = "+" if self._transaction_type == "credit" else "-"
        desc = f" ({self._description})" if self._description else ""
        return f"{self._date}: {sign}${self._amount:.2f} - {self._category}{desc}"

# =============================================================================
# ACCOUNT ABC + TransactionHistory (kept simple / compatible)
# =============================================================================

class Account(ABC):
    def __init__(self, account_id: str, account_name: str, owner: str):
        if not account_id or not account_id.strip():
            raise ValueError("Account ID cannot be empty")
        if not account_name or not account_name.strip():
            raise ValueError("Account name cannot be empty")
        if not owner or not owner.strip():
            raise ValueError("Owner name cannot be empty")

        self._account_id = account_id.strip()
        self._account_name = account_name.strip()
        self._owner = owner.strip()
        self._transactions: List[Transaction] = []
        self._created_date = datetime.now()

    @abstractmethod
    def calculate_available_funds(self) -> float:
        raise NotImplementedError

    @abstractmethod
    def apply_monthly_fees(self) -> float:
        raise NotImplementedError

    @abstractmethod
    def can_withdraw(self, amount: float) -> Tuple[bool, str]:
        raise NotImplementedError

    @property
    def account_id(self) -> str:
        return self._account_id

    @property
    def account_name(self) -> str:
        return self._account_name

    @property
    def owner(self) -> str:
        return self._owner

    @property
    def balance(self) -> float:
        return sum(txn.signed_amount for txn in self._transactions)

    def add_transaction(self, transaction: Transaction) -> None:
        if transaction.account_id != self._account_id:
            raise ValueError(
                f"Transaction {transaction.transaction_id} belongs to account "
                f"{transaction.account_id}, not {self._account_id}"
            )
        self._transactions.append(transaction)

    def get_transactions(self) -> List[Transaction]:
        return list(self._transactions)

# =============================================================================
# CHECKING ACCOUNT
# =============================================================================

class CheckingAccount(Account):
    def __init__(
        self,
        account_id: str,
        account_name: str,
        owner: str,
        overdraft_limit: float = 0.0,
        monthly_fee: float = 10.0,
        minimum_balance: float = 500.0,
    ):
        super().__init__(account_id, account_name, owner)
        if overdraft_limit < 0 or monthly_fee < 0 or minimum_balance < 0:
            raise ValueError("Checking parameters cannot be negative")
        self._overdraft_limit = float(overdraft_limit)
        self._monthly_fee = float(monthly_fee)
        self._minimum_balance = float(minimum_balance)

    def calculate_available_funds(self) -> float:
        return self.balance + self._overdraft_limit

    def apply_monthly_fees(self) -> float:
        if self.balance < self._minimum_balance and self._monthly_fee > 0:
            fee_txn = Transaction(
                transaction_id=f"FEE{datetime.now().strftime('%Y%m%d%H%M%S')}",
                amount=self._monthly_fee,
                date=datetime.now().strftime("%Y-%m-%d"),
                category="Bank Fees",
                account_id=self._account_id,
                transaction_type="debit",
                description="Monthly maintenance fee",
            )
            super().add_transaction(fee_txn)
            return self._monthly_fee
        return 0.0

    def can_withdraw(self, amount: float) -> Tuple[bool, str]:
        if amount <= 0:
            return False, "Amount must be positive"
        available = self.calculate_available_funds()
        if amount <= available:
            return True, ""
        return False, f"Insufficient funds. Available: ${available:.2f}"

# =============================================================================
# SAVINGS ACCOUNT
# =============================================================================

class SavingsAccount(Account):
    DEFAULT_INTEREST_RATE = 0.04
    DEFAULT_MINIMUM_BALANCE = 100.0
    DEFAULT_WITHDRAWAL_LIMIT = 6
    DEFAULT_LOW_BALANCE_FEE = 15.0

    def __init__(
        self,
        account_id: str,
        account_name: str,
        owner: str,
        interest_rate: float = DEFAULT_INTEREST_RATE,
        minimum_balance: float = DEFAULT_MINIMUM_BALANCE,
        monthly_withdrawal_limit: int = DEFAULT_WITHDRAWAL_LIMIT,
        low_balance_fee: float = DEFAULT_LOW_BALANCE_FEE,
    ):
        super().__init__(account_id, account_name, owner)
        if interest_rate < 0 or minimum_balance < 0 or monthly_withdrawal_limit < 0 or low_balance_fee < 0:
            raise ValueError("Savings parameters cannot be negative")
        self._interest_rate = float(interest_rate)
        self._minimum_balance = float(minimum_balance)
        self._monthly_withdrawal_limit = int(monthly_withdrawal_limit)
        self._low_balance_fee = float(low_balance_fee)
        self._withdrawal_count_this_month = 0
        self._last_withdrawal_month = None

    def _reset_withdrawal_count_if_new_month(self) -> None:
        current_month = datetime.now().month
        if self._last_withdrawal_month != current_month:
            self._withdrawal_count_this_month = 0

    def calculate_available_funds(self) -> float:
        return max(0.0, self.balance - self._minimum_balance)

    def apply_monthly_fees(self) -> float:
        if self.balance >= self._minimum_balance:
            monthly_interest = self.balance * (self._interest_rate / 12)
            # returning negative to mean "earned"
            return -round(monthly_interest, 2)
        return self._low_balance_fee

    def can_withdraw(self, amount: float) -> Tuple[bool, str]:
        if amount <= 0:
            return False, "Withdrawal amount must be positive"
        self._reset_withdrawal_count_if_new_month()
        if self._withdrawal_count_this_month >= self._monthly_withdrawal_limit:
            return False, f"Monthly withdrawal limit reached ({self._monthly_withdrawal_limit}). Resets next month."
        available = self.calculate_available_funds()
        if amount > available:
            return False, f"Insufficient funds. Available: ${available:,.2f} (${self._minimum_balance:,.2f} minimum required)"
        return True, ""

    def add_transaction(self, transaction: Transaction) -> None:
        # track withdrawals when debit
        if transaction.signed_amount < 0:
            allowed, reason = self.can_withdraw(abs(transaction.signed_amount))
            if not allowed:
                raise ValueError(f"Withdrawal denied: {reason}")
            self._reset_withdrawal_count_if_new_month()
            self._withdrawal_count_this_month += 1
            self._last_withdrawal_month = datetime.now().month
        super().add_transaction(transaction)

# =============================================================================
# CREDIT ACCOUNT (rewritten to fix balance/property issues)
# =============================================================================

class CreditAccount(Account):
    """
    Credit account where negative balance means money owed.

    With transactions:
    - debit transactions (purchases) make balance more negative (owed)
    - credit transactions (payments/refunds) make balance less negative / positive
    """

    def __init__(
        self,
        account_id: str,
        account_name: str,
        owner: str,
        credit_limit: float = 3000.0,
        apr: float = 19.99,
    ):
        super().__init__(account_id, account_name, owner)
        if credit_limit < 0 or apr < 0:
            raise ValueError("Credit limit and APR must be non-negative")
        self._credit_limit = float(credit_limit)
        self._apr = float(apr)
        self._total_interest_charged = 0.0

    @property
    def credit_limit(self) -> float:
        return self._credit_limit

    @property
    def apr(self) -> float:
        return self._apr

    @property
    def total_interest_charged(self) -> float:
        return self._total_interest_charged

    def calculate_available_funds(self) -> float:
        # If balance is -200 (owed), available = limit - 200
        # If balance is +50 (overpaid), available = limit + 50
        if self.balance < 0:
            return max(0.0, self._credit_limit - abs(self.balance))
        return self._credit_limit + self.balance

    def apply_monthly_fees(self) -> float:
        # Charge interest only if money is owed (balance < 0)
        if self.balance >= 0:
            return 0.0
        monthly_rate = self._apr / 100.0 / 12.0
        interest = abs(self.balance) * monthly_rate
        interest = round(interest, 2)
        if interest > 0:
            # Interest increases amount owed => add as a debit transaction
            txn = Transaction(
                transaction_id=f"INT{datetime.now().strftime('%Y%m%d%H%M%S')}",
                amount=interest,
                date=datetime.now().strftime("%Y-%m-%d"),
                category="Interest",
                account_id=self._account_id,
                transaction_type="debit",
                description="Monthly interest charge",
            )
            super().add_transaction(txn)
            self._total_interest_charged += interest
        return interest

    def can_withdraw(self, amount: float) -> Tuple[bool, str]:
        if amount <= 0:
            return False, "Amount must be positive"
        available = self.calculate_available_funds()
        if amount <= available:
            return True, ""
        return False, f"Exceeds credit limit. Available credit: ${available:.2f}"

# =============================================================================
# DATA CLEANER + ALERT RULES
# =============================================================================

def normalize_date_format(row: Dict[str, Any]) -> Dict[str, Any]:
    new_row = dict(row)
    date_value = row.get("date") or row.get("Date")
    if not date_value:
        raise ValueError("Missing date field")

    for fmt in ("%m/%d/%Y", "%Y-%m-%d"):
        try:
            parsed = datetime.strptime(str(date_value), fmt)
            new_row["date"] = parsed.strftime("%Y-%m-%d")
            break
        except ValueError:
            continue
    else:
        raise ValueError(f"Invalid date format: {date_value}")

    # standardize other keys while we're here
    if "amount" not in new_row and "Amount" in new_row:
        new_row["amount"] = new_row["Amount"]
    if "account" not in new_row and "Account" in new_row:
        new_row["account"] = new_row["Account"]
    if "category" not in new_row and "Category" in new_row:
        new_row["category"] = new_row["Category"]
    if "description" not in new_row and "Description" in new_row:
        new_row["description"] = new_row["Description"]

    return new_row


def clean_transaction_description(row: Dict[str, Any]) -> Dict[str, Any]:
    new_row = dict(row)
    desc = row.get("description") or row.get("Description") or ""
    cleaned = re.sub(r"[#A-Z0-9]+$", "", str(desc)).strip()
    new_row["description"] = cleaned
    return new_row


def standardize_category_names(row: Dict[str, Any]) -> Dict[str, Any]:
    new_row = dict(row)
    category_raw = row.get("category") or row.get("Category") or ""
    category = str(category_raw).lower().strip()

    mapping = {
        "subscr": "Subscription",
        "subs": "Subscription",
        "dining": "Dining",
        "food": "Dining",
        "shop": "Shopping",
        "groceries": "Groceries",
        "restaurants": "Dining",
    }
    new_row["category"] = mapping.get(category, category.title() if category else "Other")
    return new_row


def remove_duplicate_transactions(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    unique = []
    for row in rows:
        key = tuple(sorted(row.items()))
        if key not in seen:
            seen.add(key)
            unique.append(row)
    return unique


class TransactionCleaner:
    def __init__(self, rows: Optional[Iterable[Dict[str, Any]]] = None) -> None:
        self._transactions: List[Dict[str, Any]] = []
        if rows is not None:
            if not hasattr(rows, "__iter__"):
                raise TypeError("rows must be an iterable of dicts or None")
            for idx, r in enumerate(rows):
                if not isinstance(r, dict):
                    raise TypeError(f"rows[{idx}] must be a dict")
                self._transactions.append(dict(r))

    @property
    def transactions(self) -> List[Dict[str, Any]]:
        return [dict(r) for r in self._transactions]

    def normalize_dates(self) -> int:
        new_rows = []
        for r in self._transactions:
            new_rows.append(normalize_date_format(r))
        self._transactions = new_rows
        return len(new_rows)

    def clean_descriptions(self) -> int:
        new_rows = []
        for r in self._transactions:
            new_rows.append(clean_transaction_description(r))
        self._transactions = new_rows
        return len(new_rows)

    def standardize_categories(self) -> int:
        new_rows = []
        for r in self._transactions:
            new_rows.append(standardize_category_names(r))
        self._transactions = new_rows
        return len(new_rows)

    def deduplicate(self) -> int:
        before = len(self._transactions)
        self._transactions = remove_duplicate_transactions(self._transactions)
        return before - len(self._transactions)

    def clean_all(self) -> int:
        self.normalize_dates()
        self.clean_descriptions()
        self.standardize_categories()
        return self.deduplicate()


class AlertRule(ABC):
    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def check(self, tx: Dict[str, Any]) -> Optional[str]:
        raise NotImplementedError


class LargeTransactionRule(AlertRule):
    def __init__(self, threshold: float = 1000.0) -> None:
        super().__init__("Large Transaction")
        self.threshold = threshold

    def check(self, tx: Dict[str, Any]) -> Optional[str]:
        amount_raw = tx.get("amount") or tx.get("Amount")
        try:
            amount = abs(float(amount_raw))
        except (TypeError, ValueError):
            return None
        if amount >= self.threshold:
            return f"{self.name}: ${amount:.2f} on {tx.get('date')} at {tx.get('description', 'Unknown')}"
        return None


class CategoryLimitRule(AlertRule):
    def __init__(self, category: str, per_tx_limit: float) -> None:
        super().__init__(f"{category} per-transaction limit")
        self.category = category
        self.per_tx_limit = per_tx_limit

    def check(self, tx: Dict[str, Any]) -> Optional[str]:
        tx_cat = tx.get("category") or tx.get("Category")
        if tx_cat != self.category:
            return None
        amount_raw = tx.get("amount") or tx.get("Amount")
        try:
            amount = abs(float(amount_raw))
        except (TypeError, ValueError):
            return None
        if amount > self.per_tx_limit:
            return f"{self.name} exceeded: ${amount:.2f} on {tx.get('date')} ({tx.get('description', 'Unknown')})"
        return None


class SuspiciousMerchantRule(AlertRule):
    def __init__(self, suspicious_keywords: List[str]) -> None:
        super().__init__("Suspicious merchant/description")
        self.suspicious_keywords = [kw.lower() for kw in suspicious_keywords]

    def check(self, tx: Dict[str, Any]) -> Optional[str]:
        desc = (tx.get("description") or tx.get("Description") or "").lower()
        for kw in self.suspicious_keywords:
            if kw in desc:
                return f"{self.name}: matched '{kw}' in '{tx.get('description') or tx.get('Description')}' on {tx.get('date')}"
        return None


class StatementMonitor:
    def __init__(self, rows: Iterable[Dict[str, Any]], rules: Optional[List[AlertRule]] = None) -> None:
        self._cleaner = TransactionCleaner(rows)
        self._rules = rules or [
            LargeTransactionRule(threshold=500.0),
            CategoryLimitRule("Dining", per_tx_limit=120.0),
            SuspiciousMerchantRule(["unknown", "cash app", "money transfer"]),
        ]

    def run_full_analysis(self) -> List[str]:
        self._cleaner.clean_all()
        alerts: List[str] = []
        for tx in self._cleaner.transactions:
            for rule in self._rules:
                msg = rule.check(tx)
                if msg:
                    alerts.append(msg)
        return alerts

# =============================================================================
# CSV INGESTION + INSIGHTS
# =============================================================================

def load_csv_rows(csv_path: str) -> List[Dict[str, Any]]:
    with open(csv_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def parse_amount(value: Any) -> float:
    s = str(value).replace("$", "").replace(",", "").strip()
    return float(s)


def build_default_accounts(owner: str = "You") -> Dict[str, Account]:
    checking = CheckingAccount("ACC_CHECK", "Checking", owner, overdraft_limit=500)
    savings = SavingsAccount("ACC_SAVE", "Savings", owner, minimum_balance=100)
    credit = CreditAccount("ACC_CREDIT", "Credit", owner, credit_limit=3000, apr=19.99)
    return {"checking": checking, "savings": savings, "credit": credit}


def account_key_from_row(row: Dict[str, Any]) -> str:
    raw = row.get("account") or row.get("Account") or ""
    k = str(raw).strip().lower()
    if "sav" in k:
        return "savings"
    if "cred" in k or "visa" in k or "card" in k:
        return "credit"
    return "checking"


def make_transaction_from_row(row: Dict[str, Any], idx: int, account: Account) -> Transaction:
    # after cleaning, date should be in row["date"]
    date = row.get("date") or row.get("Date")
    desc = row.get("description") or row.get("Description") or ""
    cat = row.get("category") or row.get("Category") or "Other"
    amt_raw = row.get("amount") or row.get("Amount")
    amt_signed = parse_amount(amt_raw)

    # If CSV already uses negative for expenses, keep sign.
    # Determine transaction_type and pass positive amount into Transaction.
    tx_type = "credit" if amt_signed > 0 else "debit"
    amount = abs(amt_signed)

    return Transaction(
        transaction_id=f"TXN{idx:05d}",
        amount=amount,
        date=str(date),
        category=str(cat),
        description=str(desc),
        account_id=account.account_id,
        transaction_type=tx_type,
    )


def compute_insights(accounts: Dict[str, Account]) -> str:
    lines: List[str] = []
    lines.append("=== ACCOUNT BALANCES ===")
    for k, acc in accounts.items():
        lines.append(f"- {acc.account_name} ({acc.account_id}): balance=${acc.balance:,.2f}, available=${acc.calculate_available_funds():,.2f}")

    richest = max(accounts.values(), key=lambda a: a.balance)
    lines.append("\n=== WHICH ACCOUNT HAS THE MOST MONEY? ===")
    lines.append(f"{richest.account_name} has the most: ${richest.balance:,.2f}")

    all_tx: List[Transaction] = []
    for acc in accounts.values():
        all_tx.extend(acc.get_transactions())
    all_tx.sort(key=lambda t: t.date, reverse=True)

    lines.append("\n=== MOST RECENT TRANSACTIONS (TOP 10) ===")
    for t in all_tx[:10]:
        lines.append(str(t))

    inflow = defaultdict(float)
    outflow = defaultdict(float)
    for t in all_tx:
        if t.signed_amount > 0:
            inflow[t.category] += t.signed_amount
        else:
            outflow[t.category] += abs(t.signed_amount)

    lines.append("\n=== WHERE IS MY MONEY COMING FROM? (INFLOWS BY CATEGORY) ===")
    for cat, amt in sorted(inflow.items(), key=lambda x: x[1], reverse=True):
        lines.append(f"- {cat}: ${amt:,.2f}")

    lines.append("\n=== WHERE IS MY MONEY GOING? (OUTFLOWS BY CATEGORY) ===")
    for cat, amt in sorted(outflow.items(), key=lambda x: x[1], reverse=True):
        lines.append(f"- {cat}: ${amt:,.2f}")

    return "\n".join(lines)


def run_from_csv(csv_path: str, owner: str = "You") -> None:
    rows = load_csv_rows(csv_path)

    monitor = StatementMonitor(rows)
    alerts = monitor.run_full_analysis()

    # Use the cleaner's cleaned rows for ingestion
    cleaner = monitor._cleaner  # already created; composition in StatementMonitor
    cleaned = cleaner.transactions

    accounts = build_default_accounts(owner=owner)

    # route + create txns
    for i, row in enumerate(cleaned, start=1):
        key = account_key_from_row(row)
        acc = accounts[key]
        tx = make_transaction_from_row(row, i, acc)
        acc.add_transaction(tx)

    print("\n=== ALERTS (if any) ===")
    if alerts:
        for a in alerts:
            print("-", a)
    else:
        print("No alerts triggered.")

    print()
    print(compute_insights(accounts))


def main():
    csv_path = "statement.csv"
    if os.path.exists(csv_path):
        run_from_csv(csv_path, owner="You")
    else:
        # quick fallback demo dataset (same schema as CSV)
        demo_rows = [
            {"Date": "2025-09-01", "Amount": "2500.00", "Description": "Paycheck - School District", "Category": "Income", "Account": "Checking"},
            {"Date": "2025-09-02", "Amount": "-1200.00", "Description": "September Rent", "Category": "Housing", "Account": "Checking"},
            {"Date": "2025-09-09", "Amount": "-15.50", "Description": "Amazon Purchase", "Category": "Shopping", "Account": "Credit"},
        ]
        # write demo to show flow
        monitor = StatementMonitor(demo_rows)
        alerts = monitor.run_full_analysis()
        accounts = build_default_accounts(owner="You")
        for i, row in enumerate(monitor._cleaner.transactions, start=1):
            key = account_key_from_row(row)
            tx = make_transaction_from_row(row, i, accounts[key])
            accounts[key].add_transaction(tx)
        print("\n=== ALERTS (if any) ===")
        for a in alerts:
            print("-", a)
        print()
        print(compute_insights(accounts))
        print("\nTip: Put 'statement.csv' in the same folder as this script to run on your CSV.")


if __name__ == "__main__":
    main()
