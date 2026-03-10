import streamlit as st
import requests
import json

st.set_page_config(page_title="DocuMind AI", page_icon="📄")
st.title("📄 DocuMind: Chat with your PDF")

API_URL = "http://127.0.0.1:8000/query"

user_question = st.text_input("Enter your question here:")

if st.button("Ask AI"):
    if user_question:
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            sources = []
            
            try:
                with requests.post(API_URL, json={"question": user_question}, stream=True) as r:
                    if r.status_code == 429:
                        st.error("Rate limit exceeded. Please wait a minute before asking again.")
                    elif r.status_code == 200:
                        for line in r.iter_lines():
                            if line:
                                data = json.loads(line.decode('utf-8'))
                                
                                if data["type"] == "content":
                                    full_response += data["content"]
                                    response_placeholder.markdown(full_response + "▌")
                                
                                elif data["type"] == "metadata":
                                    sources = data["sources"]
                                    
                        response_placeholder.markdown(full_response)
                        
                        if sources:
                            st.info("Sources checked:\n" + "\n".join([f"- {s}" for s in sources]))
                    else:
                        st.error(f"Server Error: {r.status_code}")
            except Exception as e:
                st.error(f"Could not connect to backend. Error: {e}")