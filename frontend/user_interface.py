# frontend/user_interface.py

import streamlit as st
from frontend.timeline import show_timeline
from frontend.add_workout import input_workout
from frontend.templates import templates_page
from backend.auth import login_user, signup_user
from backend.db_fitness.workouts import get_all_workouts

def run_session():
    """
    Main controller for login and navigation logic.
    Handles session state and routes to pages after login.
    """

    # Setup session defaults
    if "user" not in st.session_state:
        st.session_state.user = None
    if "page" not in st.session_state:
        st.session_state.page = "Timeline"

    # --- LOGIN / SIGNUP SCREEN ---
    if st.session_state.user is None:
        st.title("🏋️ Fitness Tracker Login")

        tab1, tab2 = st.tabs(["Login", "Signup"])

        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login")

                if submitted:
                    if login_user(username, password):
                        st.session_state.user = username
                        st.success(f"✅ Welcome, {username}!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials")

        with tab2:
            with st.form("signup_form"):
                new_username = st.text_input("New Username")
                new_password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                signup_submitted = st.form_submit_button("Sign Up")

                if signup_submitted:
                    if new_password != confirm_password:
                        st.error("❌ Passwords do not match")
                    elif signup_user(new_username, new_password):
                        st.success("✅ Signup successful! Please login.")
                    else:
                        st.error("⚠️ Username already exists")

        return  # End early if not logged in

    # --- APP UI AFTER LOGIN ---
    st.sidebar.write(f"🔒 Logged in as: {st.session_state.user}")

    # Sidebar navigation
    page_options = ["Add Workout", "Templates", "Timeline"]
    page = st.sidebar.selectbox(
        "📋 Navigation",
        page_options,
        index=page_options.index(st.session_state.page)
    )

    if page != st.session_state.page:
        st.session_state.page = page

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.session_state.page = "Timeline"
        st.rerun()

    # --- PAGE ROUTING ---
    if st.session_state.page == "Timeline":
        workouts = get_all_workouts(st.session_state.user)
        show_timeline(workouts)

    elif st.session_state.page == "Add Workout":
        input_workout(st.session_state.user)

    elif st.session_state.page == "Templates":
        templates_page(st.session_state.user)
