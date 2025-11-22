#Kevin Miele
from typing import Any, Dict, Iterable, List, Optional
from abc import ABC, abstractmethod

class TransactionCleaner:

  """
    This class uses the four data-cleaning functions:
    - normalize_date_format(row)
    - clean_transaction_description(row)
    - standardize_category_names(row)
    - remove_duplicate_transactions(rows)

    Attributes:
      (private) _transactions: List[Dict[str, Any]]

    Example:
      >>> rows = [
      ...   {"Date":"9/1/2025","Amount":"9.99","Description":"Spotify #123","category":"subscr","account":"visa"},
      ...   {"date":"2025-09-01","amount":9.99,"description":"Spotify","category":"Subscription","account":"Visa"},
      ... ]
      >>> tc = TransactionCleaner(rows)
      >>> tc.clean_all()             # normalize dates, clean descriptions, standardize categories, removing duplicates
      1
      >>> tc.transactions[0]["date"]
      '2025-09-01'
      >>> tc.transactions[0]["description"]
      'Spotify'
      >>> tc.transactions[0]["category"]
      'Subscription'
    """


    # Initialization
    def __init__(self, rows: Optional[Iterable[Dict[str, Any]]] = None) -> None:
        """Initialize the cleaner

        Args:
          rows: Optional set of transactions, each stored as a dictionary.

        Raises:
          TypeError: If rows can’t be looped through or has items that aren’t dictionaries.

        """
        self._transactions: List[Dict[str, Any]] = []
        if rows is not None:
            if not hasattr(rows, "__iter__"):
                raise TypeError("rows must be an iterable of dicts or None")
            for idx, r in enumerate(rows):
                if not isinstance(r, dict):
                    raise TypeError(f"rows[{idx}] must be a dict")
                # Store a copy
                self._transactions.append(dict(r))

    @property
    def transactions(self) -> List[Dict[str, Any]]:
        """Return a copy of the current transactions (read-only view)."""
        return [dict(r) for r in self._transactions]

    @property
    def size(self) -> int:
        """Number of transactions currently stored."""
        return len(self._transactions)

    
    # Core cleaning methods                 
    def normalize_dates(self) -> int:
        """Apply normalize_date_format to each stored row.

        Returns:
          int: Count of rows successfully normalized.

        Raises:
          normalize_date_format: If a date is missing or formatted incorrectly.


        Example:
          >>> tc = TransactionCleaner([{"Date":"10/11/2025"}])
          >>> tc.normalize_dates()
          1
          >>> tc.transactions[0]["date"]
          '2025-10-11'
        """
        count = 0
        new_rows: List[Dict[str, Any]] = []
        for r in self._transactions:
            nr = normalize_date_format(r)
            new_rows.append(nr)
            count += 1
        self._transactions = new_rows
        return count

    def clean_descriptions(self) -> int:
        """Apply clean_transaction_description to each stored row.

        Returns:
          int: Count of rows successfully cleaned.

        Example:
          >>> tc = TransactionCleaner([{"description":"Starbucks TRN0001"}])
          >>> tc.clean_descriptions()
          1
          >>> tc.transactions[0]["description"]
          'Starbucks'
        """
        count = 0
        new_rows: List[Dict[str, Any]] = []
        for r in self._transactions:
            nr = clean_transaction_description(r)
            new_rows.append(nr)
            count += 1
        self._transactions = new_rows
        return count

    def standardize_categories(self) -> int:
        """Apply standardize_category_names to each stored row.

        Returns:
          int: Count of rows successfully standardized.

        Example:
          >>> tc = TransactionCleaner([{"category":"subscr"}])
          >>> tc.standardize_categories()
          1
          >>> tc.transactions[0]["category"]
          'Subscription'
        """
        count = 0
        new_rows: List[Dict[str, Any]] = []
        for r in self._transactions:
            nr = standardize_category_names(r)
            new_rows.append(nr)
            count += 1
        self._transactions = new_rows
        return count

    def deduplicate(self) -> int:
        """Remove exact duplicates using remove_duplicate_transactions.

        Returns:
          int: Number of rows removed as duplicates.

        Example:
          >>> rows = [
          ...   {"date":"2025-09-03","amount":"25.00","description":"Amazon","category":"Shopping","account":"Checking"},
          ...   {"date":"2025-09-03","amount":25.0,"description":"Amazon","category":"Shopping","account":"checking"},
          ... ]
          >>> tc = TransactionCleaner(rows)
          >>> removed = tc.deduplicate()
          >>> removed
          1
          >>> tc.size
          1
        """
        before = len(self._transactions)
        self._transactions = remove_duplicate_transactions(self._transactions)
        after = len(self._transactions)
        return before - after

    def clean_all(self) -> int:
        """Run in order:
        1) normalize_dates → 2) clean_descriptions → 3) standardize_categories → 4) deduplicate

        Returns:
          int: Number of duplicates removed at the final step.

        Notes:
        - If something goes wrong, the error will stop the process.
        - After cleaning, all transactions will use the same key names:
          'date', 'description', and 'category', along with the original fields 
          like 'amount' and 'account'.

        Example:
          >>> rows = [
          ...   {"Date":"9/1/2025","Amount":"9.99","Description":"Spotify #123","category":"subscr","account":"visa"},
          ...   {"date":"2025-09-01","amount":9.99,"description":"Spotify","category":"Subscription","account":"Visa"},
          ... ]
          >>> tc = TransactionCleaner(rows)
          >>> tc.clean_all()
          1
          >>> tc.size
          1
        """
        self.normalize_dates()
        self.clean_descriptions()
        self.standardize_categories()
        removed = self.deduplicate()
        return removed

    # String representations
    def __str__(self) -> str:
        """Readable summary with basic inventory."""
        n = self.size
        sample_dates = [r.get("date", r.get("Date")) for r in self._transactions[:3]]
        return f"TransactionCleaner(size={n}, sample_dates={sample_dates})"

    def __repr__(self) -> str:
        """Class name and size."""
        return f"{self.__class__.__name__}(rows={self.size})"

