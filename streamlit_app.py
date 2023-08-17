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
# ... (same as before)

# Streamlit app
st.set_page_config(page_title='Event Attendance Tracking', layout='wide')
st.title('Event Attendance Tracking')

menu = ['Attendance Verification', 'Attendance Statistics']
choice = st.sidebar.selectbox("Select Option", menu)

if choice == 'Attendance Verification':
    verification_code = st.text_input('Enter Verification Code:')
    if st.button('Verify'):
        if verification_code:
            result_message = verify_and_mark_attendance(verification_code)
            if 'successfully' in result_message:
                st.success(result_message)
            else:
                st.error(result_message)

elif choice == 'Attendance Statistics':
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
    df_statistics = pd.DataFrame(statistics, columns=['EVENT_DATE', 'TOTAL_VERIFIED', 'TOTAL_ATTENDED'])
    df_statistics['ATTENDANCE_RATE'] = (df_statistics['TOTAL_ATTENDED'] / df_statistics['TOTAL_VERIFIED']) * 100

    # Display metrics
    st.subheader('Attendance Statistics')
    st.write(df_statistics)

    # Display interactive line chart using Plotly
    fig_statistics = px.line(df_statistics, x='EVENT_DATE', y=['TOTAL_VERIFIED', 'TOTAL_ATTENDED'],
                              title='Attendance Statistics')
    st.plotly_chart(fig_statistics)

    # Display interactive bar chart for attendance rate
    fig_attendance_rate = px.bar(df_statistics, x='EVENT_DATE', y='ATTENDANCE_RATE',
                                  title='Attendance Rate')
    fig_attendance_rate.update_layout(yaxis_title='Attendance Rate (%)')
    st.plotly_chart(fig_attendance_rate)

    cursor_stats.close()
    conn_stats.close()
