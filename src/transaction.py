"""
Transaction Class for Financial Tracker ~ Uzzam Tariq
Course: INST326 Section 0302

This module defines the Transaction class which represents a single
financial transaction in the financial tracker system.
"""

from datetime import datetime
from typing import Optional
import sys
sys.path.append('.')
from src.library_name import (
    validate_transaction_amount,
    validate_date_format,
    validate_category,
    validate_transaction_data
)


class Transaction:
    """
    Represents a single financial transaction.
    
    A transaction records a financial event such as a purchase, payment,
    deposit, or withdrawal. It includes validation to ensure data integrity
    and methods to analyze and display transaction information.
    
    Attributes:
        transaction_id (str): Unique identifier for the transaction
        amount (float): Transaction amount (always positive)
        date (str): Date in YYYY-MM-DD format
        category (str): Transaction category (e.g., 'Subscription', 'Food')
        description (str): Optional description of the transaction
        account_id (str): Identifier for the associated account
        transaction_type (str): Either 'debit' (expense) or 'credit' (income)
    
    Examples:
        >>> # Create a subscription transaction
        >>> netflix = Transaction(
        ...     transaction_id="TXN001",
        ...     amount=15.99,
        ...     date="2025-10-15",
        ...     category="Subscription",
        ...     description="Netflix Premium",
        ...     account_id="ACC001",
        ...     transaction_type="debit"
        ... )
        >>> print(netflix)
        2025-10-15: -$15.99 - Subscription (Netflix Premium)
        
        >>> # Create an income transaction
        >>> salary = Transaction(
        ...     transaction_id="TXN002",
        ...     amount=3000.00,
        ...     date="2025-10-01",
        ...     category="Income",
        ...     account_id="ACC001",
        ...     transaction_type="credit"
        ... )
        >>> print(salary)
        2025-10-01: +$3000.00 - Income
    """
    
    # Class variable to track total number of transactions created
    _transaction_count = 0
    
    def __init__(
        self,
        transaction_id: str,
        amount: float,
        date: str,
        category: str,
        account_id: str,
        transaction_type: str = "debit",
        description: str = ""
    ):
        """
        Initialize a new Transaction object.
        
        Args:
            transaction_id (str): Unique identifier for the transaction
            amount (float): Transaction amount (must be positive)
            date (str): Date in YYYY-MM-DD format
            category (str): Transaction category
            account_id (str): Associated account identifier
            transaction_type (str): 'debit' (expense) or 'credit' (income)
            description (str): Optional transaction description
            
        Raises:
            ValueError: If any validation fails
            TypeError: If parameters are wrong type
            
        Examples:
            >>> txn = Transaction("T1", 50.00, "2025-10-15", "Food", "A1")
            >>> txn.amount
            50.0
        """
        # Validate transaction_id
        if not isinstance(transaction_id, str):
            raise TypeError("Transaction ID must be a string")
        if not transaction_id.strip():
            raise ValueError("Transaction ID cannot be empty")
        
        # Validate amount using Project 1 function
        if not validate_transaction_amount(amount):
            raise ValueError(
                f"Invalid amount: {amount}. Must be positive and less than $1,000,000"
            )
        
        # Validate date using Project 1 function
        if not validate_date_format(date):
            raise ValueError(
                f"Invalid date: {date}. Must be in YYYY-MM-DD format and not in future"
            )
        
        # Validate category using Project 1 function
        if not validate_category(category, allow_custom=True):
            raise ValueError(f"Invalid category: {category}")
        
        # Validate account_id
        if not isinstance(account_id, str):
            raise TypeError("Account ID must be a string")
        if not account_id.strip():
            raise ValueError("Account ID cannot be empty")
        
        # Validate transaction_type
        if transaction_type not in ['debit', 'credit']:
            raise ValueError("Transaction type must be 'debit' or 'credit'")
        
        # Validate description (optional)
        if description and not isinstance(description, str):
            raise TypeError("Description must be a string")
        if len(description) > 500:
            raise ValueError("Description cannot exceed 500 characters")
        
        # If all validations pass, set private attributes
        self._transaction_id = transaction_id
        self._amount = float(amount)
        self._date = date
        self._category = category.strip()
        self._account_id = account_id
        self._transaction_type = transaction_type
        self._description = description.strip()
        
        # Update class counter
        Transaction._transaction_count += 1
    
    # ==================== PROPERTIES (Controlled Access) ====================
    
    @property
    def transaction_id(self) -> str:
        """str: Get the transaction ID (read-only)."""
        return self._transaction_id
    
    @property
    def amount(self) -> float:
        """float: Get the transaction amount (read-only)."""
        return self._amount
    
    @property
    def date(self) -> str:
        """str: Get the transaction date (read-only)."""
        return self._date
    
    @property
    def category(self) -> str:
        """str: Get the transaction category."""
        return self._category
    
    @category.setter
    def category(self, new_category: str):
        """
        Set a new category for the transaction.
        
        Args:
            new_category (str): The new category name
            
        Raises:
            ValueError: If category is invalid
        """
        if not validate_category(new_category, allow_custom=True):
            raise ValueError(f"Invalid category: {new_category}")
        self._category = new_category.strip()
    
    @property
    def description(self) -> str:
        """str: Get the transaction description."""
        return self._description
    
    @description.setter
    def description(self, new_description: str):
        """
        Set a new description for the transaction.
        
        Args:
            new_description (str): The new description
            
        Raises:
            ValueError: If description is too long
            TypeError: If description is not a string
        """
        if not isinstance(new_description, str):
            raise TypeError("Description must be a string")
        if len(new_description) > 500:
            raise ValueError("Description cannot exceed 500 characters")
        self._description = new_description.strip()
    
    @property
    def account_id(self) -> str:
        """str: Get the account ID (read-only)."""
        return self._account_id
    
    @property
    def transaction_type(self) -> str:
        """str: Get the transaction type ('debit' or 'credit')."""
        return self._transaction_type
    
    @property
    def signed_amount(self) -> float:
        """
        float: Get the amount with sign based on transaction type.
        
        Returns negative for debits (expenses), positive for credits (income).
        
        Returns:
            float: Signed transaction amount
            
        Examples:
            >>> expense = Transaction("T1", 50, "2025-10-15", "Food", "A1", "debit")
            >>> expense.signed_amount
            -50.0
            >>> income = Transaction("T2", 100, "2025-10-15", "Income", "A1", "credit")
            >>> income.signed_amount
            100.0
        """
        return self._amount if self._transaction_type == 'credit' else -self._amount
    
    # ==================== INSTANCE METHODS ====================
    
    def to_dict(self) -> dict:
        """
        Convert transaction to dictionary format.
        
        Returns:
            dict: Dictionary representation of the transaction
            
        Examples:
            >>> txn = Transaction("T1", 50, "2025-10-15", "Food", "A1")
            >>> data = txn.to_dict()
            >>> data['amount']
            50.0
        """
        return {
            'transaction_id': self._transaction_id,
            'amount': self._amount,
            'date': self._date,
            'category': self._category,
            'description': self._description,
            'account_id': self._account_id,
            'transaction_type': self._transaction_type
        }
    
    def is_expense(self) -> bool:
        """
        Check if this is an expense transaction.
        
        Returns:
            bool: True if transaction is a debit (expense)
            
        Examples:
            >>> expense = Transaction("T1", 50, "2025-10-15", "Food", "A1", "debit")
            >>> expense.is_expense()
            True
            >>> income = Transaction("T2", 100, "2025-10-15", "Income", "A1", "credit")
            >>> income.is_expense()
            False
        """
        return self._transaction_type == 'debit'
    
    def is_income(self) -> bool:
        """
        Check if this is an income transaction.
        
        Returns:
            bool: True if transaction is a credit (income)
        """
        return self._transaction_type == 'credit'
    
    def matches_category(self, category: str) -> bool:
        """
        Check if transaction matches a given category (case-insensitive).
        
        Args:
            category (str): Category to check against
            
        Returns:
            bool: True if categories match
            
        Examples:
            >>> txn = Transaction("T1", 50, "2025-10-15", "Food", "A1")
            >>> txn.matches_category("food")
            True
            >>> txn.matches_category("FOOD")
            True
            >>> txn.matches_category("Entertainment")
            False
        """
        return self._category.lower() == category.lower()
    
    def is_small_transaction(self, threshold: float = 50.0) -> bool:
        """
        Check if transaction is below a threshold amount.
        
        Args:
            threshold (float): Amount threshold (default: $50)
            
        Returns:
            bool: True if amount is less than threshold
            
        Examples:
            >>> small = Transaction("T1", 25, "2025-10-15", "Food", "A1")
            >>> small.is_small_transaction()
            True
            >>> large = Transaction("T2", 100, "2025-10-15", "Food", "A1")
            >>> large.is_small_transaction()
            False
        """
        return self._amount < threshold
    
    def get_month_year(self) -> tuple:
        """
        Extract month and year from transaction date.
        
        Returns:
            tuple: (year, month) as integers
            
        Examples:
            >>> txn = Transaction("T1", 50, "2025-10-15", "Food", "A1")
            >>> txn.get_month_year()
            (2025, 10)
        """
        date_obj = datetime.strptime(self._date, "%Y-%m-%d")
        return (date_obj.year, date_obj.month)
    
    # ==================== SPECIAL METHODS ====================
    
    def __str__(self) -> str:
        """
        Return user-friendly string representation.
        
        Returns:
            str: Formatted transaction string
            
        Examples:
            >>> txn = Transaction("T1", 50, "2025-10-15", "Food", "A1", "debit", "Lunch")
            >>> str(txn)
            '2025-10-15: -$50.00 - Food (Lunch)'
        """
        sign = '+' if self._transaction_type == 'credit' else '-'
        desc = f" ({self._description})" if self._description else ""
        return f"{self._date}: {sign}${self._amount:.2f} - {self._category}{desc}"
    
    def __repr__(self) -> str:
        """
        Return developer-friendly string representation.
        
        Returns:
            str: Detailed transaction representation
            
        Examples:
            >>> txn = Transaction("T1", 50, "2025-10-15", "Food", "A1")
            >>> repr(txn)
            "Transaction(id='T1', amount=50.0, date='2025-10-15', category='Food', type='debit')"
        """
        return (
            f"Transaction(id='{self._transaction_id}', "
            f"amount={self._amount}, date='{self._date}', "
            f"category='{self._category}', type='{self._transaction_type}')"
        )
    
    def __eq__(self, other) -> bool:
        """
        Check equality based on transaction ID.
        
        Args:
            other: Another Transaction object
            
        Returns:
            bool: True if transaction IDs match
        """
        if not isinstance(other, Transaction):
            return False
        return self._transaction_id == other._transaction_id
    
    def __lt__(self, other) -> bool:
        """
        Compare transactions by date for sorting.
        
        Args:
            other: Another Transaction object
            
        Returns:
            bool: True if this transaction is earlier
            
        Examples:
            >>> txn1 = Transaction("T1", 50, "2025-10-15", "Food", "A1")
            >>> txn2 = Transaction("T2", 100, "2025-10-20", "Food", "A1")
            >>> txn1 < txn2
            True
        """
        if not isinstance(other, Transaction):
            return NotImplemented
        return self._date < other._date
    
    # ==================== CLASS METHODS ====================
    
    @classmethod
    def get_transaction_count(cls) -> int:
        """
        Get total number of transactions created.
        
        Returns:
            int: Total transaction count
            
        Examples:
            >>> count_before = Transaction.get_transaction_count()
            >>> txn = Transaction("T1", 50, "2025-10-15", "Food", "A1")
            >>> Transaction.get_transaction_count() == count_before + 1
            True
        """
        return cls._transaction_count
    
    @classmethod
    def from_dict(cls, data: dict):
        """
        Create a Transaction object from a dictionary.
        
        Args:
            data (dict): Dictionary with transaction data
            
        Returns:
            Transaction: New Transaction object
            
        Raises:
            KeyError: If required keys are missing
            
        Examples:
            >>> data = {
            ...     'transaction_id': 'T1',
            ...     'amount': 50.0,
            ...     'date': '2025-10-15',
            ...     'category': 'Food',
            ...     'account_id': 'A1',
            ...     'transaction_type': 'debit',
            ...     'description': 'Lunch'
            ... }
            >>> txn = Transaction.from_dict(data)
            >>> txn.amount
            50.0
        """
        return cls(
            transaction_id=data['transaction_id'],
            amount=data['amount'],
            date=data['date'],
            category=data['category'],
            account_id=data['account_id'],
            transaction_type=data.get('transaction_type', 'debit'),
            description=data.get('description', '')
        )



