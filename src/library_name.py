"""
Financial Transaction Tracker - Function Library
Course: INST326 Section 0302
Team Members: Uzzam Tariq, Keven Day, Kevin Miele, Angelo Montagnino
"""

from datetime import datetime
from typing import Union, Dict, List, Tuple

# ============================================================================
# DATA VALIDATION FUNCTIONS
# ============================================================================

#1.
def validate_transaction_amount(amount: Union[int, float]) -> bool:
    """
    Validate that a transaction amount is positive and within reasonable bounds.
    
    This is a simple validation function that ensures transaction amounts
    are valid numbers that make sense for financial transactions.
    
    Args:
        amount (Union[int, float]): The transaction amount to validate
        
    Returns:
        bool: True if amount is valid, False otherwise
        
    Raises:
        TypeError: If amount is not a number (int or float)
        
    Examples:
        >>> validate_transaction_amount(50.00)
        True
        >>> validate_transaction_amount(-10.00)
        False
        >>> validate_transaction_amount(0)
        False
    """
    if not isinstance(amount, (int, float)):
        raise TypeError(f"Amount must be a number, got {type(amount).__name__}")
    
    # Amount must be positive
    if amount <= 0:
        return False
    
    # Reasonable upper limit to catch data entry errors
    if amount > 1000000:
        return False
    
    return True

#2.
def validate_date_format(date_string: str, date_format: str = "%Y-%m-%d") -> bool:
    """
    Validate that a date string matches the expected format and represents a valid date.
    
    This is a medium complexity function that checks both format and logical validity
    of dates, ensuring they exist and are not in the future (for financial transactions).
    
    Args:
        date_string (str): The date string to validate
        date_format (str): Expected date format. Defaults to "YYYY-MM-DD"
        
    Returns:
        bool: True if date is valid and properly formatted, False otherwise
        
    Raises:
        TypeError: If date_string is not a string
        
    Examples:
        >>> validate_date_format("2025-10-11")
        True
        >>> validate_date_format("2025-13-45")
        False
        >>> validate_date_format("10/11/2025", "%m/%d/%Y")
        True
        >>> validate_date_format("2026-01-01")  # Future date
        False
    """
    if not isinstance(date_string, str):
        raise TypeError(f"Date must be a string, got {type(date_string).__name__}")
    
    try:
        # Parse the date string
        parsed_date = datetime.strptime(date_string, date_format)
        
        # Check if date is not in the future
        if parsed_date > datetime.now():
            return False
        
        # Check if date is not unreasonably old (before 1900)
        if parsed_date.year < 1900:
            return False
            
        return True
        
    except ValueError:
        # Invalid date or format
        return False

#3.
def validate_category(category: str, allow_custom: bool = False) -> bool:
    """
    Validate that a transaction category is recognized and properly formatted.
    
    This is a medium complexity function that checks categories against
    a predefined list of valid financial categories and handles custom categories
    when allowed.
    
    Args:
        category (str): The category name to validate
        allow_custom (bool): If True, allows categories not in predefined list.
                            Defaults to False.
        
    Returns:
        bool: True if category is valid, False otherwise
        
    Raises:
        TypeError: If category is not a string
        ValueError: If category is empty or only whitespace
        
    Examples:
        >>> validate_category("Subscription")
        True
        >>> validate_category("food")  # Case insensitive
        True
        >>> validate_category("InvalidCategory")
        False
        >>> validate_category("My Custom Category", allow_custom=True)
        True
    """
    if not isinstance(category, str):
        raise TypeError(f"Category must be a string, got {type(category).__name__}")
    
    # Check for empty or whitespace-only strings
    if not category.strip():
        raise ValueError("Category cannot be empty or only whitespace")
    
    # Predefined valid categories (aligned with project requirements)
    valid_categories = {
        'subscription', 'subscriptions',
        'bill', 'bills',
        'food', 'groceries',
        'entertainment',
        'transportation', 'transport',
        'utilities',
        'healthcare', 'health',
        'shopping', 'retail',
        'debt', 'loan',
        'income', 'salary',
        'other'
    }
    
    # Normalize category for comparison
    normalized_category = category.strip().lower()
    
    # Check if it's a valid predefined category
    if normalized_category in valid_categories:
        return True
    
    # If custom categories are allowed and basic formatting is valid
    if allow_custom:
        # Must be reasonable length
        if len(category) > 50:
            return False
        # Must contain at least one letter
        if not any(c.isalpha() for c in category):
            return False
        return True
    
    return False

