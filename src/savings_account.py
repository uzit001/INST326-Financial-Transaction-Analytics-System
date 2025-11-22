"""
SavingsAccount - Concrete Implementation
Author: Angelo Montagnino
Date: November 2025
Course: INST326 Section 0302

SavingsAccount specializes the Account base class for long-term savings with 
interest earnings, minimum balance requirements, and limited monthly 
withdrawals.
"""
from datetime import datetime
from src.account import Account
from datetime import datetime
from src.transaction import Transaction



class SavingsAccount(Account):
    """
    Savings account with interest earnings and withdrawal limits.
    
    Features:
        - Earns monthly interest on balance
        - Requires minimum balance to avoid fees
        - Limited withdrawals per month (Regulation D style)
    
    Attributes:
        interest_rate (float): Annual interest rate (e.g., 0.04 = 4%)
        minimum_balance (float): Minimum balance to avoid fees
        monthly_withdrawal_limit (int): Max withdrawals per month
        low_balance_fee (float): Fee charged if below minimum balance
    
    Example:
        >>> savings = SavingsAccount(
        ...     account_id="SAV001",
        ...     account_name="Emergency Fund",
        ...     owner="Uzzam",
        ...     interest_rate=0.045,
        ...     minimum_balance=500
        ... )
        >>> savings.calculate_available_funds()
        500.00  # balance minus minimum required
    """
    
    # Class constants
    DEFAULT_INTEREST_RATE = 0.04  # 4% annual
    DEFAULT_MINIMUM_BALANCE = 100.0
    DEFAULT_WITHDRAWAL_LIMIT = 6  # Per month
    DEFAULT_LOW_BALANCE_FEE = 15.0
    
    def __init__(
        self,
        account_id: str,
        account_name: str,
        owner: str,
        interest_rate: float = DEFAULT_INTEREST_RATE,
        minimum_balance: float = DEFAULT_MINIMUM_BALANCE,
        monthly_withdrawal_limit: int = DEFAULT_WITHDRAWAL_LIMIT,
        low_balance_fee: float = DEFAULT_LOW_BALANCE_FEE
    ):
        """
        Initialize a savings account.
        
        Args:
            account_id: Unique identifier
            account_name: Display name
            owner: Account owner's name
            interest_rate: Annual interest rate (default 4%)
            minimum_balance: Minimum balance requirement (default $100)
            monthly_withdrawal_limit: Max withdrawals per month (default 6)
            low_balance_fee: Fee if below minimum balance (default $15)
            
        Raises:
            ValueError: If interest_rate < 0 or minimum_balance < 0
        """
        # Call parent constructor
        super().__init__(account_id, account_name, owner)
        
        # Validate savings-specific parameters
        if interest_rate < 0:
            raise ValueError("Interest rate cannot be negative")
        if minimum_balance < 0:
            raise ValueError("Minimum balance cannot be negative")
        if monthly_withdrawal_limit < 0:
            raise ValueError("Withdrawal limit cannot be negative")
        if low_balance_fee < 0:
            raise ValueError("Low balance fee cannot be negative")
        
        # Set savings-specific attributes
        self._interest_rate = interest_rate
        self._minimum_balance = minimum_balance
        self._monthly_withdrawal_limit = monthly_withdrawal_limit
        self._low_balance_fee = low_balance_fee
        
        # Track withdrawals per month
        self._withdrawal_count_this_month = 0
        self._last_withdrawal_month = None
    
    # ══════════════════════════════════════════════════════════════════════
    # PROPERTIES
    # ══════════════════════════════════════════════════════════════════════
    
    @property
    def interest_rate(self) -> float:
        """float: Annual interest rate."""
        return self._interest_rate
    
    @interest_rate.setter
    def interest_rate(self, value: float) -> None:
        if value < 0:
            raise ValueError("Interest rate cannot be negative")
        self._interest_rate = value
    
    @property
    def minimum_balance(self) -> float:
        """float: Minimum balance requirement."""
        return self._minimum_balance
    
    @property
    def monthly_withdrawal_limit(self) -> int:
        """int: Maximum withdrawals allowed per month."""
        return self._monthly_withdrawal_limit
    
    @property
    def withdrawals_remaining(self) -> int:
        """int: Number of withdrawals remaining this month."""
        self._reset_withdrawal_count_if_new_month()
        return max(0, self._monthly_withdrawal_limit - self._withdrawal_count_this_month)
    
    # ══════════════════════════════════════════════════════════════════════
    # ABSTRACT METHOD IMPLEMENTATIONS
    # ══════════════════════════════════════════════════════════════════════
    
    def calculate_available_funds(self) -> float:
        """
        Calculate available funds (balance minus minimum balance requirement).
        
        The minimum balance must be maintained, so available funds
        is the amount above that threshold.
        
        Returns:
            float: Available amount (never negative)
            
        Example:
            >>> savings = SavingsAccount("SAV001", "Savings", "Uzzam",
            ...                         minimum_balance=500)
            >>> # If balance is $1500
            >>> savings.calculate_available_funds()
            1000.00  # $1500 - $500 minimum
        """
        available = self.balance - self._minimum_balance
        return max(0, available)
    
    def apply_monthly_fees(self) -> float:
        """
        Apply monthly interest earnings or low balance fees.
        
        - If balance >= minimum: EARN interest (returns negative)
        - If balance < minimum: CHARGE low balance fee (returns positive)
        
        Interest is calculated as: balance * (annual_rate / 12)
        
        Returns:
            float: Negative = interest earned, Positive = fee charged
            
        Example:
            >>> savings = SavingsAccount("SAV001", "Savings", "Uzzam",
            ...                         interest_rate=0.04)
            >>> # With $5000 balance
            >>> savings.apply_monthly_fees()
            -16.67  # Earned $16.67 interest
        """
        if self.balance >= self._minimum_balance:
            # Calculate monthly interest (annual rate / 12)
            monthly_interest = self.balance * (self._interest_rate / 12)
            # Return negative because it's money EARNED
            return -round(monthly_interest, 2)
        else:
            # Below minimum balance - charge fee
            return self._low_balance_fee
    
    def can_withdraw(self, amount: float) -> tuple[bool, str]:
        """
        Check if withdrawal is allowed based on balance and monthly limit.
        
        Validates:
            1. Amount is positive
            2. Sufficient funds (respecting minimum balance)
            3. Withdrawal limit not exceeded
        
        Args:
            amount: Amount to withdraw
            
        Returns:
            tuple: (allowed, reason)
            
        Example:
            >>> savings.can_withdraw(100)
            (True, '')
            
            >>> savings.can_withdraw(10000)
            (False, 'Insufficient funds. Available: $1,000.00')
        """
        # Validate amount
        if amount <= 0:
            return False, "Withdrawal amount must be positive"
        
        # Check withdrawal limit
        self._reset_withdrawal_count_if_new_month()
        if self._withdrawal_count_this_month >= self._monthly_withdrawal_limit:
            return False, (
                f"Monthly withdrawal limit reached ({self._monthly_withdrawal_limit}). "
                f"Resets next month."
            )
        
        # Check available funds
        available = self.calculate_available_funds()
        if amount > available:
            return False, (
                f"Insufficient funds. Available: ${available:,.2f} "
                f"(${self._minimum_balance:,.2f} minimum balance required)"
            )
        
        return True, ""
    
    # ══════════════════════════════════════════════════════════════════════
    # OVERRIDDEN METHODS
    # ══════════════════════════════════════════════════════════════════════
    
    def add_transaction(self, transaction) -> None:
        """
        Add transaction with withdrawal tracking.
        
        Overrides parent to track withdrawal count for monthly limits.
        
        Args:
            transaction: Transaction to add
            
        Raises:
            ValueError: If withdrawal not allowed
        """
        # Check if it's a withdrawal (negative amount)
        if transaction.signed_amount < 0:
            allowed, reason = self.can_withdraw(abs(transaction.signed_amount))
            if not allowed:
                raise ValueError(f"Withdrawal denied: {reason}")
            
            # Increment withdrawal count
            self._reset_withdrawal_count_if_new_month()
            self._withdrawal_count_this_month += 1
            self._last_withdrawal_month = datetime.now().month
        
        # Call parent method to actually add the transaction
        super().add_transaction(transaction)
    
    # ══════════════════════════════════════════════════════════════════════
    # HELPER METHODS
    # ══════════════════════════════════════════════════════════════════════
    
    def _reset_withdrawal_count_if_new_month(self) -> None:
        """Reset withdrawal count if we're in a new month."""
        current_month = datetime.now().month
        if self._last_withdrawal_month != current_month:
            self._withdrawal_count_this_month = 0
    
    def calculate_annual_yield(self) -> float:
        """
        Calculate projected annual yield based on current balance.
        
        Returns:
            float: Projected annual interest earnings
            
        Example:
            >>> savings.balance  # $10,000
            >>> savings.calculate_annual_yield()
            400.00  # At 4% interest
        """
        return round(self.balance * self._interest_rate, 2)
    
    def get_account_summary(self) -> dict:
        """
        Get a summary of account status.
        
        Returns:
            dict: Account summary information
        """
        return {
            "account_id": self.account_id,
            "account_name": self.account_name,
            "owner": self.owner,
            "balance": self.balance,
            "available_funds": self.calculate_available_funds(),
            "interest_rate": f"{self._interest_rate * 100:.2f}%",
            "minimum_balance": self._minimum_balance,
            "withdrawals_remaining": self.withdrawals_remaining,
            "projected_annual_yield": self.calculate_annual_yield(),
        }
    
    # ══════════════════════════════════════════════════════════════════════
    # SPECIAL METHODS
    # ══════════════════════════════════════════════════════════════════════
    
    def __str__(self) -> str:
        """User-friendly string representation."""
        return (
            f"{self._account_name} ({self._account_id}): "
            f"${self.balance:,.2f} @ {self._interest_rate * 100:.1f}% APY"
        )
    
    def __repr__(self) -> str:
        """Developer-friendly string representation."""
        return (
            f"SavingsAccount(id='{self._account_id}', "
            f"name='{self._account_name}', "
            f"owner='{self._owner}', "
            f"interest_rate={self._interest_rate}, "
            f"min_balance={self._minimum_balance})"
        )