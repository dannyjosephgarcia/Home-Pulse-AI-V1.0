INSERT_CUSTOMER_INTO_USER_TABLE = """INSERT INTO home_pulse_ai.users 
(email, hashed_password, stripe_customer_id, is_paid, company_id) VALUES (%s, %s, %s, %s, %s);"""

SELECT_CUSTOMER_FROM_USER_TABLE = """SELECT * FROM home_pulse_ai.users WHERE email=%s;"""

INSERT_CUSTOMER_PROPERTY_INTO_PROPERTY_TABLE = """INSERT INTO home_pulse_ai.properties 
(user_id, street, city, state, zip, age, address) VALUES (%s, %s, %s, %s, %s, %s, %s);"""

INSERT_PROPERTY_APPLIANCES_INTO_APPLIANCE_TABLE = """INSERT INTO home_pulse_ai.appliances
(property_id, unit_id, appliance_type, appliance_brand, appliance_model, age_in_years, estimated_replacement_cost) VALUES (%s, %s, %s, %s, %s, %s, %s);"""

INSERT_PROPERTY_STRUCTURES_INTO_STRUCTURES_TABLE = """INSERT INTO home_pulse_ai.structures
(property_id, structure_type, age_in_years) VALUES (%s, %s, %s);"""

INSERT_UNITS_INTO_UNITS_TABLE = """INSERT INTO home_pulse_ai.units
(property_id, unit_number) VALUES (%s, %s);"""

SELECT_CUSTOMER_FOR_AUTHENTICATION = """SELECT id, email, hashed_password, first_name, last_name, company_id 
FROM home_pulse_ai.users WHERE email=%s;"""

SELECT_PROPERTIES_BY_USER_ID = """SELECT
    p.id,
    p.user_id,
    p.age,
    p.street,
    p.city,
    p.state,
    p.zip,
    p.address,
    p.created_at,
    CASE WHEN EXISTS (SELECT 1 FROM home_pulse_ai.units u WHERE u.property_id = p.id AND u.unit_number IS NOT NULL) THEN 1 ELSE 0 END as is_multifamily
FROM home_pulse_ai.properties p
WHERE p.user_id = %s;"""

SELECT_ADDRESSES_BY_USER_ID = """SELECT id, address FROM home_pulse_ai.properties WHERE user_id=%s;"""

SELECT_PROPERTY_BY_PROPERTY_ID = """SELECT
    p.id,
    p.user_id,
    p.age,
    p.street,
    p.city,
    p.state,
    p.zip,
    p.address,
    p.created_at,
    CASE WHEN EXISTS (
        SELECT 1 FROM home_pulse_ai.units u
        WHERE u.property_id = p.id
        AND u.unit_number IS NOT NULL
    ) THEN 1 ELSE 0 END as is_multifamily
FROM home_pulse_ai.properties p
WHERE p.id = %s;"""

SELECT_APPLIANCES_BY_PROPERTY_ID = """SELECT * FROM home_pulse_ai.appliances WHERE property_id=%s;"""

SELECT_STRUCTURES_BY_PROPERTY_ID = """SELECT * FROM home_pulse_ai.structures WHERE property_id=%s;"""

UPDATE_FIRST_AND_LAST_OF_CUSTOMER = """UPDATE home_pulse_ai.users SET first_name=%s, last_name=%s WHERE id=%s;"""

SELECT_CUSTOMER_FIRST_AND_LAST = """SELECT first_name, last_name, email FROM home_pulse_ai.users WHERE id=%s;"""

UPDATE_IS_PAID_STATUS_OF_CUSTOMER = """UPDATE home_pulse_ai.users SET is_paid=1, stripe_customer_id=%s WHERE id=%s;"""

SELECT_CUSTOMER_EMAIL_FIRST_AND_LAST = """SELECT email, first_name, last_name FROM home_pulse_ai.users WHERE id=%s;"""

SELECT_IS_PAID_STATUS_FOR_CUSTOMER = """SELECT is_paid, email, first_name, last_name 
FROM home_pulse_ai.users WHERE id=%s;"""

SELECT_TENANT_INFORMATION_BY_PROPERTY_ID = """SELECT * FROM home_pulse_ai.tenants WHERE property_id=%s;"""

INSERT_TENANT_INFORMATION_INTO_TENANTS_TABLE = """INSERT INTO home_pulse_ai.tenants (property_id, first_name, 
last_name, contract_start_date, contract_end_date, monthly_rent, phone_number) VALUES (%s, %s, %s, %s, %s, %s, %s);"""

UPDATE_APPLIANCE_INFORMATION = """UPDATE home_pulse_ai.appliance_information 
SET appliance_price=%s WHERE appliance_type=%s;"""

SELECT_APPLIANCE_INFORMATION_FOR_REPLACEMENT_COST = """SELECT appliance_type, appliance_price 
FROM home_pulse_ai.appliance_information"""

SELECT_PROPERTY_IMAGE_URL = """SELECT s3_key FROM home_pulse_ai.property_images 
WHERE user_id=%s AND property_id=%s;"""

