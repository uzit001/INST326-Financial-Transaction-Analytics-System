### DEMONSTRATION OF DATA VALIDATION FUNCTION ###

def test_validation_functions():
    """Test all validation functions."""
    
    print("="*60)
    print("Testing Data Validation Functions")
    print("="*60)
    
    # Test 1: Amount validation
    print("\n1. Testing validate_transaction_amount():")
    print(f"   Valid amount (50.00): {validate_transaction_amount(50.00)}")
    print(f"   Invalid amount (-10): {validate_transaction_amount(-10.00)}")
    
    # Test 2: Date validation
    print("\n2. Testing validate_date_format():")
    print(f"   Valid date (2025-10-11): {validate_date_format('2025-10-11')}")
    print(f"   Invalid date (2025-13-45): {validate_date_format('2025-13-45')}")
    
    # Test 3: Category validation
    print("\n3. Testing validate_category():")
    print(f"   Valid category (Subscription): {validate_category('Subscription')}")
    print(f"   Invalid category (Random): {validate_category('Random')}")
    
    # Test 4: Full transaction validation
    print("\n4. Testing validate_transaction_data():")
    transaction = {
        'amount': 49.99,
        'date': '2025-10-11',
        'category': 'Subscription',
        'description': 'Netflix',
        'account': 'Checking'
    }
    is_valid, errors = validate_transaction_data(transaction)
    print(f"   Valid transaction: {is_valid}")
    print(f"   Errors: {errors}")
    
    print("\n" + "="*60)
    print("All tests completed!")
    print("="*60)

if __name__ == "__main__":
    test_validation_functions()


