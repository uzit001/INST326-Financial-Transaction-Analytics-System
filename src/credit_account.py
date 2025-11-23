"""
CreditAccount - Concrete Implementation
Author: Keven Day
Date: November 2025
Course: INST326 Section 0302

The credit account allows for charges to be made on a credit limit, intrest rates for paying back,
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

class CreditAccount(Account):
    """Credit card account that charges interest on balances."""
    
    def __init__(self, owner, account_id, account_name, credit_limit, apr, balance=0.0):
        """
        Initialize a Credit Account.
        
        Args:
            account_id: Unique account ID (e.g., "ACC001")
            account_name: Name of the account (e.g., "Chase Visa")
            credit_limit: Maximum credit limit
            apr: Annual Percentage Rate (e.g., 18.99 for 18.99%)
            balance: Starting balance (default 0.0, negative means owed)
        """
        super().__init__(account_id, account_name, owner)
        self.balance = balance 
        self._credit_limit = credit_limit
        self._apr = apr
        self._total_interest_charged = 0.0
    # ══════════════════════════════════════════════════════════════════════
    # properties 
    # ══════════════════════════════════════════════════════════════════════  
    @property
    def credit_limit(self):
        """Get credit limit."""
        return self._credit_limit
    
    @property
    def available_credit(self):
        """Calculate available credit remaining."""
        # For credit cards, negative balance means money owed
        # Positive balance means credit available
        return self._credit_limit + self._balance  # balance is negative when owed
    
    @property
    def apr(self):
        """Get APR."""
        return self._apr
    
    @property
    def total_interest_charged(self):
        """Get total interest charged over account lifetime."""
        return self._total_interest_charged
    # ══════════════════════════════════════════════════════════════════════
    # ABSTRACT METHODS 
    # ══════════════════════════════════════════════════════════════════════
    def calculate_available_funds(self):
    """
    Calculate available credit remaining.
    
    Returns:
        float: Amount of credit available to spend
    """
    if balance < 0
        return self._credit_limit - self._balance
    
    if balance > 0:
        return self._credit_limit + self._balance

    def apply_monthly_fees(self):
    """
    Calculate and apply monthly interest charges.
    
    Returns:
        float: Interest charged (positive number = you pay this)
    """
    # Only charge interest if there's a balance owed
    if self._balance <= 0:  # No balance owed
        return 0.0
    
    # Calculate monthly interest
    monthly_rate = self._apr / 100 / 12
    interest = self._balance * monthly_rate
    
    # Apply interest to balance
    self._balance += interest
    self._total_interest_charged += interest
    
    return interest  # Positive = money charged
    def can_withdraw(self, amount):
    """
    Check if a charge is allowed (won't exceed credit limit).
    
    Args:
        amount: Amount to charge
        
    Returns:
        tuple: (allowed, reason)
    """
    available = self.calculate_available_funds()
    
    if amount <= available:
        return (True, "")
    else:
        return (False, f"Exceeds credit limit. Available credit: ${available:.2f}")

    # ══════════════════════════════════════════════════════════════════════
    # credit specific methods
    # ══════════════════════════════════════════════════════════════════════
    
    def set_apr(self, new_apr):
        """
        Update the APR.
        
        Args:
            new_apr: New annual percentage rate
        """
        if new_apr < 0:
            raise ValueError("APR cannot be negative")
        self._apr = new_apr
        
    def calculate_interest(self):
        
        """
        Calculate monthly interest on the balance.
        Credit cards charge interest on negative balances (money owed).
            
        Returns:
            Interest amount to be charged
        """
        # Only charge interest if there's a balance owed (negative balance)
        if self._balance >= 0:
            return 0.0
            
        # Monthly interest rate
        monthly_rate = self._apr / 100 / 12
            
        # Interest on amount owed (negative balance, so multiply by -1)
        interest = abs(self._balance) * monthly_rate
            
        return interest
    
    def apply_interest(self):
            """
            Apply monthly interest to the account balance.
            This reduces the balance (makes it more negative).
            """
            interest = self.calculate_interest()
            if interest > 0:
                self._balance -= interest  # Makes balance more negative
                self._total_interest_charged += interest
            return interest
    def __str__(self):
        """String representation."""
        owed = abs(self._balance) if self._balance < 0 else 0
        return f"CreditAccount('{self.account_name}', owed=${owed:.2f}, limit=${self._credit_limit:.2f})"
