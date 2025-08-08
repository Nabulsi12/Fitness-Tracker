# frontend/templates.py

import streamlit as st
from typing import List
from backend.models import Template, Exercise, WorkoutSet
from backend.db_fitness.templates import add_template, get_templates, delete_template, update_template
import uuid

def templates_page(username: str):
    st.header("Manage Workout Templates")

    # Load templates from backend each run
    templates = get_templates(username)

    # Initialize session state variables if they don't exist
    if "template_mode" not in st.session_state:
        st.session_state.template_mode = "View Templates"  # or "Add New Template"
    if "edit_template_id" not in st.session_state:
        st.session_state.edit_template_id = None
    if "template_exercises" not in st.session_state:
        st.session_state.template_exercises = []
    if "template_name_input" not in st.session_state:
        st.session_state.template_name_input = ""

    # Mode radio (View / Add New)
    mode = st.radio(
        "Mode",
        ["View Templates", "Add New Template"],
        index=["View Templates", "Add New Template"].index(st.session_state.template_mode),
        horizontal=True,
    )
    st.session_state.template_mode = mode

    # --- VIEW MODE ---
    if mode == "View Templates":
        if not templates:
            st.info("You don't have any templates yet.")
            # Button to switch to Add mode
            if st.button("➕ Create New Template"):
                st.session_state.template_mode = "Add New Template"
                st.session_state.edit_template_id = None
                st.session_state.template_name_input = ""
                st.session_state.template_exercises = []
                return  # Immediate return to refresh UI
            return

        # Select a template to view
        selected = st.selectbox("Select Template:", templates, format_func=lambda t: t.name)

        st.subheader(f"Template: {selected.name}")
        st.write("Exercises:")
        for i, ex in enumerate(selected.exercises):
            st.markdown(f"**{i+1}. {ex.name}** ({ex.type})")
            if ex.type in ["strength", "bodyweight"]:
                for j, s in enumerate(ex.sets):
                    reps = s.reps if s.reps is not None else "-"
                    weight = s.weight if s.weight is not None else "-"
                    st.write(f" - Set {j+1}: {reps} reps, {weight} lbs")
            elif ex.type == "cardio":
                for j, s in enumerate(ex.sets):
                    time = s.reps if s.reps is not None else "-"
                    dist = s.weight if s.weight is not None else "-"
                    st.write(f" - Cardio {j+1}: {time} min, {dist} mi")

        # Edit and Delete buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✏️ Edit This Template"):
                # Load template into session state for editing
                st.session_state.template_name_input = selected.name
                st.session_state.template_exercises = [
                    {
                        "name": ex.name,
                        "type": ex.type,
                        "sets": [{"reps": s.reps, "weight": s.weight} for s in ex.sets],
                    }
                    for ex in selected.exercises
                ]
                st.session_state.edit_template_id = selected.id
                st.session_state.template_mode = "Add New Template"
                return  # Stop here to refresh UI
        with col2:
            if st.button("🗑️ Delete This Template"):
                try:
                    delete_template(selected.id, username)  # Correct param order
                    st.success("Template deleted successfully.")
                    # Reset edit state if deleting the current edited template
                    if st.session_state.edit_template_id == selected.id:
                        st.session_state.edit_template_id = None
                    # Reset form and go back to view mode
                    st.session_state.template_name_input = ""
                    st.session_state.template_exercises = []
                    st.session_state.template_mode = "View Templates"
                    return  # Immediate return to refresh UI
                except Exception as e:
                    st.error(f"Failed to delete template: {e}")

        return  # End view mode UI

    # --- ADD / EDIT MODE ---
    st.subheader("Add/Edit Template")

    # Template name input
    template_name = st.text_input("Template Name", value=st.session_state.template_name_input)
    st.session_state.template_name_input = template_name

    # Exercises form
    for idx, ex in enumerate(st.session_state.template_exercises):
        st.markdown("---")
        st.markdown(f"### Exercise {idx + 1}")

        ex_name = st.text_input("Exercise Name", value=ex.get("name", ""), key=f"ex_name_{idx}")
        ex_type = st.selectbox(
            "Exercise Type",
            ["strength", "bodyweight", "cardio"],
            index=["strength", "bodyweight", "cardio"].index(ex.get("type", "strength")),
            key=f"ex_type_{idx}",
        )

        st.session_state.template_exercises[idx]["name"] = ex_name
        st.session_state.template_exercises[idx]["type"] = ex_type

        if "sets" not in ex:
            st.session_state.template_exercises[idx]["sets"] = []

        # Input sets depending on exercise type
        if ex_type in ["strength", "bodyweight"]:
            num_sets = st.number_input(
                "Number of Sets",
                min_value=1,
                max_value=20,
                value=len(ex["sets"]) or 1,
                step=1,
                key=f"setnum_{idx}",
            )

            sets = ex.get("sets", [])
            # Adjust sets length to match num_sets
            if len(sets) < num_sets:
                sets.extend([{"reps": 0, "weight": 0.0}] * (num_sets - len(sets)))
            elif len(sets) > num_sets:
                sets = sets[:num_sets]

            for sidx in range(num_sets):
                col1, col2 = st.columns(2)
                with col1:
                    reps = st.number_input(
                        "Reps",
                        min_value=0,
                        value=sets[sidx].get("reps", 0) or 0,
                        step=1,
                        key=f"ex{idx}_reps_{sidx}",
                    )
                with col2:
                    weight = st.number_input(
                        "Weight (lbs)",
                        min_value=0.0,
                        value=sets[sidx].get("weight", 0.0) or 0.0,
                        step=0.5,
                        key=f"ex{idx}_weight_{sidx}",
                    )
                sets[sidx] = {"reps": reps, "weight": weight}

            st.session_state.template_exercises[idx]["sets"] = sets

        elif ex_type == "cardio":
            col1, col2 = st.columns(2)
            with col1:
                duration = st.number_input(
                    "Duration (minutes)",
                    min_value=0,
                    value=ex.get("sets", [{}])[0].get("reps", 0) or 0,
                    step=1,
                    key=f"ex{idx}_duration",
                )
            with col2:
                distance = st.number_input(
                    "Distance (mi)",
                    min_value=0.0,
                    value=ex.get("sets", [{}])[0].get("weight", 0.0) or 0.0,
                    step=0.1,
                    key=f"ex{idx}_distance",
                )
            st.session_state.template_exercises[idx]["sets"] = [{"reps": duration, "weight": distance}]

        # Delete exercise button
        if st.button(f"🗑️ Delete Exercise {idx + 1}", key=f"del_ex_{idx}"):
            st.session_state.template_exercises.pop(idx)
            return  # Return immediately to avoid stale keys / rerun issues

    # Add Exercise Button at bottom
    if st.button("➕ Add Exercise"):
        st.session_state.template_exercises.append({"name": "", "type": "strength", "sets": []})
        return  # Return immediately to update UI with new exercise input

    st.markdown("---")

    # Save Template Button
    if st.button("💾 Save Template"):
        # Validate inputs
        if not template_name.strip():
            st.error("Template Name is required.")
            return
        if not st.session_state.template_exercises:
            st.error("Add at least one exercise.")
            return

        # Build Exercise list for backend
        built_exercises: List[Exercise] = []
        for ex in st.session_state.template_exercises:
            sets: List[WorkoutSet] = []
            for s in ex["sets"]:
                reps = s.get("reps")
                weight = s.get("weight")
                # Convert zero values to None (optional, depends on your backend logic)
                reps = reps if reps != 0 else None
                weight = weight if weight != 0 else None
                sets.append(WorkoutSet(reps=reps, weight=weight))
            built_exercises.append(
                Exercise(name=ex["name"].strip(), type=ex["type"], sets=sets)
            )

        # Create Template instance WITHOUT id param
        new_template = Template.create(
            name=template_name.strip(),
            type="mixed",
            exercises=built_exercises,
        )
        # Assign id after creation (for update or add)
        new_template.id = st.session_state.edit_template_id or str(uuid.uuid4())

        try:
            if st.session_state.edit_template_id:
                # Update existing template
                update_template(username, new_template)
                st.success("Template updated successfully.")
                st.session_state.edit_template_id = None
            else:
                # Add new template
                add_template(username, new_template)
                st.success("Template saved successfully.")

            # Clear session state to reset form & go back to view mode
            st.session_state.template_exercises = []
            st.session_state.template_name_input = ""
            st.session_state.template_mode = "View Templates"

        except Exception as e:
            st.error(f"Failed to save template: {e}")
