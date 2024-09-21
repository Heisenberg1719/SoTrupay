# Query to register a new user in the user_demographics table
register_user_query = """
    INSERT INTO user_demographics (
        username, email, phone_number, hashed_password, adhaar_number, pan_number, 
        dob, gender, address, pincode
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""

# Query to get a user's username by their phone number
get_user_query = """
    SELECT username 
    FROM user_demographics 
    WHERE phone_number = %s;
"""

# Query to authenticate a user by retrieving their hashed password
authenticate_user_query = """
    SELECT hashed_password AS password 
    FROM user_demographics 
    WHERE username = %s;
"""

# Query to get the user's payout wallet balance by their username
get_payout_wallet_by_username = """
    SELECT PayOut_Wallet
    FROM wallet
    WHERE username = %s;
"""

# Query to check the user's transaction rights and t_pin for validation
get_kyc_status_query = """
    SELECT transaction_right, t_pin 
    FROM user_demographics 
    WHERE username = %s;
"""

# Query to insert a new transaction request into the transaction_request table
transaction_request_insert_query = """
    INSERT INTO transaction_request (
        username, beneficiary_name, phone, bank_account, ifsc, amount, 
        transfer_id, wallet_balance
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
"""

# Query to retrieve a token from the creds table for the Neobiz integration
get_neobiz_token_query = """
    SELECT * 
    FROM creds 
    WHERE provider = %s;
"""
