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



attendees = session.read.table("EMP")
# print(attendees.show())
st.write(attendees)


