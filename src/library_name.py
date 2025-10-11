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
