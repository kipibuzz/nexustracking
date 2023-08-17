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
    filtered_attendee = attendees.filter(attendees["CODE"] == verification_code).filter(~attendees["ATTENDED"])
    if len(filtered_attendee.collect()) > 0:
        attendee_id = filtered_attendee.collect()[0]["ATTENDEE_ID"]
        attendees.write \
            .overwrite() \
            .filter(attendees["CODE"] == verification_code) \
            .filter(~attendees["ATTENDED"]) \
            .set("ATTENDED", True)
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
    f"UPDATE NEXUS.ATTENDENCE.EVENT_STATISTICS SET TOTAL_VERIFIED = TOTAL_VERIFIED + 1, TOTAL_ATTENDED = TOTAL_ATTENDED + 1 WHERE EVENT_DATE = CURRENT_DATE()"
)

        else:
            st.error('Invalid code or code already used.')
# # Display the attendee table
attendees = session.read.table("EMP")
#st.write(attendees)
# Display event statistics
statistics = session.read.table("Event_Statistics")
st.write(statistics)

