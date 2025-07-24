INSERT_CUSTOMER_INTO_USER_TABLE = """INSERT INTO home_pulse_ai.users 
(email, hashed_password, stripe_customer_id, is_paid) VALUES (%s, %s, %s, %s);"""

SELECT_CUSTOMER_FROM_USER_TABLE = """SELECT * FROM home_pulse_ai.users WHERE email=%s;"""

INSERT_CUSTOMER_PROPERTY_INTO_PROPERTY_TABLE = """INSERT INTO home_pulse_ai.properties 
(user_id, postal_code, age, address) VALUES (%s, %s, %s, %s);"""

INSERT_PROPERTY_APPLIANCES_INTO_APPLIANCE_TABLE = """INSERT INTO home_pulse_ai.appliances 
(property_id, appliance_type, age_in_years) VALUES (%s, %s, %s);"""

INSERT_PROPERTY_STRUCTURES_INTO_STRUCTURES_TABLE = """INSERT INTO home_pulse_ai.structures 
(property_id, structure_type, age_in_years) VALUES (%s, %s, %s);"""

SELECT_CUSTOMER_FOR_AUTHENTICATION = """SELECT id, email, hashed_password FROM home_pulse_ai.users 
WHERE email=%s;"""

SELECT_PROPERTIES_BY_USER_ID = """SELECT * FROM home_pulse_ai.properties WHERE user_id=%s;"""

SELECT_PROPERTY_BY_PROPERTY_ID = """SELECT * FROM home_pulse_ai.properties WHERE id=%s;"""

SELECT_APPLIANCES_BY_PROPERTY_ID = """SELECT * FROM home_pulse_ai.appliances WHERE property_id=%s;"""

SELECT_STRUCTURES_BY_PROPERTY_ID = """SELECT * FROM home_pulse_ai.structures WHERE property_id=%s;"""

UPDATE_FIRST_AND_LAST_OF_CUSTOMER = """UPDATE home_pulse_ai.users SET first_name=%s, last_name=%s WHERE id=%s;"""

SELECT_CUSTOMER_FIRST_AND_LAST = """SELECT first_name, last_name FROM home_pulse_ai.users WHERE id=%s;"""
