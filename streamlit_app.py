import os
import glob
import numpy as np
import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from snowflake.snowpark.session import Session
import streamlit as st
import pandas as pd

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



# attendees = session.read.table("EMP")
# # print(attendees.show())
# st.write(attendees)
 
# Verify the code and mark attendance
def verify_and_mark_attendance(verification_code):
    attendees = session.read.table("EMP")
    filtered_attendee = attendees.filter(attendees["code"] == verification_code).filter(attendees["attended"] == False)
    if len(filtered_attendee.collect()) > 0:
        attendee_id = filtered_attendee.collect()[0]["attendee_id"]
        attendees.write \
            .overwrite() \
            .filter(attendees["code"] == verification_code) \
            .filter(attendees["attended"] == False) \
            .set("attended", True)
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
            # Increment statistics in Event_Statistics table
            session.execute(
                f"UPDATE Event_Statistics SET total_verified = total_verified + 1, total_attended = total_attended + 1 WHERE event_date = CURRENT_DATE()"
            )
        else:
            st.error('Invalid code or code already used.')
# # Display the attendee table
# attendees = session.read.table("EMP")
st.write(attendees)
# Display event statistics
statistics = session.read.table("Event_Statistics")
st.write(statistics)

