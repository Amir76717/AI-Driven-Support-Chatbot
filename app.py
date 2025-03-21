import streamlit as st
import requests
import json

st.title("Customer Support Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("How can I help you today?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Send message to Rasa server
    rasa_url = "http://localhost:5005/webhooks/rest/webhook"
    response = requests.post(
        rasa_url,
        json={"sender": "user", "message": prompt}
    )
    
    # Get response from Rasa
    bot_response = ""
    if response.status_code == 200:
        response_data = response.json()
        if response_data:
            bot_response = response_data[0].get("text", "Sorry, I didn't understand that.")
        else:
            bot_response = "I didn't get a response. Please try again."
    else:
        bot_response = f"Error: {response.status_code}"
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(bot_response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": bot_response})