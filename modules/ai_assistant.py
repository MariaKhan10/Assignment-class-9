import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv


class GeminiAssistant:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("models/gemini-1.5-flash")
        self.chat = self.model.start_chat(history=[])

    def chat_with_ai(self, user_input):
        try:
            response = self.chat.send_message(user_input)
            return response.text
        except Exception as e:
            return f"❌ Error: {e}"


class GeminiAssistantApp:
    def __init__(self, api_key):
        self.assistant = GeminiAssistant(api_key)
    def show(self):
        st.title("🧠 Welcome to Your AI Buddy!")
        st.subheader("🤖 Your AI Assistant — Here to help you anytime")

        st.write("Feel free to ask me anything or get some helpful tips.")
        user_input = st.text_input("What's on your mind today?", key="gemini_input")


        if user_input:
            with st.spinner("Thinking..."):
                response = self.assistant.chat_with_ai(user_input)

            st.markdown(f"**🧑 You:** {user_input}")
            st.markdown(f"**🤖 Gemini:** {response}")


def run():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        st.error("❌ Gemini API key not found. Please set GEMINI_API_KEY in your .env file.")
        return

    app = GeminiAssistantApp(api_key)
    app.show()
