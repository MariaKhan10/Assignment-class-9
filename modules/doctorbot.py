import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv
from deep_translator import GoogleTranslator
import google.generativeai as genai
from fpdf import FPDF
import base64

# -------------------- Helper Functions --------------------
def get_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def get_risk_score(text):
    if "High" in text:
        return "High", "🔴"
    elif "Moderate" in text:
        return "Moderate", "🟠"
    return "Low", "🟢"

# -------------------- Load API Key --------------------
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# -------------------- OOP Classes --------------------
class Translator:
    def __init__(self, target_lang):
        self.target_lang = target_lang
        self.lang_map = {"Urdu": "ur", "Hindi": "hi"}

    def translate(self, text):
        if self.target_lang == "English":
            return text
        try:
            return GoogleTranslator(source='auto', target=self.lang_map.get(self.target_lang, "en")).translate(text)
        except Exception:
            st.error("❌ Translation failed.")
            return text

class MedicalAnalyzer:
    def get_diagnosis(self, symptoms):
        raise NotImplementedError()

class GeminiAnalyzer(MedicalAnalyzer):
    def get_diagnosis(self, symptoms):
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        prompt = f"""
        A user has reported the following symptoms: {symptoms}.
        1. What could be the possible diagnosis?
        2. Suggest common over-the-counter medicines.
        3. Suggest quick home remedies.
        4. Suggest preventive care tips.
        5. What emergency level does this case seem to be? (Low, Moderate, High)
        6. What follow-up questions would help clarify the diagnosis?
        Provide answers in bullet points. Keep it simple and helpful.
        """
        response = model.generate_content(prompt)
        return response.text

class InputHandler:
    def get_input(self):
        raise NotImplementedError()

class TextInputHandler(InputHandler):
    def get_input(self):
        st.sidebar.markdown("------")
        return st.text_area("🤒 Enter your symptoms:", value=st.session_state.get("symptoms", ""))

class PDFExporter:
    def export(self, text):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for line in text.split('\n'):
            pdf.multi_cell(0, 10, line)
        filename = f"Medical_Report_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        pdf.output(filename)
        return filename

# -------------------- Main Function --------------------
def run():
    img_base64 = get_image_base64("assets/image1.png")

    st.markdown("""<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #FF5722;
        text-align: center;
        margin-bottom: 1rem;
        animation: glow 1.5s infinite alternate;
    }
    .subtitle {
        font-size: 1.1rem;
        text-align: center;
        color: #FF5722;
        margin-bottom: 2rem;
    }
    .description {
        font-size: 1rem;
        color: #FFC107;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    @keyframes glow {
        from { box-shadow: 0 0 10px #7e57c2; }
        to { box-shadow: 0 0 20px #9575cd; }
    }
    .emoji-title {
        font-size: 2rem;
        text-align: center;
        margin-top: 1rem;
        color: #FF5722;
    }
    </style>""", unsafe_allow_html=True)

    st.markdown('<div class="main-title">MediConsult Pro 🩺</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">AI-Powered Instant Medical Help  💜</div>', unsafe_allow_html=True)
    st.markdown('<div class="description">Your personal health assistant, guiding you through symptoms, providing remedies, and answering your health-related queries in real-time! 🩺💡</div>', unsafe_allow_html=True)
    st.markdown('<div class="emoji-title">Get Help Anytime, Anywhere!\n 💬</div>', unsafe_allow_html=True)
    st.sidebar.markdown("---")

    # ---------------- Sidebar ----------------
    st.sidebar.image("assets/image4.gif", use_container_width=True)
    lang = st.sidebar.radio("🌐 Choose language", ["English", "Urdu", "Hindi"])

    st.sidebar.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #d1c4e9, #7e57c2);
            padding: 16px;
            border-radius: 14px;
            box-shadow: 0 0 15px rgba(126, 87, 194, 0.6);
            text-align: center;
            color: white;
            animation: glow 2s ease-in-out infinite alternate;
        '>
            <img src='data:image/png;base64,{img_base64}' 
                 style='width: 75px; height: 75px; border-radius: 50%; margin-bottom: 10px; border: 2px solid white;'>
            <h4 style='margin: 0;'>SehatBot</h4>
            <p style='font-size: 0.9rem;'>Health Advisor</p>
            <hr style='margin: 10px 0; border-color: rgba(255,255,255,0.4);'>
            <p style='font-size: 0.85rem;'>Empowering care with AI 💜</p>
        </div>
    """, unsafe_allow_html=True)

    # ---------------- Session Init ----------------
    st.session_state.setdefault("symptoms", "")
    st.session_state.setdefault("final_result", "")
    st.session_state.setdefault("followup_query", "")
    st.session_state.setdefault("followup_response", "")

    translator = Translator(lang)
    analyzer = GeminiAnalyzer()
    pdf_exporter = PDFExporter()
    input_handler = TextInputHandler()

    # ---------------- Symptom Input ----------------
    symptoms = input_handler.get_input()

    if st.button("🩺 Get Advice"):
        if symptoms.strip():
            st.session_state["symptoms"] = symptoms
            with st.spinner("🩺 Scanning symptoms and preparing advice..."):
                translated = translator.translate(symptoms)
                result = analyzer.get_diagnosis(translated)
                final_result = translator.translate(result)
                st.session_state["final_result"] = final_result
                st.session_state["followup_query"] = ""
                st.session_state["followup_response"] = ""
                st.markdown("### ✅ Medical Advice:")
                st.write(final_result)
                st.markdown("---")
            risk_level, emoji = get_risk_score(final_result)
            st.markdown(f"### 🚨 Health Risk Level: {emoji} **{risk_level}**")
            st.progress({"Low": 0.3, "Moderate": 0.6, "High": 1.0}[risk_level])
        else:
            st.warning("⚠️ Please enter your symptoms first.")

    # ---------------- Follow-Up Assistant ----------------
    if st.session_state.get("final_result"):
        followup_response = st.session_state.get("followup_response")
        expanded_state = bool(followup_response)

        if followup_response:
            st.markdown("🔔 **Answered your follow-up! Scroll down and click to view the response.**")

        with st.expander("💬 Still have questions? Ask AI Assistant", expanded=expanded_state):
            followup = st.text_input("Ask a follow-up question:", value=st.session_state.get("followup_query", ""))
            if st.button("Submit Follow-Up"):
                if followup.strip():
                    st.session_state["followup_query"] = followup
                    with st.spinner("Thinking..."):
                        response = genai.GenerativeModel("models/gemini-1.5-flash").generate_content(
                            f"User asked: '{followup}'\nBased on earlier diagnosis: '{st.session_state['final_result']}'\nRespond clearly and helpfully."
                        )
                        st.session_state["followup_response"] = response.text
                    st.rerun()
            if st.session_state.get("followup_response"):
                st.markdown("### 🤖 Response to Your Question:")
                st.write(st.session_state["followup_response"])

    # ---------------- PDF Export ----------------
    if st.session_state.get("final_result"):
        if st.button("📄 Want to Download Medical Report (PDF) ?"):
            filename = pdf_exporter.export(st.session_state["final_result"])
            with open(filename, "rb") as file:
                st.download_button(
                    label="📥 Click to View PDF",
                    data=file,
                    file_name=filename,
                    mime="application/pdf"
                )
