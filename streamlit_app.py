import streamlit as st
import snowflake.connector
import pandas as pd
import matplotlib.pyplot as plt

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

# Function to query attendance data
def query_attendance_data():
    conn = snowflake.connector.connect(
        user=CONNECTION_PARAMETERS['user'],
        password=CONNECTION_PARAMETERS['password'],
        account=CONNECTION_PARAMETERS['account'],
        warehouse=CONNECTION_PARAMETERS['warehouse'],
        database=CONNECTION_PARAMETERS['database'],
        schema=CONNECTION_PARAMETERS['schema']
    )
    cursor = conn.cursor()

    # Query attendance data
    cursor.execute("SELECT ATTENDEE_ID, ATTENDED FROM EMP")
    data = cursor.fetchall()

    cursor.close()
    conn.close()
    return data

# Function to generate attendance statistics
def generate_attendance_statistics(data):
    total_attendees = len(data)
    total_attended = sum(1 for _, attended in data if attended)
    total_not_attended = total_attendees - total_attended
    return {
        "Total Attendees": total_attendees,
        "Total Attended": total_attended,
        "Total Not Attended": total_not_attended,
    }

# Streamlit app
st.title('Event Attendance Management')

# Navigation menu
menu_choice = st.sidebar.radio("Select Page", ["Verify Attendance", "Attendance Statistics"])

if menu_choice == "Verify Attendance":
    # Verify attendance page
    st.header('Verify Attendance')
    verification_code = st.text_input('Enter Verification Code:')
    if st.button('Verify'):
        if verification_code:
            result_message = verify_and_mark_attendance(verification_code)
            if 'successfully' in result_message:
                st.success(result_message)
            else:
                st.error(result_message)

 

# ... (existing code)

# ... (existing code)

elif menu_choice == "Attendance Statistics":
    # Attendance statistics page
    st.header('Attendance Statistics')

    # Query attendance data
    attendance_data = query_attendance_data()

    # Generate statistics
    statistics = generate_attendance_statistics(attendance_data)

    # Create a pie chart for attendance breakdown
    plt.figure(figsize=(6, 6))
    plt.pie(statistics.values(), labels=statistics.keys(), autopct='%1.1f%%', colors=["#86bf91", "#f1c40f", "#e74c3c"])
    plt.title("Attendance Breakdown")
    plt.axis('equal')  # Equal aspect ratio ensures the pie is circular.
    
    st.subheader('Attendance Breakdown')
    st.pyplot(plt)
    
    # Display attendance counts
    st.subheader('Attendance Counts')
    st.write(f"Total Attendees: {statistics['Total Attendees']}")
    st.write(f"Total Attended: {statistics['Total Attended']}")
    st.write(f"Total Not Attended: {statistics['Total Not Attended']}")



