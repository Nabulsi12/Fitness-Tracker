# frontend/add_workout.py

import streamlit as st
from datetime import date
from typing import Optional

from backend.models import Workout, WorkoutSet, Exercise
from backend.validators import validate_workout
from backend.db_fitness.workouts import add_workout, update_workout
from backend.db_fitness.templates import get_templates

def mark_template_change():
    """Trigger flag when template selection changes."""
    st.session_state["template_changed"] = True

def input_workout(username: str):
    """
    Render the Add Workout form.
    Supports editing, loading from template, and creating new workouts.
    """

    # --- Template Selection ---
    templates = get_templates(username)
    template_names = [t.name for t in templates]
    last_loaded_template = st.session_state.get("template_loaded", None)

    selected_template_name = st.selectbox(
        "\U0001F4C4 Load Template (optional)",
        ["None"] + template_names,
        index=(["None"] + template_names).index(last_loaded_template) if last_loaded_template else 0,
        key="template_select",
        on_change=mark_template_change
    )

    if (
        st.session_state.get("template_changed")
        and selected_template_name != "None"
        and selected_template_name != last_loaded_template
    ):
        selected_template = next(t for t in templates if t.name == selected_template_name)

        st.session_state["edit_workout"] = Workout.create(
            type=selected_template.type,
            date=date.today(),
            name=selected_template.name,
            exercises=selected_template.exercises,
            sets=[],
            duration_minutes=None,
            distance_mi=None,
            intensity=None
        )

        st.session_state["template_loaded"] = selected_template_name
        st.session_state["template_changed"] = False
        st.rerun()

    if selected_template_name == "None":
        st.session_state.pop("template_loaded", None)

    edit_workout: Optional[Workout] = st.session_state.get("edit_workout", None)

    valid_types = ["strength", "bodyweight", "cardio"]
    default_type = edit_workout.type if edit_workout and edit_workout.type in valid_types else "strength"

    workout_type = st.selectbox(
        "Workout Type",
        options=valid_types,
        index=valid_types.index(default_type)
)


    workout_date = st.date_input("Date", value=edit_workout.date if edit_workout else date.today())
    workout_name = st.text_input("Workout Name", value=edit_workout.name if edit_workout else "")

    exercises = []
    duration = None
    distance = None
    intensity = None

    if workout_type in ["strength", "bodyweight"]:
        st.subheader("Exercises")

        existing_exercises = edit_workout.exercises if edit_workout and edit_workout.exercises else []

        num_exercises = st.number_input(
            "Number of Exercises",
            min_value=1,
            max_value=20,
            value=len(existing_exercises) if existing_exercises else 1,
            step=1,
        )

        for i in range(num_exercises):
            ex_name = existing_exercises[i].name if i < len(existing_exercises) else f"Exercise {i+1}"
            ex_type = existing_exercises[i].type if i < len(existing_exercises) else workout_type
            sets_in_ex = existing_exercises[i].sets if i < len(existing_exercises) else []

            exercise_name = st.text_input(f"Exercise {i+1} Name", value=ex_name, key=f"exercise_name_{i}")
            exercise_type = st.selectbox(
                f"Type for {exercise_name}",
                options=["strength", "bodyweight", "cardio"],
                index=["strength", "bodyweight", "cardio"].index(ex_type),
                key=f"exercise_type_{i}"
            )

            exercise_sets = []
            if exercise_type in ["strength", "bodyweight"]:
                num_sets = st.number_input(
                    f"Number of Sets for {exercise_name}",
                    min_value=1,
                    max_value=10,
                    value=len(sets_in_ex) if sets_in_ex else 1,
                    step=1,
                    key=f"num_sets_{i}",
                )

                for j in range(num_sets):
                    rep_val = sets_in_ex[j].reps if j < len(sets_in_ex) else 0
                    weight_val = sets_in_ex[j].weight if j < len(sets_in_ex) else 0.0

                    col1, col2 = st.columns(2)
                    with col1:
                        reps = st.number_input(
                            f"{exercise_name} - Set {j+1} Reps",
                            min_value=0,
                            value=rep_val,
                            step=1,
                            key=f"reps_{i}_{j}"
                        )
                    with col2:
                        weight = st.number_input(
                            f"{exercise_name} - Set {j+1} Weight (lbs)",
                            min_value=0.0,
                            value=weight_val,
                            step=0.5,
                            key=f"weight_{i}_{j}"
                        )
                    exercise_sets.append(WorkoutSet(reps=reps, weight=weight))

            elif exercise_type == "cardio":
                col1, col2 = st.columns(2)
                with col1:
                    duration = st.number_input(
                        f"{exercise_name} - Duration (minutes)",
                        min_value=0,
                        value=existing_exercises[i].sets[0].reps if i < len(existing_exercises) and existing_exercises[i].sets else 30,
                        step=1,
                        key=f"duration_{i}"
                    )
                with col2:
                    distance = st.number_input(
                        f"{exercise_name} - Distance (mi)",
                        min_value=0.0,
                        value=existing_exercises[i].sets[0].weight if i < len(existing_exercises) and existing_exercises[i].sets else 1.0,
                        step=0.1,
                        key=f"distance_{i}"
                    )
                exercise_sets = [WorkoutSet(reps=duration, weight=distance)]

            exercises.append(Exercise(name=exercise_name, type=exercise_type, sets=exercise_sets))

    else:  # workout_type == cardio (single-entry workout)
        duration = st.number_input(
            "Duration (minutes)",
            min_value=0,
            value=edit_workout.duration_minutes if edit_workout else 0,
            step=1,
        )
        distance = st.number_input(
            "Distance (mi)",
            min_value=0.0,
            value=edit_workout.distance_mi if edit_workout else 0.0,
            step=0.1,
        )
        intensity_options = ["Low", "Medium", "High"]
        intensity = st.selectbox(
            "Intensity",
            options=intensity_options,
            index=intensity_options.index(edit_workout.intensity) if (edit_workout and edit_workout.intensity in intensity_options) else 0,
        )
        sets = []
        exercises = None

    if st.button("Save Workout"):
        error = validate_workout(
            workout_type=workout_type,
            date=workout_date.isoformat(),
            name=workout_name.strip(),
            exercises=exercises if workout_type in ["strength", "bodyweight"] else None,
            duration=duration,
            distance=distance,
            intensity=intensity,
        )

        if error:
            st.error(f"Validation error: {error}")
            return

        workout = Workout.create(
            type=workout_type,
            date=workout_date,
            name=workout_name.strip(),
            sets=[] if workout_type == "cardio" else None,
            exercises=exercises,
            duration_minutes=duration,
            distance_mi=distance,
            intensity=intensity,
        )

        try:
            if "template_loaded" in st.session_state:
                # If the user loaded from a template, it's a new workout
                add_workout(username, workout)
                st.success(f"Workout '{workout_name}' added from template!")
                del st.session_state["edit_workout"]
                del st.session_state["template_loaded"]

            elif edit_workout:
                # Editing an existing workout
                update_workout(username, edit_workout.id, workout)
                st.success(f"Workout '{workout_name}' updated successfully!")
                del st.session_state["edit_workout"]

            else:
                # Brand new workout not from template
                add_workout(username, workout)
                st.success(f"Workout '{workout_name}' added successfully!")

        except Exception as e:
            st.error(f"Error saving workout: {e}")
