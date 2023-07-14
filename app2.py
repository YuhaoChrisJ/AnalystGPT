import streamlit as st
import pandas as pd
import sqlite3
import openai

from sql_loader.loaders import mysqlDB, postgresDB, sqliteDB, render_prompt

## All functions

def get_completion(messages, model="gpt-3.5-turbo"):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]

def df_to_db(df1):
        ## Turn csv file into sql database
        global c, conn
        conn = sqlite3.connect('database')
        c = conn.cursor()
        df1.to_sql('t1', conn, if_exists='replace', index=False)

def plot_prompt(result_tb, question):
    # turn df to db
    df_to_db(result_tb)
    # Extract table schema
    schema = pd.read_sql_query(f"PRAGMA table_info('t1')", conn)
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


##### Web component

## Title
st.markdown("""<style> .big-font {
    font-size:50px !important;
    color: navy;
    font-weight: bold;
    font-style: italic;
    font-family: "Lucida Handwriting";
} </style> """, unsafe_allow_html=True)
st.markdown(f'''
    <style>
    section[data-testid="stSidebar"] .css-ng1t4o {{width: 18rem;}}
    </style>
''',unsafe_allow_html=True)

st.sidebar.markdown('<p class="big-font">Analyst GPT</p>', unsafe_allow_html=True)
st.sidebar.write("### Your data anlysis & visualization assistant")

ct1 = st.container()
ct2 = st.container()

## connect to db

db = st.selectbox(
    'What databse you want to connect?',
    ('sqlite', 'mysql', 'postgresql'))
button = st.button("connect")

if db == 'sqlite':
    if "sqlite_state" not in st.session_state:
        st.session_state.sqlite_state = False
    ad = st.text_input('Input your database address')
    if button or st.session_state.sqlite_state:
        st.session_state.sqlite_state = True
        connect = sqliteDB.connect_db(ad)
        db_info = sqliteDB.db_info(connect)
        if db_info != []:
            st.write("Information invalid. Please enter the right information again.")
        else:
            st.write("sucess!")
elif db == 'mysql':
    dbname = st.text_input('database name:')
    user = st.text_input('user:')
    password = st.text_input('password:')
    host = st.text_input('host:')
    if "mysql_state" not in st.session_state:
        st.session_state.mysql_state = False
    if button or st.session_state.mysql_state:
        try:
            st.session_state.mysql_state = True
            connect = mysqlDB.connect_db(host=host, user=user, database=dbname, password=password)
            db_info = mysqlDB.db_info(connect)
            st.write("sucess!")
        except:
            st.write("Information invalid. Please enter the right information again.")
elif db == 'postgresql':
    dbname = st.text_input('database name:')
    user = st.text_input('user:')
    password = st.text_input('password:')
    host = st.text_input('host:')
    port = st.text_input('port:')
    if "postgres_state" not in st.session_state:
        st.session_state.postgres_state = False
    if button or st.session_state.postgres_state:
        try:
            st.session_state.postgres_state = True
            connect = postgresDB.connect_db(dbname=dbname, user=user, password=password, host=host, port=port)
            db_info = postgresDB.db_info(connect)
            st.write("sucess!")
        except:
            st.write("Information invalid. Please enter the right information again.")


## input API/QUERY/DESCRIPTON
api = st.sidebar.text_input("Input your openai API key")
input = st.sidebar.text_area("input your query description")

if "input_state" not in st.session_state:
    st.session_state.input_state = False

if input or st.session_state.input_state:
    try:
        st.session_state.input_state = True
        openai.api_key = api
        prompt = render_prompt(db_info, input)

        query = get_completion(messages=prompt)
        result_tb = pd.read_sql_query(query, connect)
        with ct2:
            st.write("### Your Query Result:",result_tb)
    except:
        st.sidebar.write("Your description is blur or irrelevant. Or you are not connected to a databse.")

input2 = st.sidebar.text_area("What plot you want to see?")
if input2:
    prompt2 = plot_prompt(result_tb, input2)
    response = get_completion(messages=prompt2)
    start = "import"
    end = 'fig.show()'
    start_index = response.find(start)
    end_index = response.find(end)
    code = response[start_index:end_index]

    try:
        exec(code)
    except:
        st.sidebar.write("Your description is blur or irrelevant, please be more specific.")
    with ct1:
        st.write("## Your Analysis Plot:")
        st.plotly_chart(fig)
    del st.session_state['input_state']
