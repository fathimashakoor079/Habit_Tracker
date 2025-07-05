import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import sqlite3

# Initialize database connection
def create_connection():
    conn = sqlite3.connect('habit_tracker.db')
    return conn

# User authentication functions
def register_user(username, password):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(username, password):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

# Load habits for a user
def load_user_habits(user_id):
    conn = create_connection()
    query = "SELECT * FROM habits WHERE user_id=?"
    habits = pd.read_sql(query, conn, params=(user_id,))
    conn.close()
    if "date" in habits.columns:
        habits["date"] = pd.to_datetime(habits["date"], errors="coerce")
    return habits

# Add a habit
def add_habit(user_id, habit_name, notes):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO habits (user_id, name, date, status, notes) VALUES (?, ?, ?, ?, ?)",
                   (user_id, habit_name, datetime.datetime.now(), 'Started', notes))
    conn.commit()
    conn.close()

# Log progress
def log_habit_progress(user_id, habit_name, status):
    conn = create_connection()
    cursor = conn.cursor()
    current_time = datetime.datetime.now()
    cursor.execute(
        "INSERT INTO habits (user_id, name, date, status) VALUES (?, ?, ?, ?)",
        (user_id, habit_name, current_time, status)
    )
    conn.commit()
    conn.close()

# Create tables if they do not exist
def create_tables():
    conn = create_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Habits table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            date DATETIME NOT NULL,
            status TEXT NOT NULL,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()

# Calculate streaks
def calculate_streaks(habit_data):
    streaks = {}
    for habit in habit_data["name"].unique():
        dates = habit_data[habit_data["name"] == habit]["date"].sort_values()
        max_streak, current_streak = 0, 0
        prev_date = None
        for date in dates:
            if prev_date and (date - prev_date).days == 1:
                current_streak += 1
            else:
                current_streak = 1
            max_streak = max(max_streak, current_streak)
            prev_date = date
        streaks[habit] = max_streak
    return streaks

create_tables()

# Set up Streamlit
st.set_page_config(page_title="Habit Tracker", layout="wide")
st.title("📊 Enhanced Habit Tracker Application")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'habits_data' not in st.session_state:
    st.session_state.habits_data = pd.DataFrame(columns=["id", "user_id", "name", "date", "status", "notes"])

# User authentication
st.sidebar.subheader("User Authentication")
auth_option = st.sidebar.radio("Select an option:", ["Login", "Register"])

if auth_option == "Register":
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type='password')
    if st.sidebar.button("Register"):
        if register_user(username, password):
            st.success("Registered successfully!")
        else:
            st.error("Username already exists!")

elif auth_option == "Login":
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type='password')
    if st.sidebar.button("Login"):
        user = login_user(username, password)
        if user:
            st.session_state.user_id = user[0]
            st.session_state.logged_in = True
            st.session_state.habits_data = load_user_habits(st.session_state.user_id)
            st.success(f"Welcome back, {username}!")
        else:
            st.error("Invalid credentials.")

