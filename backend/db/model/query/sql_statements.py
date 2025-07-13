INSERT_CUSTOMER_INTO_USER_TABLE = """INSERT INTO home_pulse_ai.users 
(email, hashed_password, stripe_customer_id, is_paid) VALUES (%s, %s, %s, %s)"""

SELECT_CUSTOMER_FROM_USER_TABLE = """SELECT * FROM home_pulse_ai.users WHERE email=%s"""
