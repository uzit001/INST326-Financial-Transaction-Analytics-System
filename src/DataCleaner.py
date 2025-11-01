#Kevin Miele
from typing import Any, Dict, Iterable, List, Optional

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
        """Apply `normalize_date_format` to each stored row.

        Returns:
          int: Count of rows successfully normalized.

        Raises:
          `normalize_date_format`: If a date is missing or formatted incorrectly.


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
        """Apply `clean_transaction_description` to each stored row.

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
        """Apply `standardize_category_names` to each stored row.

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
        """Remove exact duplicates using `remove_duplicate_transactions`.

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
