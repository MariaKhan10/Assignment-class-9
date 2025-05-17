import streamlit as st
import google.generativeai as genai
import os


genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class AIWritingAssistant:
    def __init__(self):
        st.title("📝 AI Writing Assistant")
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def show(self):
        st.subheader("🤖 AI-Powered Writing Assistant")

        option = st.radio(
            "Choose Task",
            ["Summarize Text", "Generate Email Draft", "Suggest Resume Bullets"]
        )

        if option == "Summarize Text":
            self.summarize_text()
        elif option == "Generate Email Draft":
            self.generate_email()
        elif option == "Suggest Resume Bullets":
            self.suggest_resume_bullets()

    def summarize_text(self):
        text = st.text_area("Paste your text here", height=200)
        if st.button("Summarize"):
            if not text.strip():
                st.warning("Please enter some text to summarize.")
                return
            prompt = f"Summarize the following text:\n\n{text}"
            response = self.model.generate_content(prompt)
            st.success("Summary:")
            st.write(response.text)

    def generate_email(self):
        recipient = st.text_input("Recipient Name")
        purpose = st.text_area("Purpose of the Email", height=100)
        if st.button("Generate Email Draft"):
            if not purpose.strip():
                st.warning("Please enter the purpose of the email.")
                return
            prompt = f"Write a professional email to {recipient} about {purpose}"
            response = self.model.generate_content(prompt)
            st.success("Email Draft:")
            st.write(response.text)

    def suggest_resume_bullets(self):
        job_role = st.text_input("Job Role")
        achievements = st.text_area("Your Achievements / Responsibilities", height=150)
        if st.button("Suggest Bullets"):
            if not job_role.strip() or not achievements.strip():
                st.warning("Please fill both Job Role and Achievements.")
                return
            prompt = f"Suggest resume bullet points for a {job_role} with these achievements:\n{achievements}"
            response = self.model.generate_content(prompt)
            st.success("Suggested Resume Bullets:")
            st.write(response.text)

def run():
    app = AIWritingAssistant()
    app.show()
