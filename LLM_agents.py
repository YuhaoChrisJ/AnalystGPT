import pandas as pd
import sqlite3
import streamlit as st
import openai

@st.cache_data
def get_completion(messages, model="gpt-3.5-turbo"):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]

@st.cache_data
def df_to_db(df1, table_name):
    ## Turn csv file into sql database
    global c, conn
    conn = sqlite3.connect('database')
    c = conn.cursor()
    df1.to_sql(table_name, conn, if_exists='replace', index=False)

@st.cache_data
def get_schema(table_name):
    schema = pd.read_sql_query(f"PRAGMA table_info({table_name})", conn)
    schema_str = ''
    for index, row in schema.iterrows():
        column_info = f"name={row['name']}, datatype={row['type']};\n"
        schema_str = schema_str + column_info
    return schema_str


# 1.code plot agent
@st.cache_data
def plot_prompt(result_tb, question):
    # turn df to db
    df_to_db(result_tb, 'result_tb')
    # Extract table schema
    schema_str = get_schema('result_tb')
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

# 2.extract plot info agent
@st.cache_data
def plot_info(result_tb, question):
    # turn df to db
    df_to_db(result_tb, 'result_tb')
    # Extract table schema
    schema_str = get_schema('result_tb')

    query_system_prompt = "You are a helpful assistant that defines what columns are needed based on description of plots. You must only return column names as a list in python. Wrap your answer in square bracket."
    query_prompt = f"""
    Given a pandas dataframe:
    result_tb
    With schema:
    {schema_str}
    Return only column names as a python list based on this description:
    {question}"""

    messages = [{"role": "system", "content": query_system_prompt}, {"role": "user", "content": query_prompt}]
    return messages

@st.cache_data
def describ_plot(plot_data, question):
    data_str = plot_data.to_string(index=False)

    # plot description Prompt
    query_system_prompt = "You are a helpful assistant that write description about the trend of the data in a plot. You will be given a short description of plot and the data frame used in that plot."
    query_prompt = f"""
    Given the used data frame:
    {data_str}
    Given the short description:
    {question}
    Write a description about the trend of the data in this plot in 100 words."""

    messages = [{"role": "system", "content": query_system_prompt}, {"role": "user", "content": query_prompt}]
    return messages

@st.cache_data
def describ_df(df):
    data_str = df.to_string(index=False)

    # plot description Prompt
    query_system_prompt = "You are a helpful assistant that write introduction for a report. You will be given a dataframe that related to this report. Only return plain text."
    query_prompt = f"""
    Given the used data frame:
    {data_str}
    Write a introduction of a report about this dataframe in 100 words.
    Return text in plain style."""

    messages = [{"role": "system", "content": query_system_prompt}, {"role": "user", "content": query_prompt}]
    return messages