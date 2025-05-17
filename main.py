import streamlit as st
import streamlit_authenticator as stauth
import yaml
import bcrypt
import os
import time

from modules import ai_writing_assistant, task_manager, budget_tracker, habit_tracker, notes_manager, ai_assistant, doctorbot
import stripe

stripe_secret_key = st.secrets["STRIPE_SECRET_KEY"]
stripe_publishable_key = st.secrets["STRIPE_PUBLISHABLE_KEY"]

stripe.api_key = stripe_secret_key

def create_checkout_session():
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",  # Try usd to rule out currency issue
                    "unit_amount": 50000,
                    "product_data": {
                        "name": "Upgrade to Premium",
                    },
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url="https://smartkit.streamlit.app/?success=true",
            cancel_url="https://smartkit.streamlit.app/?canceled=true",
        )
        return session.url
    except Exception as e:
        st.error(f"Stripe Error: {e}")  # Show in Streamlit
        return None


USERS_FILE = "users.yaml"

def load_users(file_path=USERS_FILE):
    if not os.path.exists(file_path):
        return {"credentials": {"usernames": {}}}
    with open(file_path, "r") as f:
        users = yaml.safe_load(f)

  
    for username, info in users["credentials"]["usernames"].items():
        if "name" not in info:
            info["name"] = username  

    return users


def save_users(users, file_path=USERS_FILE):
    with open(file_path, "w") as f:
        yaml.dump(users, f, default_flow_style=False)

def register_user(username, name, password, file_path=USERS_FILE):
    users = load_users(file_path)
    if username in users["credentials"]["usernames"]:
        return False, "Username already exists"
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    users["credentials"]["usernames"][username] = {
        "name": name,
        "password": hashed_pw
    }
    save_users(users, file_path)
    return True, "User registered successfully"

st.set_page_config(page_title="SmartKit", layout="centered",page_icon="🧰")

st.markdown("""
    <style>
        /* Default (Light mode) background and text */
        .stApp {
            background: linear-gradient(135deg, #c3cfe2 0%, #e6e9f0 100%);
            padding: 30px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #222222;
        }

        /* Text colors for light mode */
        h1, h2, h3, p, li, label {
            color: #222222 !important;
        }

        /* Buttons for light mode */
        .stButton > button, .stDownloadButton > button {
            background-color: #6a5acd !important;
            color: white !important;
            border-radius: 8px !important;
            padding: 10px 22px !important;
            font-weight: 600 !important;
            border: none !important;
            cursor: pointer !important;
            transition: background-color 0.3s ease;
        }
        .stButton > button:hover, .stDownloadButton > button:hover {
            background-color: #5848c2 !important;
        }

        /* Inputs & textareas for light mode */
        input, textarea {
            border: 1px solid #aaa !important;
            border-radius: 8px !important;
            padding: 10px !important;
            color: #222 !important;
            background-color: white !important;
        }

        /* Dark mode overrides */
        @media (prefers-color-scheme: dark) {
            .stApp {
                background: linear-gradient(135deg, #121212 0%, #1e1e1e 100%);
                color: #e0e0e0 !important;
            }
            h1, h2, h3, p, li, label {
                color: #e0e0e0 !important;
            }
            .stButton > button, .stDownloadButton > button {
                background-color: #8a79ff !important;
                color: #121212 !important;
            }
            .stButton > button:hover, .stDownloadButton > button:hover {
                background-color: #6c5ce7 !important;
                color: white !important;
            }
            input, textarea {
                background-color: #222 !important;
                color: #ddd !important;
                border: 1px solid #555 !important;
            }
        }
    </style>
""", unsafe_allow_html=True)


st.markdown("""
<h1 style="text-align:center; font-size:48px; color:#4B0082;">
    <strong>Smart<span style='color:#FF69B4;'>Kit</span> 🧰</strong>
</h1>
""", unsafe_allow_html=True)

st.markdown("<h4 style='text-align:center; color:gray;'>Your All-in-One Productivity Toolkit</h4>", unsafe_allow_html=True)