#4.
def validate_transaction_data(transaction_dict: dict) -> tuple[bool, list[str]]:
    """
    Comprehensively validate all fields in a transaction dictionary.
    
    This is a complex validation function that checks multiple fields,
    accumulates error messages, and ensures the entire transaction record
    is consistent and valid for storage.
    
    Args:
        transaction_dict (dict): Dictionary containing transaction data with keys:
                                - 'amount': transaction amount (required)
                                - 'date': transaction date (required)
                                - 'category': transaction category (required)
                                - 'description': transaction description (optional)
                                - 'account': account name/id (required)
        
    Returns:
        tuple[bool, list[str]]: A tuple containing:
                               - bool: True if all validations pass, False otherwise
                               - list[str]: List of error messages (empty if valid)
        
    Raises:
        TypeError: If transaction_dict is not a dictionary
        
    Examples:
        >>> transaction = {
        ...     'amount': 49.99,
        ...     'date': '2025-10-11',
        ...     'category': 'Subscription',
        ...     'description': 'Netflix',
        ...     'account': 'Checking'
        ... }
        >>> is_valid, errors = validate_transaction_data(transaction)
        >>> is_valid
        True
        >>> errors
        []
        
        >>> bad_transaction = {
        ...     'amount': -50,
        ...     'date': '2025-13-45',
        ...     'category': ''
        ... }
        >>> is_valid, errors = validate_transaction_data(bad_transaction)
        >>> is_valid
        False
        >>> len(errors) > 0
        True
    """
    if not isinstance(transaction_dict, dict):
        raise TypeError(f"Transaction must be a dictionary, got {type(transaction_dict).__name__}")
    
    errors = []
    required_fields = ['amount', 'date', 'category', 'account']
    
    # Check for required fields
    for field in required_fields:
        if field not in transaction_dict:
            errors.append(f"Missing required field: '{field}'")
    
    # If missing required fields, return early
    if errors:
        return False, errors
    
    # Validate amount
    try:
        if not validate_transaction_amount(transaction_dict['amount']):
            errors.append("Invalid amount: must be positive and less than $1,000,000")
    except TypeError as e:
        errors.append(f"Amount validation error: {str(e)}")
    
    # Validate date
    try:
        if not validate_date_format(transaction_dict['date']):
            errors.append("Invalid date: must be in YYYY-MM-DD format and not in the future")
    except TypeError as e:
        errors.append(f"Date validation error: {str(e)}")
    
    # Validate category
    try:
        if not validate_category(transaction_dict['category']):
            errors.append("Invalid category: not a recognized category (use allow_custom=True for custom categories)")
    except (TypeError, ValueError) as e:
        errors.append(f"Category validation error: {str(e)}")
    
    # Validate account (basic check - must be non-empty string)
    account = transaction_dict['account']
    if not isinstance(account, str):
        errors.append(f"Account must be a string, got {type(account).__name__}")
    elif not account.strip():
        errors.append("Account cannot be empty")
    elif len(account) > 100:
        errors.append("Account name is too long (max 100 characters)")
    
    # Validate optional description if present
    if 'description' in transaction_dict:
        description = transaction_dict['description']
        if not isinstance(description, str):
            errors.append(f"Description must be a string, got {type(description).__name__}")
        elif len(description) > 500:
            errors.append("Description is too long (max 500 characters)")
    
    # Check for amount and account consistency if account balance is provided
    if 'account_balance' in transaction_dict:
        try:
            balance = float(transaction_dict['account_balance'])
            amount = float(transaction_dict['amount'])
            if balance < 0 and abs(balance) < amount:
                errors.append("Warning: Transaction amount exceeds available balance")
        except (ValueError, TypeError):
            errors.append("Invalid account_balance: must be a number")
    
    # Return validation result
    is_valid = len(errors) == 0
    return is_valid, errors


