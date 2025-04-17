import datetime

import streamlit as st
import plotly.graph_objects as go

from agent import invoke_llm
import pandas as pd

st.title("Insights POC v2")


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.thread_id = datetime.datetime.now().isoformat()
    print('setting new threadid', st.session_state.thread_id)
    st.session_state.messages = []
    st.session_state.update({"explanation2plot": {}})

# read default csv
# df = pd.read_csv("data/Demo.csv")

# allow uploading files
# uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

# if uploaded_file is not None:
    # df = pd.read_csv(uploaded_file)
    # st.write("Here’s a preview of your data:")
    # st.dataframe(df)
    #
    # # Example of working with the data:
    # st.write("Basic Statistics:")
    # st.write(df.describe())

    # cleaning history
    # st.session_state.messages = []
    # st.session_state.update({"explanation2plot": {}})

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        obj = st.session_state.get("explanation2plot").get(message["content"])
        if obj is not None:
            if isinstance(obj, pd.DataFrame):
                st.dataframe(obj)
            elif isinstance(obj, go.Figure):
                st.plotly_chart(st.session_state.get("explanation2plot")[message["content"]])

# React to user input
if prompt := st.chat_input("How salary raise affects performance?"):

    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        llm_response, python_tool_result = invoke_llm(prompt, st.session_state.thread_id)
        last_msg = llm_response["messages"][-1].content
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(last_msg)
            #

            if python_tool_result:
                if python_tool_result.type == "plot":
                    st.plotly_chart(python_tool_result.result)
                    st.session_state.get("explanation2plot")[last_msg] = python_tool_result.result
                elif python_tool_result.type == "table":
                    st.dataframe(python_tool_result.result)
                    st.session_state.get("explanation2plot")[last_msg] = python_tool_result.result

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": last_msg})

    except Exception as e:
        st.chat_message("assistant").markdown(f"Oops, something went wrong: {str(e)}")
        st.chat_message("assistant").markdown("We will fix this, but for now try reformulating your question.")