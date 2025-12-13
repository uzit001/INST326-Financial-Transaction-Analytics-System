"""
Abstract Account Base Class - Project 3
Author: Team (Uzzam)
Course: INST326 Section 0302

This module defines the abstract base class for all account types,
enforcing a common interface while allowing specialized implementations.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List


class Account(ABC):
    """
    Abstract base class for all financial accounts.
    
    This class defines the common interface that ALL account types must
    implement. Subclasses MUST override the abstract methods to provide
    specialized behavior.
    
    Attributes:
        account_id (str): Unique identifier
        account_name (str): Display name
        owner (str): Account owner's name
        balance (float): Current balance (calculated from transactions)
    
    Abstract Methods (must be implemented by subclasses):
        calculate_available_funds(): Calculate spendable amount
        apply_monthly_fees(): Apply fees or interest
        can_withdraw(): Check if transaction is allowed
    
    Examples:
        # Cannot instantiate abstract class:
        >>> account = Account("ACC001", "Test", "Uzzam")
        TypeError: Can't instantiate abstract class Account
        
        # Must use concrete subclass:
        >>> checking = CheckingAccount("ACC001", "Checking", "Uzzam")
        >>> print(checking.calculate_available_funds())
        1200.00
    """
    
    def __init__(self, account_id: str, account_name: str, owner: str):
        """
        Initialize common account attributes.
        
        Args:
            account_id: Unique identifier (e.g., "ACC001")
            account_name: Display name (e.g., "Main Checking")
            owner: Account owner's name
            
        Raises:
            ValueError: If any parameter is empty or invalid
        """
        # Validation
        if not account_id or not account_id.strip():
            raise ValueError("Account ID cannot be empty")
        if not account_name or not account_name.strip():
            raise ValueError("Account name cannot be empty")
        if not owner or not owner.strip():
            raise ValueError("Owner name cannot be empty")
        
        # Set protected attributes (subclasses can access)
        self._account_id = account_id.strip()
        self._account_name = account_name.strip()
        self._owner = owner.strip()
        self._transactions: List = []
        self._created_date = datetime.now()
    
    # ══════════════════════════════════════════════════════════════════════
    # ABSTRACT METHODS - Subclasses MUST implement
    # ══════════════════════════════════════════════════════════════════════
    
    @abstractmethod
    def calculate_available_funds(self) -> float:
        """
        Calculate how much money is available to spend/withdraw right now.
        
        This is a POLYMORPHIC method - each account type calculates
        differently based on its rules:
        
        - CheckingAccount: balance + overdraft protection
        - SavingsAccount: balance - required minimum balance
        - CreditCardAccount: credit_limit - current_balance
        
        Returns:
            float: Amount available to use
            
        Examples:
            >>> checking = CheckingAccount("ACC001", "Checking", "Uzzam", 
            ...                            overdraft_limit=500)
            >>> checking.calculate_available_funds()
            1200.00  # $700 balance + $500 overdraft
            
            >>> savings = SavingsAccount("ACC002", "Savings", "Uzzam",
            ...                         minimum_balance=100)
            >>> savings.calculate_available_funds()
            900.00  # $1000 balance - $100 minimum
        """
        pass
    
    @abstractmethod
    def apply_monthly_fees(self) -> float:
        """
        Calculate and apply monthly fees or interest charges.
        
        This is a POLYMORPHIC method - each account handles fees differently:
        
        - CheckingAccount: May charge monthly maintenance fee
        - SavingsAccount: EARNS interest (returns negative = money earned)
        - CreditCardAccount: CHARGES interest on unpaid balance
        
        Returns:
            float: Amount charged (positive) or earned (negative)
                  Positive = you PAY this amount
                  Negative = you EARN this amount
                  Zero = no fees or interest
                  
        Examples:
            >>> checking = CheckingAccount("ACC001", "Checking", "Uzzam")
            >>> checking.apply_monthly_fees()
            10.00  # $10 monthly fee
            
            >>> savings = SavingsAccount("ACC002", "Savings", "Uzzam",
            ...                         interest_rate=0.02)
            >>> savings.apply_monthly_fees()
            -8.33  # Earned $8.33 interest (negative = earned!)
            
            >>> visa = CreditCardAccount("ACC003", "Visa", "Uzzam")
            >>> visa.apply_monthly_fees()
            25.00  # $25 interest charge on unpaid balance
        """
        pass
    
    @abstractmethod
    def can_withdraw(self, amount: float) -> tuple[bool, str]:
        """
        Check if a withdrawal or charge is allowed for this account.
        
        This is a POLYMORPHIC method - each account has different rules:
        
        - CheckingAccount: Check against balance + overdraft
        - SavingsAccount: Check balance AND monthly withdrawal limit
        - CreditCardAccount: Check against available credit
        
        Args:
            amount: Amount to withdraw or charge
            
        Returns:
            tuple: (allowed, reason)
                - allowed (bool): True if transaction is allowed
                - reason (str): Empty if allowed, explanation if not
                
        Examples:
            >>> checking = CheckingAccount("ACC001", "Checking", "Uzzam")
            >>> can_withdraw, reason = checking.can_withdraw(500)
            >>> can_withdraw
            True
            
            >>> can_withdraw, reason = checking.can_withdraw(5000)
            >>> can_withdraw
            False
            >>> reason
            'Insufficient funds. Available: $1200.00'
        """
        pass
    
    # ══════════════════════════════════════════════════════════════════════
    # PROPERTIES - Common to all accounts
    # ══════════════════════════════════════════════════════════════════════
    
    @property
    def account_id(self) -> str:
        """str: Get account ID (read-only)."""
        return self._account_id
    
    @property
    def account_name(self) -> str:
        """str: Get account name (read-only)."""
        return self._account_name
    
    @property
    def owner(self) -> str:
        """str: Get owner name (read-only)."""
        return self._owner
    
    @property
    def created_date(self) -> datetime:
        """datetime: Get creation date (read-only)."""
        return self._created_date
    
    @property
    def balance(self) -> float:
        """
        float: Calculate current balance from transactions.
        
        Default implementation sums all transaction amounts.
        Subclasses can override for specialized behavior
        (e.g., CreditCardAccount calculates debt differently).
        
        Returns:
            float: Current balance
        """
        total = 0
        for txn in self._transactions:
            # Use signed_amount: negative for expenses, positive for income
            total += txn.signed_amount
        return total
    
    @property
    def transaction_count(self) -> int:
        """int: Get number of transactions."""
        return len(self._transactions)
    
    # ══════════════════════════════════════════════════════════════════════
    # CONCRETE METHODS - Inherited by all subclasses
    # ══════════════════════════════════════════════════════════════════════
    
    def add_transaction(self, transaction) -> None:
        """
        Add a transaction to this account.
        
        Subclasses can override to add specialized validation
        (e.g., SavingsAccount checks withdrawal limits).
        
        Args:
            transaction: Transaction object to add
            
        Raises:
            ValueError: If transaction doesn't belong to this account
        """
        # Verify transaction belongs to this account
        if transaction.account_id != self._account_id:
            raise ValueError(
                f"Transaction {transaction.transaction_id} belongs to "
                f"account {transaction.account_id}, not {self._account_id}"
            )
        
        self._transactions.append(transaction)
    
    def get_transactions(self) -> List:
        """
        Get all transactions for this account.
        
        Returns:
            List: Copy of transaction list (to prevent external modification)
        """
        return self._transactions.copy()
    
    def get_transactions_by_date_range(self, start_date: str, 
                                      end_date: str) -> List:
        """
        Get transactions within a date range.
        
        Args:
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            
        Returns:
            List: Transactions within date range
            
        Example:
            >>> txns = account.get_transactions_by_date_range(
            ...     "2025-10-01", "2025-10-31"
            ... )
            >>> len(txns)
            15
        """
        return [
            txn for txn in self._transactions
            if start_date <= txn.date <= end_date
        ]
    
    def generate_statement(self) -> str:
        """
        Generate a simple account statement.
        
        Returns:
            str: Formatted statement
        """
        statement = [
            "=" * 60,
            f"Account Statement: {self._account_name}",
            f"Owner: {self._owner}",
            f"Account ID: {self._account_id}",
            "=" * 60,
            f"Current Balance: ${self.balance:.2f}",
            f"Available Funds: ${self.calculate_available_funds():.2f}",
            f"Total Transactions: {self.transaction_count}",
            "=" * 60,
        ]
        
        if self._transactions:
            statement.append("\nRecent Transactions:")
            statement.append("-" * 60)
            for txn in self._transactions[-10:]:  # Last 10 transactions
                statement.append(str(txn))
        
        return "\n".join(statement)
    
    # ══════════════════════════════════════════════════════════════════════
    # SPECIAL METHODS
    # ══════════════════════════════════════════════════════════════════════
    
    def __str__(self) -> str:
        """
        User-friendly string representation.
        
        Returns:
            str: Formatted string
            
        Example:
            >>> str(account)
            'Main Checking (ACC001): $2,500.00'
        """
        return (f"{self._account_name} ({self._account_id}): "
                f"${self.balance:,.2f}")
    
    def __repr__(self) -> str:
        """
        Developer-friendly string representation.
        
        Returns:
            str: Detailed representation
            
        Example:
            >>> repr(account)
            "Account(id='ACC001', name='Main Checking', owner='Uzzam')"
        """
        return (f"Account(id='{self._account_id}', "
                f"name='{self._account_name}', "
                f"owner='{self._owner}')")
    
    def __eq__(self, other) -> bool:
        """
        Check equality based on account ID.
        
        Args:
            other: Another object to compare
            
        Returns:
            bool: True if account IDs match
        """
        if not isinstance(other, Account):
            return False
        return self._account_id == other._account_id
    
    def __lt__(self, other) -> bool:
        """
        Compare accounts by balance for sorting.
        
        Args:
            other: Another Account object
            
        Returns:
            bool: True if this account has lower balance
        """
        if not isinstance(other, Account):
            return NotImplemented
        return self.balance < other.balance


# ══════════════════════════════════════════════════════════════════════════
# DEMONSTRATION - Shows abstract class cannot be instantiated
# ══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("Abstract Base Class Demonstration")
    print("=" * 70)
    
    print("\nAttempting to instantiate abstract Account class...")
    try:
        # This will FAIL because Account is abstract
        account = Account("ACC001", "Test Account", "Uzzam")
        print("ERROR: Should not be able to create Account!")
    except TypeError as e:
        print(f"✓ Correctly prevented instantiation:")
        print(f"  {e}")
    
    print("\n" + "=" * 70)
    print("Key Points:")
    print("=" * 70)
    print("""