if __name__ == "__main__":
    # Test the functions with some examples
    print("Testing validation functions...\n")
    
    # Test 1: validate_transaction_amount
    print("Test 1: validate_transaction_amount")
    print(f"  50.00: {validate_transaction_amount(50.00)}")
    print(f"  -10.00: {validate_transaction_amount(-10.00)}")
    
    # Test 2: validate_date_format
    print("\nTest 2: validate_date_format")
    print(f"  '2025-10-11': {validate_date_format('2025-10-11')}")
    print(f"  '2025-13-45': {validate_date_format('2025-13-45')}")
    
    # Test 3: validate_category
    print("\nTest 3: validate_category")
    print(f"  'Subscription': {validate_category('Subscription')}")
    print(f"  'InvalidCat': {validate_category('InvalidCat')}")
    
    # Test 4: validate_transaction_data
    print("\nTest 4: validate_transaction_data")
    good_transaction = {
        'amount': 49.99,
        'date': '2025-10-11',
        'category': 'Subscription',
        'description': 'Netflix',
        'account': 'Checking'
    }
    is_valid, errors = validate_transaction_data(good_transaction)
    print(f"  Valid transaction: {is_valid}, Errors: {errors}")

# import list
import csv
# 1-5 Keven Day 
# 1. Find_largest_transaction 
# will sort transactions in order from largest to smallest by amount spent 
def sort_largest_transaction(accounts):
    unsorted_list = accounts.copy()
    sorted_list = []
    # sort until unsorted is done 
    while unsorted_list:
        largest_transaction = unsorted_list[0]
        largest_amount = largest_transaction["Amount"]

        # find transaction with largest amount
        for transaction in unsorted_list:
            if transaction["Amount"] > largest_amount:
                largest_amount = transaction["Amount"]
                largest_transaction = transaction 

        # add the largest transaction to the sorted list
        sorted_list.append(largest_transaction)

        # remove largest transaction from the unsorted list
        unsorted_list.remove(largest_transaction)

    return(sorted_list)
# 2. get_transaction_by_date_range
# will return any transactions that are included in given date range 
def get_transaction_by_date_range(transactions, start_date, end_date):
    # Helper function to validate date format (YYYY-MM-DD)
    def is_valid_date_format(date_str):
        # Check structure and character count
        if len(date_str) != 10:
            return False
        if date_str[4] != "-" or date_str[7] != "-":
            return False

        year, month, day = date_str.split("-")

        # Check that all parts are numeric
        if not (year.isdigit() and month.isdigit() and day.isdigit()):
            return False

        # Check proper ranges
        if not (1 <= int(month) <= 12):
            return False
        if not (1 <= int(day) <= 31):
            return False

        return True

    # Check start and end date formats
    if not is_valid_date_format(start_date):
        raise ValueError(f"Start date '{start_date}' is not in 'YYYY-MM-DD' format.")
    if not is_valid_date_format(end_date):
        raise ValueError(f"End date '{end_date}' is not in 'YYYY-MM-DD' format.")

    # Check date order
    if start_date > end_date:
        raise ValueError("Start date cannot be after end date.")

    matching_transactions = []

    for transaction in transactions:
        # ensures theres a data field 
        if "Date" not in transaction:
            print(f"Skipping transaction {transaction.get('ID', '?')}: missing 'Date' field.")
            continue

        date = transaction["Date"]

        # Validate format of the transaction date
        if not is_valid_date_format(date):
            print(f"Skipping transaction {transaction.get('ID', '?')}: invalid date format '{date}'.")
            continue

        # Compare as strings (works for YYYY-MM-DD)
        if start_date <= date <= end_date:
            matching_transactions.append(transaction)

    return matching_transactions

