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

# Function to verify and mark attendance
def verify_and_mark_attendance(verification_code):
    conn = snowflake.connector.connect(CONNECTION_PARAMETERS)
    cursor = conn.cursor()

    # Check if attendee exists and has not attended
    cursor.execute(
        f"SELECT ATTENDEE_ID, ATTENDED FROM EMP WHERE CODE = '{verification_code}'"
    )
    row = cursor.fetchone()
    if row:
        attendee_id, attended = row
        if attended:
            message = f'Attendance already marked for Attendee ID: {attendee_id}'
        else:
            # Mark attendance
            cursor.execute(
                f"UPDATE EMP SET ATTENDED = TRUE WHERE ATTENDEE_ID = '{attendee_id}'"
            )
            conn.commit()
            message = f'Code verified successfully for Attendee ID: {attendee_id}! They are marked as attended.'
    else:
        message = 'Invalid code'

    cursor.close()
    conn.close()
    return message

# Streamlit app
st.title('Event Attendance Verification')
verification_code = st.text_input('Enter Verification Code:')
if st.button('Verify'):
    if verification_code:
        result_message = verify_and_mark_attendance(verification_code)
        if 'successfully' in result_message:
            st.success(result_message)
        else:
            st.error(result_message)

# Display event statistics
conn_stats = snowflake.connector.connect(CONNECTION_PARAMETERS)
cursor_stats = conn_stats.cursor()
cursor_stats.execute("SELECT * FROM EVENT_STATISTICS")
statistics = cursor_stats.fetchall()
st.write(statistics)
cursor_stats.close()
conn_stats.close()
