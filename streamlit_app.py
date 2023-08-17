import os
import glob
import numpy as np
import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from snowflake.snowpark.session import Session
import streamlit as st
import pandas as pd

# import streamlit as st
# import snowflake.connector

# Snowflake connection parameters
CONNECTION_PARAMETERS = {
    "account": st.secrets['account'],
    "user": st.secrets['user'],
    "password": st.secrets['password'],
    "database": st.secrets['database'],
    "schema": st.secrets['schema'],
    "warehouse": st.secrets['warehouse'],
}

# Create Snowflake connection
conn = snowflake.connector.connect(**CONNECTION_PARAMETERS)

# Verify the code and mark attendance
def verify_and_mark_attendance(verification_code):
    cursor = conn.cursor()

    # Perform the necessary SQL operations to update attendees and event statistics
    try:
        cursor.execute(
            f"UPDATE EMP SET ATTENDED = TRUE WHERE CODE = '{verification_code}' AND NOT ATTENDED"
        )

        cursor.execute(
            f"UPDATE EVENT_STATISTICS SET TOTAL_VERIFIED = TOTAL_VERIFIED + 1, TOTAL_ATTENDED = TOTAL_ATTENDED + 1 WHERE EVENT_DATE = CURRENT_DATE()"
        )

        conn.commit()
        return True
    except snowflake.connector.errors.DatabaseError as e:
        print("Error:", e)
        conn.rollback()
        return False
    finally:
        cursor.close()

# Streamlit app
st.title('Event Attendance Verification')
verification_code = st.text_input('Enter Verification Code:')
if st.button('Verify'):
    if verification_code:
        if verify_and_mark_attendance(verification_code):
            st.success(f'Code verified successfully! They are marked as attended.')
        else:
            st.error('Invalid code or code already used.')
