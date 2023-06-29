import streamlit as st
import pandas as pd

## Loading File
uploaded_file = st.file_uploader("Choose a CSV file")
if uploaded_file is not None:
    #read csv
    df1=pd.read_csv(uploaded_file)
    st.write(df1)

    ## Turn csv file into sql database
    import sqlite3
    conn = sqlite3.connect('database')
    c = conn.cursor()
    df1.to_sql('t1', conn, if_exists='replace', index=False)




    ## import Langchain, OpenAI API
    from langchain.agents import create_sql_agent
    from langchain.agents.agent_toolkits import SQLDatabaseToolkit
    from langchain.sql_database import SQLDatabase
    from langchain.llms.openai import OpenAI
    from langchain.agents.agent_types import AgentType
    import os

    os.environ['OPENAI_API_KEY'] = "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"

    ## create db engine
    from sqlalchemy import create_engine
    from sqlalchemy.pool import StaticPool
    eng = create_engine(
        url='sqlite:///file:memdb1?mode=memory&cache=shared', 
        poolclass=StaticPool, # single connection for requests
        creator=lambda: conn)
    db = SQLDatabase(engine=eng)

    ## Create sql agent
    toolkit = SQLDatabaseToolkit(db=db, llm=OpenAI(temperature=0))

    agent_executor = create_sql_agent(
        llm=OpenAI(temperature=0),
        toolkit=toolkit,
        verbose=False,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    )

    ## Input description
    input = st.text_input("input your description")
    prompt = input + ', and return me the query clause.'
    if input:
        response = agent_executor.run(prompt)

        ## execute sql clasue and returning result
        t2 = c.execute(response)
        df2 = pd.DataFrame(t2.fetchall())
        st.write(df2)