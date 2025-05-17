import streamlit as st
import sqlite3

DB_PATH = "data/tasks.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT,
                  title TEXT,
                  description TEXT,
                  deadline TEXT,
                  priority TEXT)''')
    conn.commit()
    conn.close()

def add_task(username, title, description, deadline, priority):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO tasks (username, title, description, deadline, priority)
        VALUES (?, ?, ?, ?, ?)
    ''', (username, title, description, deadline, priority))
    conn.commit()
    conn.close()

def get_tasks(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, title, description, deadline, priority FROM tasks WHERE username=?', (username,))
    data = c.fetchall()
    conn.close()
    return data

def delete_task(task_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

def run():
    st.subheader("🗓️ Task Manager")
    init_db()

    # ✅ Correctly fetch logged-in user
    username = st.session_state.get("username")

    if not username:
        st.warning("⚠️ You must be logged in to manage your tasks.")
        return

    with st.form("Add Task"):
        title = st.text_input("Task Title")
        description = st.text_area("Description")
        deadline = st.date_input("Deadline")
        priority = st.radio("Priority", ["Low", "Medium", "High"])
        submitted = st.form_submit_button("Add Task")
        if submitted:
            add_task(username, title, description, deadline.strftime("%Y-%m-%d"), priority)
            st.success("✅ Task added!")

    st.markdown("---")
    st.subheader("📋 Your Tasks")
    tasks = get_tasks(username)
    for task in tasks:
        task_id, title, description, deadline, priority = task
        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
        col1.write(f"**{title}**")
        col2.write(f"📅 {deadline}")
        col3.write(f"⭐ {priority}")
        col4.write(f"📝 {description}")
        if col5.button("❌", key=f"del-{task_id}"):
            delete_task(task_id)
            st.rerun()
