import streamlit as st
import pandas as pd
import sqlite3
import openai

## All functions
def df_to_db(df1):
        ## Turn csv file into sql database
        global c, conn
        conn = sqlite3.connect('database')
        c = conn.cursor()
        df1.to_sql('t1', conn, if_exists='replace', index=False)

        
def query_prompt(question):
    # Extract table schema
    schema = pd.read_sql_query(f"PRAGMA table_info('t1')", conn)
    schema_str = ''
    for index, row in schema.iterrows():
        column_info = f"name={row['name']}, datatype={row['type']};\n"
        schema_str = schema_str + column_info
    ## Render Prompt
    query_system_prompt = "You are a helpful assistant that only writes SQL SELECT queries. Reply only with SQL queries."
    query_prompt = f"""
    Given a table name:
    t1
    With schema:
    {schema_str}
    Write a SQL query to answer the following question:
    {question}"""

    messages = [{"role": "system", "content": query_system_prompt}, {"role": "user", "content": query_prompt}]
    return messages

def get_completion(messages, model="gpt-3.5-turbo"):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]

def plot_prompt(result_tb, question):
    # Save table to database
    result_tb.to_sql('t2', conn, if_exists='replace', index=False)
    # Extract table schema
    schema = pd.read_sql_query(f"PRAGMA table_info('t2')", conn)
    schema_str = ''
    for index, row in schema.iterrows():
        column_info = f"name={row['name']}, datatype={row['type']};\n"
        schema_str = schema_str + column_info

    # Render Prompt
    query_system_prompt = "You are a helpful assistant that only writes Python code using plotly library. You must reply only with Python code, wrap your code in triple backquotes."
    query_prompt = f"""
    Given a pandas dataframe:
    result_tb
    With schema:
    {schema_str}
    Based on this dataframe, write some python code using plotly to meet the following request:
    {question}"""

    messages = [{"role": "system", "content": query_system_prompt}, {"role": "user", "content": query_prompt}]
    return messages






## Web component
uploaded_file = st.sidebar.file_uploader("Choose a CSV file")
if uploaded_file is not None:
    df1=pd.read_csv(uploaded_file)
    if not st.sidebar.checkbox("Hide orginal data", False):
        st.write("## Your Dataset:", df1)
    df_to_db(df1)

api = st.sidebar.text_input("input your openai API key")
input = st.sidebar.text_input("input your query description")
if input:
    openai.api_key = api
    prompt = query_prompt(input)
    query = get_completion(messages=prompt)
    result_tb = pd.read_sql_query(query, conn)
    if not st.sidebar.checkbox("Hide query result", False):
        st.write("## Your Query Result:",result_tb)

input2 = st.sidebar.text_input("What plot you want to see?")
if input2:
    prompt2 = plot_prompt(result_tb, input2)
    response = get_completion(messages=prompt2)
    start = "import"
    end = 'fig.show()'
    start_index = response.find(start)
    end_index = response.find(end)
    code = response[start_index:end_index]

    exec(code)
    st.write("## Your Analysis Plot:")
    st.plotly_chart(fig)