# Main functionality
if st.session_state.logged_in:
    menu = st.sidebar.radio("Menu", ["Add Habit", "Log Habit", "View Habits", "Visualize Habits", "Dashboard"])

    if menu == "Add Habit":
        st.subheader("📝 Add a New Habit")
        new_habit = st.text_input("Habit Name:")
        notes = st.text_area("Notes (optional):")
        if st.button("Add Habit"):
            if new_habit:
                add_habit(st.session_state.user_id, new_habit, notes)
                st.session_state.habits_data = load_user_habits(st.session_state.user_id)
                st.success("Habit added successfully.")
            else:
                st.error("Habit name cannot be empty.")

    elif menu == "Log Habit":
        st.subheader("📅 Log Habit Progress")
        if not st.session_state.habits_data.empty:
            habit_names = st.session_state.habits_data["name"].unique()
            selected_habit = st.selectbox("Select a Habit:", habit_names)
            log_status = st.radio("Status:", ["completed","inprogress", "skipped"], horizontal=True)
            if st.button("Log Progress"):
                log_habit_progress(st.session_state.user_id, selected_habit, log_status)
                st.session_state.habits_data = load_user_habits(st.session_state.user_id)
                st.success(f"Progress for '{selected_habit}' logged as '{log_status}'.")
        else:
            st.warning("No habits added yet.")

    elif menu == "View Habits":
        st.subheader("📋 View Habit Logs")
        if not st.session_state.habits_data.empty:
            columns_to_display = [col for col in st.session_state.habits_data.columns if col not in ['id', 'user_id']]
            st.dataframe(st.session_state.habits_data.sort_values("date", ascending=False)[columns_to_display])
        else:
            st.info("No logs available.")

    elif menu == "Visualize Habits":
        st.subheader("📊 Visualize Your Habit Progress")

        if st.session_state.habits_data.empty:
            st.info("No habit data available for visualization.")
        else:
            habit_names = st.session_state.habits_data["name"].unique()
            selected_habit = st.selectbox("Select a habit to visualize:", habit_names)

            start_date = st.date_input("Start Date", value=st.session_state.habits_data["date"].min().date())
            end_date = st.date_input("End Date", value=st.session_state.habits_data["date"].max().date())

            filtered_data = st.session_state.habits_data[
                (st.session_state.habits_data["name"] == selected_habit) &
                (st.session_state.habits_data["date"].dt.date >= start_date) &
                (st.session_state.habits_data["date"].dt.date <= end_date)
            ]

            if filtered_data.empty:
                st.warning("No data available for the selected habit and date range.")
            else:
                               # Pie Chart
                

                # Assuming filtered_data is your DataFrame, and selected_habit is defined earlier.
                st.write(f"### Pie Chart for {selected_habit}")

                # Creating a plot
                fig, ax = plt.subplots()
                # Value counts on status column, followed by plotting it as a pie chart
                status_counts = filtered_data["status"].value_counts()
                # Plotting pie chart without showing extra counts on the left
                status_counts.plot.pie(autopct="%1.1f%%", startangle=90, ax=ax, colors=["green", "red", "orange"])

                # Hiding the axis
                ax.set_ylabel('')

                # Display the pie chart in Streamlit
                st.pyplot(fig)

                # Heatmap
                st.write(f"### Heatmap for {selected_habit}")
                heatmap_data = filtered_data.pivot_table(index="date", columns="status", aggfunc="size", fill_value=0)
                heatmap_data.index = heatmap_data.index.date
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.set_yticklabels([str(date) for date in heatmap_data.index], rotation=0)
                sns.heatmap(heatmap_data, annot=True, fmt="d", cmap="coolwarm", ax=ax)
                st.pyplot(fig)

                # Success Rate
                total_logs = len(filtered_data)
                completed_logs = len(filtered_data[filtered_data["status"] == "completed"])
                success_rate = (completed_logs / total_logs) * 100 if total_logs else 0
                st.metric("Success Rate", f"{success_rate:.2f}%")

                # Streak Information
                streaks = calculate_streaks(st.session_state.habits_data)
                st.metric("Longest Streak", f"{streaks.get(selected_habit, 0)} days")

            # Data Export
            csv = filtered_data.to_csv(index=False)
            st.download_button(label="Download Habit Data", data=csv, file_name="habit_data.csv", mime="text/csv")

    elif menu == "Dashboard":
        st.subheader("📊 User Dashboard")
        if not st.session_state.habits_data.empty:
            st.write("### Habit Overview")
            st.bar_chart(st.session_state.habits_data["status"].value_counts())
            success_rate = (
                st.session_state.habits_data["status"].value_counts().get("completed", 0) /
                len(st.session_state.habits_data)
            ) * 100
            st.metric("Overall Success Rate", f"{success_rate:.2f}%")
        else:
            st.info("No data available.")