###Project 3 Addition###
class AlertRule(ABC):
    """Abstract base class for different alert rules on transactions."""

    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def check(self, tx: Dict[str, Any]) -> Optional[str]:
        """
        Inspect a single transaction.
        Return:
          - str message if the rule is triggered
          - None if everything is fine
        """
        raise NotImplementedError

    def describe(self) -> str:
        """Non-abstract method that subclasses can extend with super()."""
        return f"Rule: {self.name}"
####################################################################################
class LargeTransactionRule(AlertRule):
    """Flags transactions above a certain amount."""

    def __init__(self, threshold: float = 1000.0) -> None:
        super().__init__("Large Transaction")  # uses super()
        self.threshold = threshold

    def describe(self) -> str:
        base = super().describe()  # method overriding + super()
        return f"{base} (threshold ≥ {self.threshold:.2f})"

    def check(self, tx: Dict[str, Any]) -> Optional[str]:
        amount_raw = tx.get("amount")
        try:
            amount = float(amount_raw)
        except (TypeError, ValueError):
            return None  # can't interpret amount, silently skip

        if amount >= self.threshold:
            return (
                f"{self.name}: ${amount:.2f} on {tx.get('date')} "
                f"at {tx.get('description', 'Unknown merchant')}"
            )
        return None
#####################################################################################
class CategoryLimitRule(AlertRule):
    """
    Flags a single transaction that exceeds a per-transaction
    limit for a specific category (e.g. Dining > $100).
    """

    def __init__(self, category: str, per_tx_limit: float) -> None:
        name = f"{category} per-transaction limit"
        super().__init__(name)  # uses super()
        self.category = category
        self.per_tx_limit = per_tx_limit

    def check(self, tx: Dict[str, Any]) -> Optional[str]:
        tx_category = tx.get("category")
        if tx_category != self.category:
            return None

        amount_raw = tx.get("amount")
        try:
            amount = float(amount_raw)
        except (TypeError, ValueError):
            return None

        if amount > self.per_tx_limit:
            return (
                f"{self.name} exceeded: ${amount:.2f} on {tx.get('date')} "
                f"({tx.get('description', 'Unknown merchant')})"
            )
        return None
