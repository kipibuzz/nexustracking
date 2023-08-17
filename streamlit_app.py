import streamlit as st
import snowflake.connector
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

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
st.title('NexusPassCheck')
 
# ... (rest of your code)

# Custom menu options with emojis
menu_choices = {
    "Verify Attendance": "✅ Verify Attendance",
    "Attendance Statistics": "📊 Attendance Statistics"
}
menu_choice = st.sidebar.radio("Select Page", list(menu_choices.values()))

if menu_choice == menu_choices["Verify Attendance"]:
    # Verify attendance page
    st.header('Verify Attendance')
    verification_code = st.text_input('Enter Verification Code:')
    if st.button('Verify'):
        if verification_code:
            result_message = verify_and_mark_attendance(verification_code)
            if 'successfully' in result_message:
                st.success(result_message + " ✅")
            else:
                st.error(result_message + " ❌")
                
elif menu_choice == menu_choices["Attendance Statistics"]:
    # Attendance statistics page
    st.header('Attendance Statistics')

    # Query attendance data
    attendance_data = query_attendance_data()

    # Generate statistics
    statistics = generate_attendance_statistics(attendance_data)

    total_attended = statistics['Total Attended']
    
    # Create a visually appealing and bold visualization for total attended
    st.write(
        f"<div style='text-align: center;'>"
        f"<h1 style='font-size: 4rem; color: green; font-weight: bold;'>{total_attended}</h1>"
        f"<p style='font-size: 1.5rem;'>Attended</p>"
        f"</div>",
        unsafe_allow_html=True
    )
    
    # Add a divider to create separation
    st.markdown("<hr style='border-top: 2px solid #ccc;'>", unsafe_allow_html=True)
    
    # Create a pie chart for attendance breakdown
    plt.figure(figsize=(8, 6))
    
    labels = ["Attended", "Not Attended"]
    sizes = [total_attended, statistics['Total Not Attended']]
    colors = ["#86bf91", "#e74c3c"]
    
    def func(pct, allvalues):
        absolute = int(pct/100.*np.sum(allvalues))
        return "{:.1f}%\n({:d})".format(pct, absolute)
    
    plt.pie(sizes, labels=labels, colors=colors, autopct=lambda pct: func(pct, sizes))
    plt.axis('equal')  # Equal aspect ratio ensures the pie is circular.
    plt.title("Attendance Breakdown", fontsize=16)
    
    # Display the pie chart
    st.pyplot(plt)
