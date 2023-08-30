# import streamlit as st
# import pandas as pd

# ## Loading File
# uploaded_file = st.file_uploader("Choose a CSV file")
# if uploaded_file is not None:
#     #read csv
#     df1=pd.read_csv(uploaded_file)
#     st.write(df1)

#     ## Turn csv file into sql database
#     import sqlite3
#     conn = sqlite3.connect('database')
#     c = conn.cursor()
#     df1.to_sql('t1', conn, if_exists='replace', index=False)




#     ## import Langchain, OpenAI API
#     from langchain.agents import create_sql_agent
#     from langchain.agents.agent_toolkits import SQLDatabaseToolkit
#     from langchain.sql_database import SQLDatabase
#     from langchain.llms.openai import OpenAI
#     from langchain.agents.agent_types import AgentType
#     import os
#     api = st.text_input("input your openai API key")

#     if api:
#         os.environ['OPENAI_API_KEY'] = api

#         ## create db engine
#         from sqlalchemy import create_engine
#         from sqlalchemy.pool import StaticPool
#         eng = create_engine(
#             url='sqlite:///file:memdb1?mode=memory&cache=shared', 
#             poolclass=StaticPool, # single connection for requests
#             creator=lambda: conn)
#         db = SQLDatabase(engine=eng)

#         ## Create sql agent
#         toolkit = SQLDatabaseToolkit(db=db, llm=OpenAI(temperature=0))

#         agent_executor = create_sql_agent(
#             llm=OpenAI(temperature=0),
#             toolkit=toolkit,
#             verbose=True,
#             agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
#         )

#         ## Input description
#         input = st.text_input("input your description")
#         prompt = input + 'don not limit the rows, and you must only return the query clause. Not the answer for this question. '
#         if input:
#             try:
#                 response = agent_executor.run(prompt)
#             except:
#                 st.write("Your description is vague or not relevant to the dataset. Please enter again.")
#             ## execute sql clasue and returning result
#             try:
#                 df2 = pd.read_sql_query(response, conn)
#                 st.write(df2)
#             except:
#                 st.write("Your description is vague or not relevant to the dataset. Please enter again.")
#             input2 = st.text_input("input your description of drawings")            

import streamlit as st

def intro():
    import streamlit as st

    st.write("# Welcome to Streamlit! 👋")
    st.sidebar.success("Select a demo above.")

    st.markdown(
        """
        Streamlit is an open-source app framework built specifically for
        Machine Learning and Data Science projects.

        **👈 Select a demo from the dropdown on the left** to see some examples
        of what Streamlit can do!

        ### Want to learn more?

        - Check out [streamlit.io](https://streamlit.io)
        - Jump into our [documentation](https://docs.streamlit.io)
        - Ask a question in our [community
          forums](https://discuss.streamlit.io)

        ### See more complex demos

        - Use a neural net to [analyze the Udacity Self-driving Car Image
          Dataset](https://github.com/streamlit/demo-self-driving)
        - Explore a [New York City rideshare dataset](https://github.com/streamlit/demo-uber-nyc-pickups)
    """
    )
import streamlit as st

input_data = st.text_area("input")


allow_editing = st.radio("Edit parsed data", [True, False])

if allow_editing:
    output = st.text_area("parsed data", value=input_data)
else:
    st.text(input_data)