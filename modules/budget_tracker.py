import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import date
import os

def init_db():
    if not os.path.exists("data"):
        os.makedirs("data")
    conn = sqlite3.connect("data/budget.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS budget
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         username TEXT,
         type TEXT,
         amount REAL,
         category TEXT,
         entry_date TEXT)
    ''')
    conn.commit()
    conn.close()

def add_entry(username, entry_type, amount, category, entry_date):
    conn = sqlite3.connect("data/budget.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO budget (username, type, amount, category, entry_date) VALUES (?, ?, ?, ?, ?)",
        (username, entry_type, amount, category, entry_date)
    )
    conn.commit()
    conn.close()

def get_entries(username):
    conn = sqlite3.connect("data/budget.db")
    df = pd.read_sql_query(
        "SELECT * FROM budget WHERE username = ?", conn, params=(username,)
    )
    conn.close()
    return df

def delete_entry(entry_id):
    conn = sqlite3.connect("data/budget.db")
    c = conn.cursor()
    c.execute("DELETE FROM budget WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()

def run():
    st.subheader("📊 Budget Tracker")
    init_db()

    username = st.session_state.get('username')

    if not username:
        st.warning("⚠️ You must be logged in to track your budget.")
        return

    st.markdown("""
    Welcome to your **Budget Tracker!**  
    - Add **Income** entries when you receive money (salary, gifts, etc.)  
    - Add **Expense** entries when you spend money (groceries, rent, bills, etc.)  
    Track your total income, expenses, and current balance.  
    Your data is private and saved just for you.
    """)

    with st.form("Add Budget Entry"):
        col1, col2, col3 = st.columns(3)

        with col1:
            entry_type = st.radio("Type", ["Income", "Expense"])

        with col2:
            amount = st.number_input("Amount", min_value=0.0, format="%.2f")

        with col3:
            if entry_type == "Income":
                categories = [
                    "Salary", "Freelance", "Business", "Gifts",
                    "Investments", "Bonus", "Other"
                ]
            else:
                categories = [
                    "Food", "Rent", "Utilities", "Transportation",
                    "Entertainment", "Shopping", "Healthcare",
                    "Education", "Travel", "Other"
                ]

            category = st.radio("Category", categories)

        entry_date = st.date_input("Date", value=date.today())

        submitted = st.form_submit_button("Add Entry")

        if submitted:
            if amount > 0:
                add_entry(username, entry_type, amount, category, str(entry_date))
                st.success("✅ Entry added!")
            else:
                st.error("Please enter a valid amount.")

    st.markdown("---")
    df = get_entries(username)

    if not df.empty:
        st.subheader("📅 Budget Summary")
        income = df[df["type"] == "Income"]["amount"].sum()
        expense = df[df["type"] == "Expense"]["amount"].sum()
        balance = income - expense

        st.write(f"**Total Income:** {income:.2f} Rupees")
        st.write(f"**Total Expense:** {expense:.2f} Rupees")
        st.write(f"**Balance:** {balance:.2f} Rupees")

        st.markdown("---")
        st.subheader("💸 Expenses by Category")

        expense_df = df[df["type"] == "Expense"]
        if not expense_df.empty:
            grouped = expense_df.groupby("category", as_index=False)["amount"].sum()
            fig = px.pie(grouped, values='amount', names='category', title='Expenses Distribution')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No expense data to show pie chart.")

        st.markdown("---")
        st.subheader("🤑 Income Entries")
        income_df = df[df["type"] == "Income"]
        if not income_df.empty:
            for _, row in income_df.iterrows():
                st.write(f"{row['entry_date']} — {row['category']} — Rupees{row['amount']:.2f}")
        else:
            st.info("No income entries yet.")

        st.markdown("---")
        st.subheader("💸 Expense Entries")
        if not expense_df.empty:
            for _, row in expense_df.iterrows():
                st.write(f"{row['entry_date']} — {row['category']} — Rupees{row['amount']:.2f}")
        else:
            st.info("No expense entries yet.")

        st.markdown("---")
        st.subheader("🧾 All Entries")
        for _, row in df.iterrows():
            col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
            col1.write(f"**{row['type']}**")
            col2.write(f"Rupees{row['amount']:.2f}")
            col3.write(f"{row['category']}")
            col4.write(f"{row['entry_date']}")
            if col5.button("❌", key=row["id"]):
                delete_entry(row["id"])
                st.rerun()
    else:
        st.info("No entries yet.")