# 3. compare_balance_accounts 
# will compare different accounts and find the diffence in balance betwneen the two 
def compare_balance_accounts(accounts, id1, id2):
    # Step 1: Create placeholders
    balance1 = None
    balance2 = None

    # Step 2: Loop through all accounts to find the two IDs
    for account in accounts:
        if account["ID"] == id1:
            balance1 = account["Amount"]
        elif account["ID"] == id2:
            balance2 = account["Amount"]

    # Step 3: Validation checks
    if balance1 is None:
        raise ValueError(f"Account with ID '{id1}' not found.")
    if balance2 is None:
        raise ValueError(f"Account with ID '{id2}' not found.")

    # Step 4: Calculate and return the difference
    difference = abs(balance1 - balance2)

    return {
        "Account 1": id1,
        "Account 2": id2,
        "Balance Difference": difference
    }
   #  4. calculate_monthly_average
# will compute the total spending of accounts in that month 
def calculate_monthly_average(transactions):

    # Step 1: create a dictionary to group transactions by month
    monthly_data = {}

    for transaction in transactions:
        date = transaction["Date"]

        # validation check
        if len(date) != 10 or date[4] != '-' or date[7] != '-':
            raise ValueError(f"Invalid date format: {date}. Must be 'YYYY-MM-DD'.")

        # Step 2: extract month key 
        month_key = date[:7]

        # Step 3: add transaction amount to that month
        if month_key not in monthly_data:
            monthly_data[month_key] = []
        monthly_data[month_key].append(transaction["Amount"])

    # Step 4: computess total and average for each month
    monthly_summary = {}
    for month, amounts in monthly_data.items():
        total = sum(amounts)
        average = total / len(amounts)
        monthly_summary[month] = {
            "Total Spending": round(total, 2),
            "Average Transaction": round(average, 2),
            "Transaction Count": len(amounts)
        }

    return monthly_summary
# 5. export_to_csv
# exports the data into a csv file
def export_to_csv(data, filename):
    """
    Exports a list of dictionaries (data) into a CSV file.
    Example: export_to_csv(transactions, "transactions.csv")
    """

    # Validation check
    if not data or not isinstance(data, list):
        raise ValueError("Data must be a non-empty list of dictionaries.")

    # Step 1: Get the column headers from the first dictionary’s keys
    headers = data[0].keys()

    # Step 2: Create and write to the CSV file
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)

        # Step 3: Write the headers first
        writer.writeheader()

        # Step 4: Write all rows (each dictionary)
        for row in data:
            writer.writerow(row)

    print(f"Data successfully exported to '{filename}'")
    
# Data transformation functions - Angelo Montagnino
# 1-5
# 1 - Sum spending by category
def calculate_category_totals(transactions:list) -> dict : 
    """
    Calculates total spending per category.

    Args:
        transactions (list): A list of dictionaries with at least 'amount' and 'category' keys.

    Returns:
        dict: A dictionary where keys are categories and values are total amounts spent.
    """
    # New dictionary to store category totals
    category_totals = {}
    # Validation Checks
    if not isinstance(transactions, list):
        raise TypeError("Transactions must be a list.")

    for t in transactions:
        if not isinstance(t, dict):
            raise TypeError("Each transaction must be a dictionary.")
        if 'amount' not in t or 'category' not in t:
            raise ValueError("Each transaction must include 'amount' and 'category'.")
        if not isinstance(t['amount'], (int, float)):
            raise TypeError("Transaction amount must be a number.")
        if not isinstance(t['category'], str):
            raise TypeError("Transaction category must be a string.")

        # Pull data from dictionary
        category = t['category'].strip().title()
        amount = t['amount']

       # Calculate transaction total by category
        if category not in category_totals:
            category_totals[category] = 0.0
        category_totals[category] += amount
    
    for category in category_totals:
     category_totals[category] = round(category_totals[category], 2)

    return category_totals

