import streamlit as st
import pandas as pd
import openai
import ast
import matplotlib.backends.backend_pdf as pdf

from sql_loader.loaders import mysqlDB, postgresDB, sqliteDB, render_prompt
from LLM_agents import get_completion, plot_prompt, plot_info, describ_plot

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
        if db_info == {}:
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


if "input2_state" not in st.session_state:
    st.session_state.input2_state = False
if "plots" not in st.session_state:
    st.session_state.plots = {}

input2 = st.sidebar.text_area("What plot you want to see?")
if input2 or st.session_state.input2_state:
    st.session_state.input2_state = True
    #show fig
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

    del st.session_state['input_state']

    #show fig info
    prompt3 = plot_info(result_tb, input2)
    columns = ast.literal_eval(get_completion(prompt3))
    plot_data = result_tb[columns]
    
    prompt4 = describ_plot(plot_data, input2)
    description = get_completion(messages=prompt4)
    ct1.write("## Your Analysis Plot:")
    save = ct1.button('Save this plot')
    ct1.plotly_chart(fig)
    ct1.write(description)

    if "save_state" not in st.session_state:
        st.session_state.save_state = False

    if save or st.session_state.save_state:
        st.session_state.save_state = True
        st.session_state.plots[description] = fig

    #save as pdf
    pdf_file = pdf.PdfPages('output.pdf')
    for description, plot in st.session_state.plots.items():
        st.plotly_chart(plot)
        st.write(description)



