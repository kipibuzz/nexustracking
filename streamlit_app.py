import streamlit as st
import snowflake.connector

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
conn = snowflake.connector.connect(CONNECTION_PARAMETERS)

# Function to verify and mark attendance
def verify_and_mark_attendance(verification_code):
    cursor = conn.cursor()

    # Check if attendee exists and has not attended
    cursor.execute(
        f"SELECT ATTENDEE_ID, ATTENDED FROM EMP WHERE CODE = '{verification_code}'"
    )
    row = cursor.fetchone()
    if row and not row[1]:
        attendee_id = row[0]

        # Mark attendance
        cursor.execute(
            f"UPDATE EMP SET ATTENDED = TRUE WHERE ATTENDEE_ID = '{attendee_id}'"
        )
        conn.commit()

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
            st.error('Invalid code or attendance already marked.')

# Close Snowflake connection
conn.close()

# Display event statistics
conn = snowflake.connector.connect(**CONNECTION_PARAMETERS)
cursor = conn.cursor()
cursor.execute("SELECT * FROM EVENT_STATISTICS")
statistics = cursor.fetchall()
st.write(statistics)
cursor.close()
conn.close()