# 2 - Identify Subscriptions
def detect_recuring_payments(transactions: list) -> str:
    """
    Detects unique recurring subscription payments from a list of transactions.

    Args:
        transactions (list): A list of dictionaries containing transaction details.
                             Each transaction should include:
                             - 'subscription' (bool)
                             - 'source' (str)
                             - 'amount' (float or int)

    Returns:
        str: A summary of detected subscriptions.

    """
    # New set to store seen sources
    seen_sources = set()
    # New list to store subscriptions
    subscription_list = []
    # Validation Checks
    if not isinstance(transactions, list):
        raise TypeError("Input must be a list of transactions.")
    
    for t in transactions:
        if not isinstance(t, dict):
            raise TypeError("Each transaction must be a dictionary.")
        # Find subscriptions in transactions
        if t.get('subscription') == True:
            source = t.get('source', '').strip().title()
            # Avoid repeat subscriptions
            if source not in seen_sources:
                seen_sources.add(source)
                subscription_list.append({
                    'source': source,
                    'amount': float(t.get('amount', 0))
                })
    # Return if no subscriptions present
    if not subscription_list:
        return "No subscriptions detected.", []
    # Format to string
    summary = 'Subscriptions: \n'
    for sub in subscription_list:
        summary += f"{sub['source']}: ${sub['amount']:.2f} per month\n"

    return summary.strip()

# 3 - Sum transactions and return current balance
def calculate_account_balance(balance:float,transactions:list) -> str:
    """
    Calculates the remaining account balance after subtracting all transaction amounts.

    Args:
        balance (float): The starting account balance.
        transactions (list): A list of dictionaries containing at least an 'amount' key.

    Returns:
        str: A formatted string showing the remaining account balance.
    """
    amount_total = 0
    # Validation Checks
    if not isinstance(balance, (int, float)):
        raise TypeError("Balance must be a number.")
    
    for t in transactions:
        if not isinstance(t, dict):
            raise TypeError("Each transaction must be a dictionary.")
        if not isinstance(t['amount'], (int, float)):
            raise TypeError("Transaction amount must be a number.")
        if not isinstance(t['amount'], (int, float)):
            raise TypeError("Transaction amount must be a number.")
        
        amount_total += t["amount"]
     # Calculate Current Balance
    account_balance = balance - amount_total   
    return f'Account Balance: ${account_balance:.2f}'

# 4 - Create period summaries (monthly)
def generate_spending_summary(transactions: list, summary_type: str = 'monthly') -> dict:
    """
    Generates a spending summary grouped by month.

    Args:
        transactions (list): A list of transaction dictionaries. Each must include
                             'amount' (float) and 'date' (str in MM-DD-YYYY format).
        summary_type (str): 'monthly' to indicate how to group the summary.

    Returns:
        dict: A dictionary with period keys and total spending values.
    """
    # New Dictonary to store period summaries
    summary = {}
    # Validation Checks
    if summary_type.lower().strip() != 'monthly':
        raise ValueError("summary_type must be 'monthly'")

    for t in transactions:
        if not isinstance(t, dict):
            raise TypeError("Each transaction must be a dictionary.")
        if 'amount' not in t or 'date' not in t:
            raise ValueError("Each transaction must contain 'amount' and 'date'.")
        if not isinstance(t['amount'], (int, float)):
            raise TypeError("Transaction amount must be a number.")
        # Pull data from transactions
        date = t['date']
        amount = t['amount']
        # Validate Date format
        if len(date) != 10 or date[2] != '-' or date[5] != '-':
            raise ValueError(f"Invalid date format: {date}")
        # Pull month and year from date
        month = date[:2]
        year = date[6:]
        
        if summary_type.strip().lower() == 'monthly':
            period = f"{month}-{year}"
        # Calculate period total
        if period not in summary:
            summary[period] = 0.0
        summary[period] += amount
    # Round to two decimal value
    for period in summary:
        summary[period] = round(summary[period], 2)

    return summary

# 5 - Flag unusual transactions
def identify_spending_spikes(transactions: list, spending_limit: float = 100) -> str:
    """
    Identifies transactions that exceed a specified spending limit.

    Args:
        transactions (list): A list of dictionaries containing 'amount', 'source', and 'date'.
        spending_limit (float): The threshold to flag a transaction. Default to 100.

    Returns:
        str: A formatted message listing flagged transactions or indicating none were found.
    """
    # New list to store flagged transactions
    flagged_transactions = []
    # Validation Checks
    for t in transactions:
        if not isinstance(t, dict):
            raise TypeError("Each transaction must be a dictionary.")
        if 'amount' not in t or 'source' not in t or 'date' not in t:
            raise ValueError("Each transaction must include 'amount', 'source', and 'date'.")
        if not isinstance(t['amount'], (int, float)):
            raise TypeError("'amount' must be a number.")
        
        # Check if transaction exceeds spending limit
        if t['amount'] >= spending_limit:
            flagged_transactions.append(t)
            
    # Return string if no unusual spending found
    if not flagged_transactions:
        return "No unusual spending detected."

    # Create formatted output for all flagged transactions
    report = "Unusual spending detected:\n"
    for ft in flagged_transactions:
        report += f"- ${ft['amount']:.2f} from {ft['source']} on {ft['date']}\n"

    return report.strip()

