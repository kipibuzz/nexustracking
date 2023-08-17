import os
import numpy as np
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from snowflake.snowpark.session import Session
import streamlit as st

# snowpark connection
CONNECTION_PARAMETERS = {
    "account": st.secrets['account'], 
    "user": st.secrets['user'],
    "password": st.secrets['password'],
    "database": st.secrets['database'],
    "schema": st.secrets['schema'],
    "warehouse": st.secrets['warehouse'], 
}

# create session
session = Session.builder.configs(CONNECTION_PARAMETERS).create()

# Verify the code and mark attendance
def verify_and_mark_attendance(verification_code):
    attendees = session.read.table("EMP")
    filtered_attendee = attendees.filter(attendees["CODE"] == verification_code).filter(~attendees["ATTENDED"])
    
    if len(filtered_attendee.collect()) > 0:
        attendee_id = filtered_attendee.collect()[0]["ATTENDEE_ID"]
        
        # Update the attendance status
        attendees_to_update = attendees.withColumn("ATTENDED", attendees["ATTENDEE_ID"] == attendee_id)
        attendees_to_update.write.overwrite()
        
        return attendee_id
    else:
        return None

# Streamlit app
st.title('Event Attendance Verification')
verification_code = st.text_input('Enter Verification Code:')
if st.button('Verify'):
    if verification_code:
        attendee_id = verify_and_mark_attendance(verification_code)
        if attendee_id is not None:
            st.success(f'Code verified successfully for Attendee ID: {attendee_id}! They are marked as attended.')
        else:
            st.error('Invalid code.')
