# Habit Tracker

A simple, interactive habit tracking application built with Python and Streamlit. This app enables users to add, log, visualize, and monitor their daily habits, supporting personal productivity and self-improvement.

## Features

- **User Authentication:** Register and log in with your own credentials.
- **Add Habits:** Define new habits and attach optional notes.
- **Log Habit Progress:** Track daily status of habits as "completed," "inprogress," or "skipped."
- **View Habit Logs:** Browse historical logs of all your habits.
- **Visualize Progress:** 
  - Pie charts for habit status distribution.
  - Heatmaps for habit activity over time.
  - Calculation of streaks (longest chain of consecutive days).
- **Dashboard:** Overview of your habit statistics, including success rates.
- **Export:** Download your habit data as a CSV file.

## Technologies Used

- **Python 3**
- **Streamlit:** For building the interactive web interface.
- **Pandas:** Data manipulation and analysis.
- **Matplotlib & Seaborn:** Data visualization.
- **SQLite:** Local database for storing user and habit data.

## How to Use

1. **Clone the repository:**
   ```bash
   git clone https://github.com/fathimashakoor079/Habit_Tracker.git
   cd Habit_Tracker
   ```

2. **Install dependencies:**
   ```bash
   pip install streamlit pandas matplotlib seaborn
   ```

3. **Run the application:**
   ```bash
   streamlit run app.py
   ```

4. **Register or log in:**  
   Use the sidebar to register a new account or log in with your credentials.

5. **Start tracking:**
   - Add new habits using the "Add Habit" menu.
   - Log progress daily on the "Log Habit" menu.
   - Visualize your streaks and performance from the "Visualize Habits" or "Dashboard" menus.
   - Export your data anytime for analysis.

## Database

- User and habit data are stored locally in `habit_tracker.db` (SQLite database).
- Two tables: `users` (id, username, password) and `habits` (id, user_id, name, date, status, notes).

---

*Made by [fathimashakoor079](https://github.com/fathimashakoor079)*
