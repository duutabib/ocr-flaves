import streamlit as st
import requests
import json



url = "https://localhost:8000/generate"

st.title("Invoice History")

if "chat history" not in st.session_state:
    st.session_state.chat_history = []

for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

if user_input := st.chat_input("Your question here"):
    with st.chat_message("user"):
        st.markdown(user_input)
    
    st.session_state.chat_history.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        prompt = "You are an assistant who helps the user. "
        "Answer their questions as accurately as possible. Be concise."
        history = [
            f'{ch["role"]}: {ch["content"]}'
            for ch in st.session_state.chat_history
        ]
        prompt += "".join(history)
        prompt += " assistant: "
        data = json.dumps({"prompt": prompt})

        with requests.post(url, data=data, stream=True) as r:
            for line in r.iter_lines(decode_unicode=True):
                full_response += line.decode("utf-8")
                placeholder.markdown(full_response + "█ ")
        placeholder.markdown(full_response)

        st.session_state.chat_history.append(
            {"role": "assistant", "content": full_response}
        )
                