1. Account is an ABSTRACT base class (ABC)
2. Cannot instantiate Account directly
3. Must create CheckingAccount, SavingsAccount, or CreditCardAccount
4. All subclasses MUST implement:
   - calculate_available_funds()
   - apply_monthly_fees()
   - can_withdraw()
5. Subclasses inherit common methods:
   - add_transaction()
   - get_transactions()
   - generate_statement()
6. This enforces a common interface while allowing specialization
    """)
    
    print("\n" + "=" * 70)
    print("Next Steps:")
    print("=" * 70)
    print("""
1. Create CheckingAccount class that inherits from Account
2. Implement the three abstract methods
3. Add CheckingAccount-specific features (overdraft, checks)
4. Test that polymorphism works correctly
    """)
    
 
 
# ══════════════════════════════════════════════════════════════════════════
# COMPOSITION 1: Account ◆─── TransactionHistory
# An account OWNS its transaction history. If the account is deleted,
# the history goes with it. The history cannot exist independently.
# ══════════════════════════════════════════════════════════════════════════
   
class TransactionHistory:
    """
    Manages the complete transaction record for an account.
    
    This is a COMPOSITION relationship:
    - Created and owned by a single Account
    - Cannot exist without its parent Account
    - Destroyed when the Account is destroyed
    
    Provides filtering, searching, and analytics on transactions.
    """
    
    def __init__(self, account_id: str):
        self._account_id = account_id
        self._transactions: List = []
        self._created_at = datetime.now()
    
    def add(self, transaction) -> None:
        """Add a transaction to history."""
        self._transactions.append(transaction)
    
    def get_all(self) -> List:
        """Return copy of all transactions."""
        return self._transactions.copy()
    
    def get_by_date_range(self, start: str, end: str) -> List:
        """Filter transactions by date range (YYYY-MM-DD)."""
        return [t for t in self._transactions if start <= t.date <= end]
    
    def get_by_category(self, category: str) -> List:
        """Filter transactions by category."""
        return [t for t in self._transactions 
                if getattr(t, 'category', None) == category]
    
    def get_by_amount_range(self, min_amt: float, max_amt: float) -> List:
        """Filter transactions by amount range."""
        return [t for t in self._transactions 
                if min_amt <= abs(t.amount) <= max_amt]
    
    def calculate_total_income(self) -> float:
        """Sum of all positive transactions."""
        return sum(t.signed_amount for t in self._transactions 
                   if t.signed_amount > 0)
    
    def calculate_total_expenses(self) -> float:
        """Sum of all negative transactions (returned as positive)."""
        return abs(sum(t.signed_amount for t in self._transactions 
                       if t.signed_amount < 0))
    
    def get_monthly_summary(self, year: int, month: int) -> dict:
        """Generate summary for a specific month."""
        month_str = f"{year}-{month:02d}"
        monthly_txns = [t for t in self._transactions 
                        if t.date.startswith(month_str)]
        
        income = sum(t.signed_amount for t in monthly_txns if t.signed_amount > 0)
        expenses = abs(sum(t.signed_amount for t in monthly_txns if t.signed_amount < 0))
        
        return {
            "month": month_str,
            "transaction_count": len(monthly_txns),
            "total_income": income,
            "total_expenses": expenses,
            "net": income - expenses
        }
    
    def __len__(self) -> int:
        return len(self._transactions)
    
    def __repr__(self) -> str:
        return f"TransactionHistory(account={self._account_id}, count={len(self)})"



