# frontend/timeline.py

import streamlit as st
from backend.models import Workout
from backend.db_fitness.workouts import delete_workout, update_workout
from frontend.add_workout import input_workout
from typing import List


def show_timeline(workouts: List[Workout]):
    """
    Renders a timeline view of all workouts with options to edit or delete.
    Displays each workout inside an expandable box sorted by date (latest first).
    """
    st.header("🏋️ Workout Timeline")

    if not workouts:
        st.info("No workouts to display.")
        return

    # Sort workouts by date, latest first
    sorted_workouts = sorted(workouts, key=lambda w: w.date, reverse=True)

    for workout in sorted_workouts:
        # Unique expander for each workout
        with st.expander(f"{workout.date.strftime('%Y-%m-%d')} - {workout.name} ({workout.type})"):

            # ----------------- Show workout data ------------------
            if workout.type in ["strength", "bodyweight"]:
                if workout.exercises:
                    for ex in workout.exercises:
                        st.markdown(f"**Exercise: {ex.name}**")
                        if ex.sets:
                            for i, s in enumerate(ex.sets):
                                st.text(f"Set {i + 1}: {s.reps} reps @ {s.weight} lbs")
                        else:
                            st.text("No sets recorded for this exercise.")
                else:
                    st.text("No exercises recorded.")

            elif workout.type == "cardio":
                st.text(f"Duration: {workout.duration_minutes or 'Unknown'} min")
                st.text(f"Distance: {workout.distance_mi or 'Unknown'} miles")
                st.text(f"Intensity: {workout.intensity or 'Unknown'}")

            st.markdown("---")

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
