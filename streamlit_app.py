import streamlit as st
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from snowflake.snowpark.session import Session

# Snowflake connection parameters
CONNECTION_PARAMETERS = {
    "account": st.secrets['account'], 
    "user": st.secrets['user'],
    "password": st.secrets['password'],
    "database": st.secrets['database'],
    "schema": st.secrets['schema'],
    "warehouse": st.secrets['warehouse'],
}

# Create Snowpark session
session = Session.builder.configs(CONNECTION_PARAMETERS).create()

# Function to verify and mark attendance
def verify_and_mark_attendance(verification_code):
    attendees = session.read.table("EMP")
    attendee = attendees.filter(attendees["CODE"] == verification_code).take(1)

    if len(attendee) > 0 and not attendee[0]["ATTENDED"]:
        attendee_id = attendee[0]["ATTENDEE_ID"]
        attendees_to_update = attendees.filter(attendees["ATTENDEE_ID"] == attendee_id)
        attendees_to_update = attendees_to_update.withColumn("ATTENDED", True)
        attendees_to_update.collect()  # Materialize the update
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

            # Update statistics in EVENT_STATISTICS table
            event_date = session.execute(f"SELECT CURRENT_DATE()")[0][0]
            session.execute(
                f"MERGE INTO EVENT_STATISTICS "
                f"USING (SELECT '{event_date}' AS EVENT_DATE) "
                f"ON EVENT_STATISTICS.EVENT_DATE = '{event_date}' "
                "WHEN MATCHED THEN "
                "UPDATE SET TOTAL_VERIFIED = TOTAL_VERIFIED + 1, TOTAL_ATTENDED = TOTAL_ATTENDED + 1 "
                "WHEN NOT MATCHED THEN "
                f"INSERT (EVENT_DATE, TOTAL_VERIFIED, TOTAL_ATTENDED) VALUES ('{event_date}', 1, 1)"
            )

        else:
            st.error('Invalid code or attendance already marked.')

# Display event statistics
statistics = session.read.table("EVENT_STATISTICS")
st.write(statistics)
