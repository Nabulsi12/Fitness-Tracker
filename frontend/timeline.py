# frontend/timeline.py

import streamlit as st
from backend.models import Workout
from backend.db_fitness.workouts import delete_workout, update_workout
from frontend.add_workout import input_workout
from typing import List
from datetime import date
from backend.filters import filter_workouts_by_date_range, filter_workouts_by_type

def show_timeline(workouts: List[Workout]):
    """
    Renders a timeline view of all workouts with options to edit or delete.
    Displays each workout inside an expandable box sorted by date (latest first).
    """
    st.header("🏋️ Workout Timeline")

    if not workouts:
        st.info("No workouts to display.")
        return

    #--- Filtering Workouts ---
    col1, col2 = st.columns(2)
    with col1: 
        start_date = st.date_input("Start Date", value=None)
    with col2:
        end_date = st.date_input("End Date", value=None)

    workout_type = [ "All", "Strength", "Bodyweight", "Cardio" ]
    selected_type = st.selectbox("Filter by Type", workout_type, index=0)

    #--- Apply Filters ---
    # Filter by type if not "All"
    if selected_type != "All":
        workouts = filter_workouts_by_type(workouts, selected_type.lower())
    
    # Filter by date range if dates selected (and not default today)
    # Treat todays date as no filter
    start_filter = start_date if start_date != date.today() else None
    end_filter = end_date if end_date != date.today() else None
    workouts = filter_workouts_by_date_range(workouts, start_filter, end_filter)

    # Sort workouts by date, latest first
    sorted_workouts = sorted(workouts, key=lambda w: w.date, reverse=True)

    for workout in sorted_workouts:
        # Unique expander for each workout
        with st.expander(f"{workout.date.strftime('%Y-%m-%d')} - {workout.name} ({workout.type})"):

            # ----------------- Show workout data ------------------
            if workout.exercises:
                for ex in workout.exercises:
                    st.markdown(f"**Exercise: {ex.name}**")
                    if ex.type in ["strength", "bodyweight"]:
                        if ex.sets:
                            for i, s in enumerate(ex.sets):
                                st.text(f"Set {i + 1}: {s.reps} reps @ {s.weight} lbs")
                        else:
                            st.text("No sets recorded for this exercise.")

                    elif ex.type == "cardio":
                        st.text(f"Duration: {ex.duration_minutes or 'Unknown'} min")
                        st.text(f"Distance: {ex.distance_mi or 'Unknown'} miles")
            else:
                st.text("No exercises recorded.")

            # ------------- Action Buttons (Edit/Delete) --------------

            # Unique keys for each workout's buttons
            edit_key = f"edit_{workout.id}"
            delete_key = f"delete_button_{workout.id}"
            confirm_key = f"confirm_delete_{workout.id}"
            confirm_btn_key = f"confirm_button_{workout.id}"

            # Button to edit workout
            if st.button("✏️ Edit Workout", key=edit_key):
                st.session_state.edit_mode = {
                    "id": workout.id,
                    "data": workout
                }

            # Button to trigger delete confirmation
            if st.button("🗑️ Delete Workout", key=delete_key):
                st.session_state[confirm_key] = True  # flag to show confirm delete

            # If delete is clicked, show confirmation prompt
            if st.session_state.get(confirm_key, False):
                st.warning("Are you sure you want to delete this workout?")
                if st.button("✅ Confirm Delete", key=confirm_btn_key):
                    delete_workout(st.session_state.user, workout.id)
                    st.success("Workout deleted.")
                    st.session_state.pop(confirm_key, None)
                    st.rerun()

    # ---------------- Edit Mode ----------------
    if hasattr(st.session_state, "edit_mode"):
        st.subheader("🛠️ Edit Workout")
        workout_data = st.session_state.edit_mode["data"]

        # Show the existing workout in the input form
        st.session_state["edit_workout"] = workout_data
        edited_workout = input_workout(st.session_state.user)

        if edited_workout:
            update_workout(st.session_state.user, workout_data.id, edited_workout)
            st.success("✅ Workout updated!")
            del st.session_state.edit_mode
            st.rerun()
