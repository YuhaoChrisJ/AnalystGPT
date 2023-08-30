
import pandas as pd
import sqlite3
import jinja2
import psycopg2
import mysql.connector
import streamlit as st



@st.cache_data
class sqliteDB:
    def __init__(self) -> None:
        pass
    def connect_db(db_address):
        ## Conncet to sql db
        conn = sqlite3.connect(db_address)

        return conn

    def db_info(conn):
        ## Extract table name/schema
        # Extract table name
        tb = pd.read_sql_query("select name as table_name from sqlite_master where type='table'", conn)
        tb_list = list(tb.iloc[:,0])

        # Extract table schema
        def get_schema(table_name):
            schema = pd.read_sql_query(f"PRAGMA table_info({table_name})", conn)
            schema_str = ''
            for index, row in schema.iterrows():
                column_info = f"name={row['name']}, datatype={row['type']};\n"
                schema_str = schema_str + column_info
            return schema, schema_str

        # Table name/schema pair
        name_schema = {}
        st.write('## Tables in your database')
        for name in tb_list:
            schema, schema_str = get_schema(name)
            st.write(name)
            st.write(schema)
            name_schema[name] = schema_str

        return name_schema
@st.cache_data
class postgresDB:
    def __init__(self) -> None:
        pass
    def connect_db(dbname, user, password, host, port):
        conn = psycopg2.connect(
            dbname = dbname,
            user = user,
            password = password,
            host = host,
            port = port,
        )
        return conn
    def db_info(conn):
        # Extract table name
        query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
        """
        tb = pd.read_sql_query(query, conn)
        tb_list = list(tb.iloc[:,0])
        # Extract table schema

        def get_schema(table_name):
            """Get schema for the given table in Postgres"""
            query = f"""
                SELECT column_name, data_type 
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
            """
            schema = pd.read_sql_query(query, conn)
            schema_str = ''
            for index, row in schema.iterrows():
                column_info = f"name={row['column_name']}, datatype={row['data_type']};\n"
                schema_str = schema_str + column_info
            return schema, schema_str

        name_schema = {}
        st.write('## Tables in database')
        for name in tb_list:
            schema, schema_str = get_schema(name)
            st.write(name)
            st.write(schema)
            name_schema[name] = get_schema(schema_str)
@st.cache_data
class mysqlDB:
    def __init__(self) -> None:
        pass
    def connect_db(host, user, password, database):
        return mysql.connector.connect(
            host = host,
            user = user,
            password = password,
            database = database
        )
    def db_info(conn):
        # Extract table name
        tb = pd.read_sql_query('SHOW TABLES', conn)
        tb_list = list(tb.iloc[:,0])

        def get_schema(table_name):
            """Get schema for the given table in Postgres"""
            query = f"""
                SELECT column_name, data_type 
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
            """
            schema = pd.read_sql_query(query, conn)
            schema_str = ''
            for index, row in schema.iterrows():
                column_info = f"name={row['COLUMN_NAME']}, datatype={row['DATA_TYPE']};\n"
                schema_str = schema_str + column_info
            return schema, schema_str

        name_schema = {}
        st.sidebar.write('## Tables in database')
        for name in tb_list:
            schema, schema_str = get_schema(name)
            st.sidebar.write(name)
            st.sidebar.write(schema)
            name_schema[name] = get_schema(schema_str)

        return name_schema


@st.cache_data
def render_prompt(name_schema, question):
        ## Render Prompt
        environment = jinja2.Environment()
        query_system_prompt = "You are a helpful assistant that only writes SQL SELECT queries. Reply only with SQL queries."
        query_template = environment.from_string(
        """
        Given tables name:
        {%- for name in name_schema.keys() %}
        {{ name }}
        With schema:
        {{ name_schema[name] }}
        {%- endfor %}
        Write a SQL query to answer the following question:
        {{ question }}""")

        query_prompt = query_template.render(
            name_schema = name_schema,
            question = question,
        )

        messages = [{"role": "system", "content": query_system_prompt}, {"role": "user", "content": query_prompt}]
        return messages
    


