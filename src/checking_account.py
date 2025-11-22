"""
CheckingAccount - Concrete Implementation
Author: Uzzam Tariq
Date: November 2025
Course: INST326 Section 0302

CheckingAccount specializes the Account base class for daily spending
with overdraft protection and check-writing capabilities.
"""

from src.account import Account
from src.transaction import Transaction
from datetime import datetime


class CheckingAccount(Account):
    """
    Checking account for daily spending with overdraft protection.
    
    A checking account allows everyday transactions with the option of
    overdraft protection. Users can write checks, use debit cards, and
    may incur monthly fees if balance falls below minimum.
    
    Attributes:
        overdraft_limit (float): Maximum overdraft allowed
        monthly_fee (float): Fee charged if below minimum balance
        minimum_balance (float): Required balance to avoid fees
        checks_written (list): List of check numbers written
    
    Examples:
        >>> checking = CheckingAccount(
        ...     "ACC001", "Main Checking", "Uzzam",
        ...     overdraft_limit=500, monthly_fee=10
        ... )
        >>> checking.calculate_available_funds()
        500.00  # $0 balance + $500 overdraft
        
        >>> checking.write_check(1001, 250, "Rent")
        >>> checking.balance
        -250.00  # In overdraft
    """
    
    def __init__(self, account_id: str, account_name: str, owner: str,
                 overdraft_limit: float = 0, monthly_fee: float = 10,
                 minimum_balance: float = 500):
        """
        Initialize a checking account.
        
        Args:
            account_id: Unique identifier
            account_name: Display name
            owner: Account owner's name
            overdraft_limit: Maximum overdraft allowed (default: $0)
            monthly_fee: Monthly maintenance fee (default: $10)
            minimum_balance: Balance to avoid fees (default: $500)
            
        Raises:
            ValueError: If overdraft_limit or fees are negative
            
        Examples:
            >>> checking = CheckingAccount("ACC001", "Checking", "Uzzam")
            >>> checking.overdraft_limit
            0
            
            >>> checking2 = CheckingAccount(
            ...     "ACC002", "Premium Checking", "Uzzam",
            ...     overdraft_limit=1000, monthly_fee=0
            ... )
            >>> checking2.overdraft_limit
            1000
        """
        # Call parent constructor
        super().__init__(account_id, account_name, owner)
        
        # Validate checking-specific attributes
        if overdraft_limit < 0:
            raise ValueError("Overdraft limit cannot be negative")
        if monthly_fee < 0:
            raise ValueError("Monthly fee cannot be negative")
        if minimum_balance < 0:
            raise ValueError("Minimum balance cannot be negative")
        
        # Set checking-specific attributes
        self._overdraft_limit = float(overdraft_limit)
        self._monthly_fee = float(monthly_fee)
        self._minimum_balance = float(minimum_balance)
        self._checks_written = []
    
    # ══════════════════════════════════════════════════════════════════════
    # PROPERTIES - CheckingAccount specific
    # ══════════════════════════════════════════════════════════════════════
    
    @property
    def overdraft_limit(self) -> float:
        """float: Get overdraft limit."""
        return self._overdraft_limit
    
    @property
    def monthly_fee(self) -> float:
        """float: Get monthly fee amount."""
        return self._monthly_fee
    
    @property
    def minimum_balance(self) -> float:
        """float: Get minimum balance requirement."""
        return self._minimum_balance
    
    @property
    def checks_written(self) -> list:
        """list: Get list of check numbers written."""
        return self._checks_written.copy()
    
    # ══════════════════════════════════════════════════════════════════════
    # ABSTRACT METHOD IMPLEMENTATIONS (Polymorphic)
    # ══════════════════════════════════════════════════════════════════════
    
    def calculate_available_funds(self) -> float:
        """
        Calculate available funds including overdraft protection.
        
        CheckingAccount calculates available funds as:
        current_balance + overdraft_limit
        
        This allows spending beyond the actual balance up to the
        overdraft limit.
        
        Returns:
            float: Balance plus overdraft limit
            
        Examples:
            >>> checking = CheckingAccount("ACC001", "Checking", "Uzzam",
            ...                            overdraft_limit=500)
            >>> # Assume balance is $200
            >>> checking.calculate_available_funds()
            700.00  # $200 + $500 overdraft
            
            >>> # Even with negative balance
            >>> # Assume balance is -$100
            >>> checking.calculate_available_funds()
            400.00  # -$100 + $500 overdraft
        """
        return self.balance + self._overdraft_limit
    
    def apply_monthly_fees(self) -> float:
        """
        Apply monthly maintenance fee if below minimum balance.
        
        CheckingAccount charges a flat monthly fee if the balance
        falls below the minimum required balance.
        
        Returns:
            float: Fee charged (0 if balance above minimum)
            
        Examples:
            >>> checking = CheckingAccount("ACC001", "Checking", "Uzzam",
            ...                            monthly_fee=10, minimum_balance=500)
            >>> # Assume balance is $300 (below $500 minimum)
            >>> checking.apply_monthly_fees()
            10.00
            
            >>> # Assume balance is $600 (above minimum)
            >>> checking.apply_monthly_fees()
            0.00
        """
        if self.balance < self._minimum_balance:
            # Create fee transaction
            fee_txn = Transaction(
                transaction_id=f"FEE{datetime.now().strftime('%Y%m%d%H%M%S')}",
                amount=self._monthly_fee,
                date=datetime.now().strftime("%Y-%m-%d"),
                category="Bank Fees",
                account_id=self._account_id,
                transaction_type="debit",
                description="Monthly maintenance fee"
            )
            super().add_transaction(fee_txn)
            return self._monthly_fee
        return 0.0
    
    def can_withdraw(self, amount: float) -> tuple[bool, str]:
        """
        Check if withdrawal is allowed (including overdraft).
        
        CheckingAccount allows withdrawals up to balance + overdraft limit.
        
        Args:
            amount: Amount to withdraw
            
        Returns:
            tuple: (allowed, reason)
                - allowed (bool): True if withdrawal allowed
                - reason (str): Empty if allowed, explanation if not
                
        Examples:
            >>> checking = CheckingAccount("ACC001", "Checking", "Uzzam",
            ...                            overdraft_limit=500)
            >>> # Assume balance is $200
            >>> can, reason = checking.can_withdraw(600)
            >>> can
            True  # $600 < $700 available ($200 + $500 overdraft)
            
            >>> can, reason = checking.can_withdraw(800)
            >>> can
            False
            >>> reason
            'Insufficient funds. Available: $700.00'
        """
        available = self.calculate_available_funds()
        
        if amount <= 0:
            return (False, "Amount must be positive")
        
        if amount <= available:
            return (True, "")
        
        return (False, f"Insufficient funds. Available: ${available:.2f}")
    
    # ══════════════════════════════════════════════════════════════════════
    # CHECKING-SPECIFIC METHODS
    # ══════════════════════════════════════════════════════════════════════
    
    def write_check(self, check_number: int, amount: float, 
                   payee: str) -> Transaction:
        """
        Write a check from this account.
        
        Creates a transaction for the check and tracks the check number
        to prevent duplicates.
        
        Args:
            check_number: Check number (must be unique)
            amount: Check amount (must be positive)
            payee: Who the check is written to
            
        Returns:
            Transaction: The created check transaction
            
        Raises:
            ValueError: If check number already used or amount invalid
            ValueError: If insufficient funds (including overdraft)
            
        Examples:
            >>> checking = CheckingAccount("ACC001", "Checking", "Uzzam",
            ...                            overdraft_limit=500)
            >>> txn = checking.write_check(1001, 250.00, "Electric Company")
            >>> txn.description
            'Check #1001 to Electric Company'
            >>> 1001 in checking.checks_written
            True
        """
        # Validate check number
        if check_number in self._checks_written:
            raise ValueError(f"Check #{check_number} already written")
        
        # Validate amount
        if amount <= 0:
            raise ValueError("Check amount must be positive")
        
        # Check if funds available (including overdraft)
        can_withdraw, reason = self.can_withdraw(amount)
        if not can_withdraw:
            raise ValueError(reason)
        
        # Create check transaction
        check_txn = Transaction(
            transaction_id=f"CHK{check_number}",
            amount=amount,
            date=datetime.now().strftime("%Y-%m-%d"),
            category="Check Payment",
            account_id=self._account_id,
            transaction_type="debit",
            description=f"Check #{check_number} to {payee}"
        )
        
        # Add transaction and track check number
        self.add_transaction(check_txn)
        self._checks_written.append(check_number)
        
        return check_txn
    
    def has_overdraft_protection(self) -> bool:
        """
        Check if account has overdraft protection.
        
        Returns:
            bool: True if overdraft limit > 0
            
        Examples:
            >>> checking1 = CheckingAccount("ACC001", "Checking", "Uzzam")
            >>> checking1.has_overdraft_protection()
            False
            
            >>> checking2 = CheckingAccount("ACC002", "Checking", "Uzzam",
            ...                             overdraft_limit=500)
            >>> checking2.has_overdraft_protection()
            True
        """
        return self._overdraft_limit > 0
    
    def get_overdraft_usage(self) -> float:
        """
        Calculate how much overdraft is currently being used.
        
        Returns:
            float: Amount of overdraft used (0 if balance positive)
            
        Examples:
            >>> checking = CheckingAccount("ACC001", "Checking", "Uzzam",
            ...                            overdraft_limit=500)
            >>> # Assume balance is -$150
            >>> checking.get_overdraft_usage()
            150.00
            
            >>> # Assume balance is $100
            >>> checking.get_overdraft_usage()
            0.00
        """
        if self.balance < 0:
            return abs(self.balance)
        return 0.0
    
    # ══════════════════════════════════════════════════════════════════════
    # SPECIAL METHODS (Override parent)
    # ══════════════════════════════════════════════════════════════════════
    
    def __str__(self) -> str:
        """
        User-friendly string representation.
        
        Returns:
            str: Formatted string with checking-specific info
            
        Examples:
            >>> checking = CheckingAccount("ACC001", "Main Checking", "Uzzam",
            ...                            overdraft_limit=500)
            >>> str(checking)
            'CheckingAccount: Main Checking (Balance: $200.00, Available: $700.00)'
        """
        return (f"CheckingAccount: {self._account_name} "
                f"(Balance: ${self.balance:.2f}, "
                f"Available: ${self.calculate_available_funds():.2f})")
    
    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        
        Returns:
            str: Detailed representation
        """
        return (f"CheckingAccount(id='{self._account_id}', "
                f"name='{self._account_name}', "
                f"overdraft=${self._overdraft_limit:.2f})")


# ══════════════════════════════════════════════════════════════════════════
# DEMONSTRATION
# ══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("CheckingAccount Demonstration")
    print("=" * 70)
    
    # Create checking account
    checking = CheckingAccount(
        "ACC001",
        "Main Checking",
        "Uzzam",
        overdraft_limit=500,
        monthly_fee=10,
        minimum_balance=500
    )
    
    print(f"\n1. Created: {checking}")
    print(f"   Overdraft protection: ${checking.overdraft_limit:.2f}")
    print(f"   Available funds: ${checking.calculate_available_funds():.2f}")
    
    # Test polymorphism
    print("\n2. Polymorphic Methods:")
    print(f"   calculate_available_funds(): ${checking.calculate_available_funds():.2f}")
    print(f"   apply_monthly_fees(): ${checking.apply_monthly_fees():.2f}")
    can, reason = checking.can_withdraw(400)
    print(f"   can_withdraw(400): {can}")
    
    # Test unique features
    print("\n3. Checking-Specific Features:")
    print(f"   Has overdraft: {checking.has_overdraft_protection()}")
    print(f"   Overdraft usage: ${checking.get_overdraft_usage():.2f}")
    
    print("\n" + "=" * 70)