st.markdown("""
<div style='
    background: linear-gradient(to right, #6a11cb, #2575fc);
    padding: 30px;
    border-radius: 15px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    text-align: center;
    color: white;
'>
    <h2 style='font-size: 32px; margin-bottom: 10px;'>Unlock <span style="color: #FFD700;">SmartKit Premium</span></h2>
    <p style='font-size: 18px; margin-bottom: 20px;'>
        Experience the best of SmartKit — access premium AI tools like 
        <strong>ProWriter AI</strong>, <strong>MediConsult Pro</strong>, and 
        <strong>SmartHelper AI</strong> with advanced features.
    </p>
</div>
""", unsafe_allow_html=True)



st.markdown("<br>", unsafe_allow_html=True)  

query_params = st.query_params

if "success" in query_params:
    st.success("🎉 Thank you for subscribing to Premium!")
    time.sleep(2)  
    st.query_params.clear()

elif "canceled" in query_params:
    st.warning("❌ Payment canceled.")
    time.sleep(1)
    st.query_params.clear()


# ---------------------------
# Main app with login/register
# ---------------------------

def main():
    users_config = load_users()

    authenticator = stauth.Authenticate(
        users_config["credentials"],
        "app_cookie",
        "app_key",
        cookie_expiry_days=1
    )

    menu = st.sidebar.radio("Menu", ["Login", "Register"])

    if menu == "Login":
        login_info = authenticator.login("Login", "main")

        if login_info is None:
            st.warning("Please enter your login details.")
            return

        # Handle login values safely
        try:
            name, auth_status, username = login_info
        except ValueError:
            name, auth_status = login_info
            username = None  

        if auth_status is False:
            st.error("Invalid username or password.")
        elif auth_status is True:
            #  Store session state
            if username:
                st.session_state["username"] = username
            st.session_state["name"] = name

            authenticator.logout("Logout", "sidebar")
            st.sidebar.success(f"Welcome {name} 👋")

            app_choice = st.sidebar.radio("Choose a tool:", [
                "Task Manager",
                "Budget Tracker",
                "Habit Tracker",
                "Notes Manager",
                "ProWriter AI  ✨ (Free Trial)",
                "MediConsult pro  🩺 (Free Trial)",
                "Smart Helper  🌐 (Free Trial)",
            ])


            if app_choice == "Task Manager":
                task_manager.run()
            elif app_choice == "Budget Tracker":
                budget_tracker.run()
            elif app_choice == "Habit Tracker":
                habit_tracker.run()
            elif app_choice == "ProWriter AI  ✨ (Free Trial)":
                ai_writing_assistant.run()
            elif app_choice == "Notes Manager":
                notes_manager.run()
            elif app_choice == "Smart Helper  🌐 (Free Trial)":
                ai_assistant.run()
            elif app_choice == "MediConsult pro  🩺 (Free Trial)":
                doctorbot.run()   


            with st.sidebar:
                st.markdown("---") 
                st.markdown("### 🔒 Premium Access")
                if st.button("💳 Upgrade to Premium – PKR 500"):
                    checkout_url = create_checkout_session()
                    if checkout_url:
                        st.components.v1.html(
                            f"""
                            <script>
                                window.top.location.href = "{checkout_url}";
                            </script>
                            """,
                            height=0,
                        )
                    else:
                        st.error("Failed to create checkout session. Check your Stripe key.")
       

    elif menu == "Register":
      st.title("🔐 Register New User")
      reg_username = st.text_input("Username")
      reg_password = st.text_input("Password", type="password")

      if st.button("Register"):
        if reg_username and reg_password:
            success, msg = register_user(reg_username, reg_username, reg_password)
            if success:
                st.success(msg + " ✅ You can now login.")
            else:
                st.error(msg)
        else:
            st.warning("Please fill all fields.")

st.markdown("""
<br><hr>
<div style='text-align: center; color: gray; font-size: 14px;'>
    Made with ❤️ by Maria Khan 
</div>
""", unsafe_allow_html=True)



if __name__ == "__main__":
    main()
