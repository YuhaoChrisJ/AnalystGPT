import streamlit as st
from LLM_agents import describ_df, get_completion

st.markdown("<h1 style='text-align: center; color: black;'>This is your REPORT</h1>", unsafe_allow_html=True)
try:
    for df in st.session_state['query_table']:
        @st.cache_data
        def intro(df):
            return get_completion(describ_df(df))
        
        introduction = intro(df)
        st.write(introduction)
        break


    for description, plot in st.session_state['plots'].items():
        st.plotly_chart(plot)
        st.write(description)
except:
    pass