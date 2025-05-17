import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

class NotesDatabase:
    def __init__(self, db_path="data/notes.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            title TEXT,
            content TEXT,
            timestamp TEXT
        )
        """
        self.conn.execute(query)
        self.conn.commit()

    def add_note(self, user_id, title, content):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.conn.execute(
            "INSERT INTO notes (user_id, title, content, timestamp) VALUES (?, ?, ?, ?)",
            (user_id, title, content, timestamp)
        )
        self.conn.commit()

    def get_notes(self, user_id):
        return pd.read_sql_query("SELECT * FROM notes WHERE user_id = ?", self.conn, params=(user_id,))

    def delete_note(self, note_id):
        self.conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()


class NotesApp:
    def __init__(self):
        self.db = NotesDatabase()

    def show(self):
        st.subheader("📝 Notes Manager")

        user_id = st.session_state.get("username")
        if not user_id:
            st.warning("⚠️ You must be logged in to use the Notes Manager.")
            return

        self.display_add_form(user_id)
        self.display_notes(user_id)

    def display_add_form(self, user_id):
        with st.form("Add Note"):
            title = st.text_input("Title")
            content = st.text_area("Note")
            submitted = st.form_submit_button("Add Note")

            if submitted and title and content:
                self.db.add_note(user_id, title, content)
                st.success("✅ Note added!")
                st.rerun()
            elif submitted:
                st.warning("⚠️ Please fill both Title and Note.")

    def display_notes(self, user_id):
        st.markdown("---")
        df = self.db.get_notes(user_id)

        if not df.empty:
            st.subheader("📚 Your Notes")
            for _, row in df.iterrows():
                col1, col2 = st.columns([9, 1])
                with col1:
                    st.markdown(f"**{row['title']}** — _{row['timestamp']}_")
                    st.write(row["content"])
                with col2:
                    if st.button("🗑️", key=f"delete_{row['id']}"):
                        self.db.delete_note(row["id"])
                        st.rerun()

            # Export as .txt
            all_text = "\n\n".join(
                [f"{row['title']} - {row['timestamp']}\n{row['content']}" for _, row in df.iterrows()]
            )
            st.download_button("📥 Download Notes (.txt)", all_text, file_name="my_notes.txt")
        else:
            st.info("You have not added any notes yet.")

def run():
    app = NotesApp()
    app.show()
