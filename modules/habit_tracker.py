import streamlit as st
import sqlite3
from datetime import date
import pandas as pd

class HabitDatabase:
    def __init__(self, db_path="data/habits.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            name TEXT,
            frequency TEXT,
            start_date TEXT,
            status TEXT
        )
        """
        self.conn.execute(query)
        self.conn.commit()

    def add_habit(self, user_id, name, frequency, start_date):
        self.conn.execute(
            "INSERT INTO habits (user_id, name, frequency, start_date, status) VALUES (?, ?, ?, ?, ?)",
            (user_id, name, frequency, start_date, "Active"),
        )
        self.conn.commit()

    def get_habits(self, user_id):
        df = pd.read_sql_query("SELECT * FROM habits WHERE user_id = ?", self.conn, params=(user_id,))
        return df

    def mark_complete(self, habit_id):
        self.conn.execute("UPDATE habits SET status = 'Completed' WHERE id = ?", (habit_id,))
        self.conn.commit()

    def delete_habit(self, habit_id):
        self.conn.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()


class HabitTrackerApp:
    def __init__(self):
        self.db = HabitDatabase()

    def show(self):
        st.subheader("🧘 Habit Tracker")

        user_id = st.session_state.get('username')
        if not user_id:
            st.warning("⚠️ You must be logged in to track your habits.")
            return

        self.display_add_form(user_id)
        self.display_habits(user_id)

    def display_add_form(self, user_id):
        with st.form("Add Habit"):
            name = st.text_input("Habit Name")
            frequency = st.radio("Frequency", ["Daily", "Weekly", "Monthly"])
            start_date = st.date_input("Start Date", date.today())
            submitted = st.form_submit_button("Add Habit")

            if submitted and name:
                self.db.add_habit(user_id, name, frequency, str(start_date))
                st.success("✅ Habit added!")
                st.rerun()  # rerun to update list

    def display_habits(self, user_id):
        st.markdown("---")
        df = self.db.get_habits(user_id)

        if not df.empty:
            st.subheader("📋 Your Habits")
            for _, row in df.iterrows():
                col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
                col1.write(f"**{row['name']}**")
                col2.write(f"{row['frequency']}")
                col3.write(f"{row['start_date']}")
                col4.write(f"Status: `{row['status']}`")

                if row["status"] != "Completed":
                    if col5.button("✅", key=f"complete_{row['id']}"):
                        self.db.mark_complete(row["id"])
                        st.rerun()
                else:
                    if col5.button("❌", key=f"delete_{row['id']}"):
                        self.db.delete_habit(row["id"])
                        st.rerun()
        else:
            st.info("No habits tracked yet.")


def run():
    app = HabitTrackerApp()
    app.show()
