import streamlit as st
import pandas as pd
import openai
import ast
import plotly.io as pio

from sql_loader.loaders import mysqlDB, postgresDB, sqliteDB, render_prompt
from LLM_agents import get_completion, plot_prompt, plot_info, describ_plot, df_to_db, get_schema

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
    ('mysql', 'sqlite', 'postgresql','upload data'))
button = st.button("connect")

if db == 'sqlite':
    if 'ad_list' not in st.session_state:
        st.session_state.ad_list = []
    ad = st.text_input('Input your database address')
    if ad:
        st.session_state.ad_list.insert(0, ad)


    if "sqlite_state" not in st.session_state:
        st.session_state.sqlite_state = False
    if button or st.session_state.sqlite_state:
        st.session_state.sqlite_state = True
        connect = sqliteDB.connect_db(st.session_state.ad_list[0])
        db_info = sqliteDB.db_info(connect)
        if db_info == {}:
            st.write("Information invalid. Please enter the right information again.")
        else:
            st.write("sucess!")
elif db == 'mysql':
    # save db connection info into session_state
    if 'mysql_host' not in st.session_state:
        st.session_state.mysql_db = []
        st.session_state.mysql_user = []
        st.session_state.mysql_password = []
        st.session_state.mysql_host = []
    dbname = st.text_input('database name:')
    if dbname:
        st.session_state.mysql_db.insert(0, dbname)

    user = st.text_input('user:')
    if user:
        st.session_state.mysql_user.insert(0, user)

    password = st.text_input('password:')
    if password:
        st.session_state.mysql_password.insert(0, password)

    host = st.text_input('host:')
    if host:
        st.session_state.mysql_host.insert(0, host)

    #connect to db
    if "mysql_state" not in st.session_state:
        st.session_state.mysql_state = False
    if button or st.session_state.mysql_state:
        try:
            st.session_state.mysql_state = True
            connect = mysqlDB.connect_db(host=st.session_state.mysql_host[0], user=st.session_state.mysql_user[0], database=st.session_state.mysql_db[0], password=st.session_state.mysql_password[0])
            st.write("sucess!")
            db_info = mysqlDB.db_info(connect)
        except:
            st.write("Information invalid. Please enter the right information again.")
elif db == 'postgresql':
    if 'post_port' not in st.session_state:
        st.session_state.post_db = []
        st.session_state.post_user = []
        st.session_state.post_password = []
        st.session_state.post_host = []
        st.session_state.post_port = []
    dbname = st.text_input('database name:')
    if dbname:
        st.session_state.post_db.insert(0, dbname)

    user = st.text_input('user:')
    if user:
        st.session_state.post_user.insert(0, user)

    password = st.text_input('password:')
    if password:
        st.session_state.post_password.insert(0, password)

    host = st.text_input('host:')
    if host:
        st.session_state.post_host.insert(0, host)

    port = st.text_input('port:')
    if port:
        st.session_state.post_port.insert(0, port)

    

    if "postgres_state" not in st.session_state:
        st.session_state.postgres_state = False
    if button or st.session_state.postgres_state:
        try:
            st.session_state.postgres_state = True
            connect = postgresDB.connect_db(dbname=st.session_state.post_db[0], user=st.session_state.post_user[0], password=st.session_state.post_password[0], host=st.session_state.post_password[0], port=st.session_state.post_port[0])
            db_info = postgresDB.db_info(connect)
            st.write("sucess!")
        except:
            st.write("Information invalid. Please enter the right information again.")
elif db == 'upload data':
    uploaded_file = st.file_uploader("Choose a CSV file")
    if uploaded_file is not None:
        df1=pd.read_csv(uploaded_file)
        st.write("### Your Dataset:", df1)
        df_to_db(df1, 'uploaded_file')
        connect = sqliteDB.connect_db('uploaded_file')
        db_info = sqliteDB.db_info(connect)
        if db_info == {}:
            st.write("Information invalid. Please enter the right information again.")
        else:
            st.write("sucess!")


## input API/QUERY/DESCRIPTON
api = '' ## Enter your open ai API
input = st.sidebar.text_area("input your query description")

if "input_state" not in st.session_state:
    st.session_state.input_state = False
    st.session_state.input_content = []

if input or st.session_state.input_state:
    st.session_state.input_state = True
    st.session_state.input_content.insert(0,input)
    try:

        openai.api_key = api
        for i in st.session_state.input_content:
            if i == '':
                pass
            else:
                prompt = render_prompt(db_info, i)

        query = get_completion(messages=prompt)
        result_tb = pd.read_sql_query(query, connect)
        st.session_state['result_tb'] = result_tb
        with ct2:
            st.write("### Your Query Result:",result_tb)
        if "query_table" not in st.session_state:
            st.session_state.query_table = []
        st.session_state.query_table.insert(0, result_tb)
        
    except:
        st.sidebar.write("Your description is blur or irrelevant. Or you are not connected to a databse.")


if "input2_state" not in st.session_state:
    st.session_state.input2_state = False
    st.session_state.input2_content = []
if "plots" not in st.session_state:
    st.session_state.plots = {}

input2 = st.sidebar.text_area("What plot you want to see?")
if input2 or st.session_state.input2_state:
    st.session_state.input2_state = True
    st.session_state.input2_content.insert(0,input2)
    result_tb = st.session_state['result_tb']
    #show fig
    for i in st.session_state.input2_content:
        if i == '':
            pass
        else:
            prompt2 = plot_prompt(result_tb, i)
            break

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


    #show fig info
    prompt3 = plot_info(result_tb, input2)
    columns = ast.literal_eval(get_completion(prompt3))
    plot_data = result_tb[columns]
    
    prompt4 = describ_plot(plot_data, input2)
    description = get_completion(messages=prompt4)
    ct1.write("## Your Analysis Plot:")
    ct1.plotly_chart(fig)
    ct1.write(description)
    save = ct1.button('Save this plot')


    if save:
        st.session_state.plots[description] = fig
        ct1.write('Success!')