from datetime import datetime
from typing import Any, Dict, List, Tuple

# Data Cleaning Functions - Kevin Miele
# 1-4
# 1) normalize_date_format
def normalize_date_format(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize row['date'] (or 'Date') to ISO 'YYYY-MM-DD'.

    Tries, in order:
      - %Y-%m-%d   (e.g., 2025-10-11)
      - %Y/%m/%d   (e.g., 2025/10/11)
      - %m/%d/%Y   (e.g., 10/11/2025)
      - %m-%d-%Y   (e.g., 10-11-2025)

    Returns:
      Dict[str, Any]: NEW row with 'date' set to ISO 'YYYY-MM-DD'. Removes 'Date' if present.

    Raises:
      KeyError: if neither 'date' nor 'Date' exists.
      ValueError: if the date cannot be parsed by the supported formats.
      TypeError: if the date value is not a string-like value.
    """
    if "date" not in row and "Date" not in row:
        raise KeyError("normalize_date_format: expected key 'date' or 'Date'")

    raw = row.get("date", row.get("Date"))
    if raw is None:
        raise ValueError("normalize_date_format: date value is None")
    s = str(raw).strip()
    if not s:
        raise ValueError("normalize_date_format: date cannot be empty")

    fmts = ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%m-%d-%Y")
    parsed = None
    for fmt in fmts:
        try:
            parsed = datetime.strptime(s, fmt)
            break
        except ValueError:
            continue
    if parsed is None:
        raise ValueError(f"normalize_date_format: unsupported date format '{raw}'")

    out = dict(row)
    out["date"] = parsed.strftime("%Y-%m-%d")
    out.pop("Date", None)
    return out


# 2) clean_transaction_description
def clean_transaction_description(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean row['description'] (or 'Description'/'source'):
      - trim and collapse internal spaces
      - remove ONE trailing code-like token (e.g., '#123', 'TRN0001', 'ORD-9981')

    Returns:
      Dict[str, Any]: NEW row with 'description' (standard key). Removes 'Description'/'source'.

    Raises:
      KeyError: if no description-like key is present.
      ValueError: if the cleaned description is empty.
    """
    if not any(k in row for k in ("description", "Description", "source")):
        raise KeyError("clean_transaction_description: expected 'description', 'Description', or 'source'")

    raw = row.get("description", row.get("Description", row.get("source")))
    s = " ".join(str(raw).strip().split())
    if not s:
        raise ValueError("clean_transaction_description: description cannot be empty")

    tokens = s.split(" ")
    if tokens:
        last = tokens[-1]
        digit_count = sum(ch.isdigit() for ch in last)
        if digit_count >= 3 or last.startswith("#") or "-" in last:
            tokens.pop()

    cleaned = " ".join(tokens).strip()
    if not cleaned:
        raise ValueError("clean_transaction_description: description became empty after cleaning")

    out = dict(row)
    out["description"] = cleaned
    out.pop("Description", None)
    out.pop("source", None)
    return out


# 3) standardize_category_names
def standardize_category_names(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map row['category'] (or 'Category'):

      Subscription, Bills, Food, Groceries, Entertainment,
      Transportation, Utilities, Healthcare, Shopping, Debt, Income, Other

    Exact/contains checks cover common variants
    (e.g., 'subscr' → 'Subscription', 'Dining' → 'Food', 'retail' → 'Shopping').

    Returns:
      Dict[str, Any]: NEW row with standard 'category'. Removes 'Category' if present.

    Raises:
      KeyError: if no category-like key is present.
      ValueError: if the category is empty.
    """
    if "category" not in row and "Category" not in row:
        raise KeyError("standardize_category_names: expected 'category' or 'Category'")

    raw = row.get("category", row.get("Category"))
    s = str(raw).strip().lower()
    if not s:
        raise ValueError("standardize_category_names: category cannot be empty")

    mapping = {
        "subscription": "Subscription", "subscriptions": "Subscription", "subs": "Subscription", "subscr": "Subscription",
        "bill": "Bills", "bills": "Bills",
        "food": "Food", "dining": "Food", "restaurant": "Food", "coffee": "Food", "cafe": "Food", "cafes": "Food",
        "groceries": "Groceries", "grocery": "Groceries",
        "entertainment": "Entertainment",
        "transport": "Transportation", "transportation": "Transportation", "uber": "Transportation",
        "lyft": "Transportation", "gas": "Transportation", "fuel": "Transportation",
        "utilities": "Utilities", "internet": "Utilities", "electric": "Utilities", "water": "Utilities",
        "health": "Healthcare", "healthcare": "Healthcare",
        "shopping": "Shopping", "retail": "Shopping",
        "debt": "Debt", "loan": "Debt",
        "income": "Income", "salary": "Income",
        "other": "Other",
    }

    if s in mapping:
        std = mapping[s]
    else:
        
        if "subscr" in s:
            std = "Subscription"
        elif "groc" in s:
            std = "Groceries"
        elif any(k in s for k in ("restaur", "dining", "cafe", "coffee", "food")):
            std = "Food"
        elif any(k in s for k in ("transport", "uber", "lyft", "gas", "fuel")):
            std = "Transportation"
        elif any(k in s for k in ("utilit", "internet", "electric", "water")):
            std = "Utilities"
        elif "retail" in s or "shop" in s:
            std = "Shopping"
        elif any(k in s for k in ("health", "care")):
            std = "Healthcare"
        elif any(k in s for k in ("loan", "debt")):
            std = "Debt"
        elif any(k in s for k in ("salary", "pay", "income")):
            std = "Income"
        else:
            std = str(raw).strip().title()
            
    out = dict(row)
    out["category"] = std
    out.pop("Category", None)
    return out


# 4) remove_duplicate_transactions
def remove_duplicate_transactions(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove duplicates after normalization/standardization.

    Duplicate key (stable, order-preserving):
      (date_iso, amount_in_cents, cleaned_description_lower, canonical_category, account_lower)

    Notes:
      • Tolerates 'Amount'/'amount', 'Date'/'date', 'Description'/'description'/'source',
        'Category'/'category', 'Account'/'account'.
      • Does NOT mutate original rows.

    Returns:
      List[Dict[str, Any]]: New list with first occurrences kept.
    """
    seen: set[Tuple[Any, ...]] = set()
    unique: List[Dict[str, Any]] = []

    for idx, row in enumerate(rows):
        # for the key, compute normalized fields without changing the original row
        # -- date (ISO)
        try:
            date_iso = normalize_date_format(row)["date"]
        except Exception:
            # fall back to raw if normalize fails
            date_iso = str(row.get("date", row.get("Date", ""))).strip()

        # -- description (cleaned)
        try:
            desc_clean = clean_transaction_description(row)["description"]
        except Exception:
            desc_clean = str(row.get("description", row.get("Description", row.get("source", "")))).strip()

        # -- category
        try:
            cat_std = standardize_category_names(row)["category"]
        except Exception:
            cat_std = str(row.get("category", row.get("Category", ""))).strip()

        # -- amount (numeric → cents)
        amt_raw = row.get("amount", row.get("Amount", 0))
        try:
            amt_float = float(amt_raw)
        except Exception:
            amt_float = 0.0
        amt_cents = int(round(amt_float * 100))

        # -- account (case-insensitive)
        account = str(row.get("account", row.get("Account", "")) or "").strip().lower()

        key = (date_iso, amt_cents, desc_clean.lower(), cat_std, account)
        if key not in seen:
            seen.add(key)
            unique.append(row)

    return unique