########################################################################################
class SuspiciousMerchantRule(AlertRule):
    """
    Flags transactions whose description contains any suspicious keyword.
    Example keywords: ['UNKNOWN', 'MONEY TRANSFER', 'CASH APP']
    """

    def __init__(self, suspicious_keywords: List[str]) -> None:
        super().__init__("Suspicious merchant/description")
        # normalize keywords to lowercase for case-insensitive matching
        self.suspicious_keywords = [kw.lower() for kw in suspicious_keywords]

    def check(self, tx: Dict[str, Any]) -> Optional[str]:
        desc = (tx.get("description") or "").lower()
        for kw in self.suspicious_keywords:
            if kw in desc:
                return (
                    f"{self.name}: matched '{kw}' in '{tx.get('description')}' "
                    f"on {tx.get('date')}"
                )
        return None
##########################################################################################
class StatementMonitor:
    """
    High-level object that:
      - owns a TransactionCleaner (composition)
      - owns multiple AlertRule instances (composition)
      - runs data cleaning, then applies all rules polymorphically
    """

    def __init__(
        self,
        rows: Iterable[Dict[str, Any]],
        rules: Optional[List[AlertRule]] = None,
    ) -> None:
        # Composition: StatementMonitor has-a TransactionCleaner
        self._cleaner = TransactionCleaner(rows)

        # Composition: StatementMonitor has-a collection of AlertRule objects
        if rules is None:
            self._rules: List[AlertRule] = [
                LargeTransactionRule(threshold=500.0),
                CategoryLimitRule("Dining", per_tx_limit=120.0),
                SuspiciousMerchantRule(["unknown", "cash app", "money transfer"]),
            ]
        else:
            self._rules = rules

    @property
    def cleaner(self) -> TransactionCleaner:
        """Expose the cleaner (read-only reference)."""
        return self._cleaner

    @property
    def rules(self) -> List[AlertRule]:
        """Expose the list of rules so caller can add/remove them."""
        return list(self._rules)

    def run_full_analysis(self) -> List[str]:
        """
        Clean all transactions and apply all alert rules.

        Returns:
          List of alert messages generated by all rules.
        """
        # Clean the data
        self._cleaner.clean_all()

        alerts: List[str] = []
        # Polymorphism: every rule has a check(tx) method, but behavior differs
        for tx in self._cleaner.transactions:
            for rule in self._rules:
                msg = rule.check(tx)   # same call, different subclass behavior
                if msg is not None:
                    alerts.append(msg)
        return alerts

############################DEMO#####################################################
if __name__ == "__main__":
    sample_rows = [
        {
            "Date": "9/1/2025",
            "Amount": "600.00",
            "Description": "DINING - Olive Garden #1234",
            "category": "Dining",
            "account": "Visa",
        },
        {
            "date": "2025-09-02",
            "amount": 50.0,
            "description": "Grocery Store",
            "category": "Groceries",
            "account": "Checking",
        },
        {
            "Date": "9/3/2025",
            "Amount": "1500",
            "Description": "UNKNOWN MONEY TRANSFER",
            "category": "Other",
            "account": "Checking",
        },
    ]

    monitor = StatementMonitor(sample_rows)
    alerts = monitor.run_full_analysis()

    print("=== Rules in this monitor ===")
    for r in monitor.rules:
        print(" -", r.describe())

    print("\n=== Alerts ===")
    for a in alerts:
        print(a)

