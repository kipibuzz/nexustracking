import streamlit as st
import snowflake.connector
import matplotlib.pyplot as plt
import pandas as pd

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
    conn = snowflake.connector.connect(
        user=CONNECTION_PARAMETERS['user'],
        password=CONNECTION_PARAMETERS['password'],
        account=CONNECTION_PARAMETERS['account'],
        warehouse=CONNECTION_PARAMETERS['warehouse'],
        database=CONNECTION_PARAMETERS['database'],
        schema=CONNECTION_PARAMETERS['schema']
    )
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
st.set_page_config(
    page_title="Event Attendance App",
    layout="wide"
)

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
conn_stats = snowflake.connector.connect(
        user=CONNECTION_PARAMETERS['user'],
        password=CONNECTION_PARAMETERS['password'],
        account=CONNECTION_PARAMETERS['account'],
        warehouse=CONNECTION_PARAMETERS['warehouse'],
        database=CONNECTION_PARAMETERS['database'],
        schema=CONNECTION_PARAMETERS['schema']
    )
cursor_stats = conn_stats.cursor()
cursor_stats.execute("SELECT * FROM EVENT_STATISTICS")
statistics = cursor_stats.fetchall()
cursor_stats.close()
conn_stats.close()

# Display statistics
st.title('Event Statistics')

# Create a DataFrame for the statistics
statistics_df = pd.DataFrame(statistics, columns=['Event Date', 'Total Verified', 'Total Attended'])
st.write(statistics_df)

# Display a bar chart for statistics
fig, ax = plt.subplots()
statistics_df.plot(x='Event Date', y=['Total Verified', 'Total Attended'], kind='bar', ax=ax)
st.pyplot(fig)