INSERT_PROPERTY_IMAGE_URL = """INSERT INTO home_pulse_ai.property_images (user_id, property_id, s3_key) 
VALUES (%s, %s, %s);"""

SELECT_INVITATION_INFORMATION = """SELECT company_id, email, status, expires_at 
FROM home_pulse_ai.invitations WHERE token=%s;"""

SELECT_COMPANY_STATUS = """SELECT is_active FROM home_pulse_ai.companies WHERE id=%s;"""

UPDATE_INVITATION_INFORMATION = """UPDATE home_pulse_ai.invitations SET accepted_at=%s WHERE email=%s;"""

INSERT_SUBSCRIPTION_INFORMATION = """INSERT INTO home_pulse_ai.subscriptions 
(user_id, status, period_start, period_end) VALUES (%s, %s, NOW(), %s);"""

UPDATE_SUBSCRIPTION_STATUS = """UPDATE home_pulse_ai.subscriptions SET status='active' WHERE user_id=%s;"""

SELECT_SUBSCRIPTION_STATUS = """SELECT status, period_end FROM home_pulse_ai.subscriptions WHERE user_id=%s"""

SELECT_STRIPE_CUSTOMER_ID = """SELECT stripe_customer_id FROM home_pulse_ai.users WHERE id=%s;"""

UPDATE_SUBSCRIPTION_STATUS_FOR_DELETION = """UPDATE home_pulse_ai.subscriptions 
SET status='canceled' WHERE user_id=%s;"""

SELECT_USER_ID_BY_STRIPE_CUSTOMER = """SELECT id FROM home_pulse_ai.users WHERE stripe_customer_id=%s;"""

UPDATE_SUBSCRIPTION_TABLE_UPON_PAYMENT_COMPLETION = """UPDATE home_pulse_ai.subscriptions SET status='active', 
subscription_id=%s WHERE user_id=%s;"""

SELECT_SUBSCRIPTION_INFORMATION = """SELECT status, subscription_id, period_end FROM home_pulse_ai.subscriptions 
WHERE user_id=%s;"""

SELECT_HOME_BOT_EMBEDDING_INFORMATION = """SELECT id, brand, model, category, avg_lifespan_years 
FROM home_pulse_ai.home_bot_training_information;"""

UPDATE_FORECASTED_REPLACEMENT_DATE = """UPDATE home_pulse_ai.appliances 
SET forecasted_replacement_date=%s WHERE property_id=%s AND appliance_type=%s;"""

UPDATE_APPLIANCE_INFORMATION_BULK = """UPDATE home_pulse_ai.appliances
SET age_in_years=%s, estimated_replacement_cost=%s, forecasted_replacement_date=%s, appliance_brand=%s, appliance_model=%s
WHERE property_id=%s AND appliance_type=%s;"""

UPDATE_STRUCTURE_INFORMATION_BULK = """UPDATE home_pulse_ai.structures 
SET age_in_years=%s, estimated_replacement_cost=%s, forecasted_replacement_date=%s 
WHERE property_id=%s AND structure_type=%s;"""

INSERT_PROPERTY_INFORMATION_BULK = """"""

SELECT_PROPERTY_INFORMATION_BY_USER_FOR_MANAGEMENT_TAB = """SELECT ap.id,
       ap.property_id,
       ap.appliance_type AS component_name,
       ap.age_in_years,
       ap.estimated_replacement_cost,
       ap.forecasted_replacement_date,
       pr.address
FROM appliances AS ap
JOIN properties AS pr
  ON ap.property_id = pr.id
WHERE ap.forecasted_replacement_date <= CURDATE() + INTERVAL 3 MONTH
  AND ap.property_id IN (SELECT id FROM properties WHERE user_id = %s)

UNION

SELECT sp.id,
       sp.property_id,
       sp.structure_type AS component_name,
       sp.age_in_years,
       sp.estimated_replacement_cost,
       sp.forecasted_replacement_date,
       pr.address
FROM structures AS sp
JOIN properties AS pr
  ON sp.property_id = pr.id
WHERE sp.forecasted_replacement_date <= CURDATE() + INTERVAL 3 MONTH
  AND sp.property_id IN (SELECT id FROM properties WHERE user_id = %s)

ORDER BY property_id;"""

GET_UNITS_BY_PROPERTY_ID = """SELECT unit_id, unit_number, property_id, created_at, updated_at
FROM home_pulse_ai.units
WHERE property_id = %s
ORDER BY unit_number ASC;"""

GET_APPLIANCES_BY_UNIT_ID = """SELECT id, property_id, unit_id, appliance_type, appliance_brand, appliance_model,
age_in_years, estimated_replacement_cost, forecasted_replacement_date
FROM home_pulse_ai.appliances
WHERE unit_id = %s
ORDER BY appliance_type ASC;"""

VERIFY_UNIT_OWNERSHIP = """SELECT u.unit_id
FROM home_pulse_ai.units u
JOIN home_pulse_ai.properties p ON u.property_id = p.id
WHERE u.unit_id = %s AND p.user_id = %s;"""
