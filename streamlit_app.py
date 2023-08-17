import streamlit as st
import snowflake.connector
import pandas as pd
import plotly.express as px

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
st.set_page_config(page_title='Attendance Verification App', layout='wide')

# Sidebar navigation
menu = ["Verification", "Attendance Statistics", "Attendance Trends"]
choice = st.sidebar.selectbox("Select Option", menu)

# Page 1: Verification Page
if choice == "Verification":
    st.title('Event Attendance Verification')
    verification_code = st.text_input('Enter Verification Code:')
    if st.button('Verify'):
        if verification_code:
            result_message = verify_and_mark_attendance(verification_code)
            if 'successfully' in result_message:
                st.success(result_message)
            else:
                st.error(result_message)

# Page 2: Attendance Statistics
if choice == "Attendance Statistics":
    st.title('Attendance Statistics')
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

    # Creating a DataFrame for the statistics
    df_statistics = pd.DataFrame(statistics, columns=["EVENT_DATE", "TOTAL_VERIFIED", "TOTAL_ATTENDED"])
    st.dataframe(df_statistics)

# Page 3: Attendance Trends
if choice == "Attendance Trends":
    st.title('Attendance Trends')
    conn_trends = snowflake.connector.connect(
            user=CONNECTION_PARAMETERS['user'],
            password=CONNECTION_PARAMETERS['password'],
            account=CONNECTION_PARAMETERS['account'],
            warehouse=CONNECTION_PARAMETERS['warehouse'],
            database=CONNECTION_PARAMETERS['database'],
            schema=CONNECTION_PARAMETERS['schema']
        )
    cursor_trends = conn_trends.cursor()
    cursor_trends.execute("SELECT * FROM EVENT_STATISTICS")
    trends = cursor_trends.fetchall()
    cursor_trends.close()
    conn_trends.close()

    # Creating a DataFrame for the trends
    df_trends = pd.DataFrame(trends, columns=["EVENT_DATE", "TOTAL_VERIFIED", "TOTAL_ATTENDED"])
    
    # Creating an interactive line chart using Plotly
    fig_trends = px.line(df_trends, x='EVENT_DATE', y=['TOTAL_VERIFIED', 'TOTAL_ATTENDED'], title='Attendance Trends')
    st.plotly_chart(fig_trends)
