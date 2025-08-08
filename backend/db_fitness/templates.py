# backend/db_fitness/templates.py

from typing import List
from backend.models import Template, Exercise, WorkoutSet
from backend.db_fitness.connection import get_connection


def add_template(username: str, template: Template):
    """
    Adds a new workout template with its exercises and sets.
    """
    conn = get_connection()
    c = conn.cursor()

    # Insert the main template record
    c.execute("""
        INSERT INTO templates (id, username, name, type)
        VALUES (?, ?, ?, ?)
    """, (template.id, username, template.name, template.type))

    # Insert exercises and their sets linked to this template
    for i, exercise in enumerate(template.exercises or []):
        c.execute("""
            INSERT INTO template_exercises (template_id, exercise_index, name, type)
            VALUES (?, ?, ?, ?)
        """, (template.id, i, exercise.name, exercise.type))

        for j, s in enumerate(exercise.sets):
            c.execute("""
                INSERT INTO template_sets (template_id, exercise_index, set_number, reps, weight)
                VALUES (?, ?, ?, ?, ?)
            """, (template.id, i, j, s.reps, s.weight))

    conn.commit()
    conn.close()


def delete_template(template_id: str, username: str):
    """
    Deletes a template and all its related exercises and sets.
    """
    conn = get_connection()
    c = conn.cursor()

    # Delete all sets associated with this template
    c.execute("DELETE FROM template_sets WHERE template_id = ?", (template_id,))
    # Delete all exercises associated with this template
    c.execute("DELETE FROM template_exercises WHERE template_id = ?", (template_id,))
    # Delete the template record itself for the specified user
    c.execute("DELETE FROM templates WHERE id = ? AND username = ?", (template_id, username))

    conn.commit()
    conn.close()


def get_templates(username: str) -> List[Template]:
    """
    Fetches all saved templates for the user, including nested exercises and sets.
    Each template includes all of its exercises and their sets.
    """
    conn = get_connection()
    c = conn.cursor()

    # Get all templates belonging to the user
    c.execute("SELECT id, name, type FROM templates WHERE username = ?", (username,))
    rows = c.fetchall()

    templates = []
    for template_id, name, type_ in rows:

        # Load all exercises for the current template, ordered by exercise_index
        c.execute("""
            SELECT exercise_index, name, type FROM template_exercises
            WHERE template_id = ? ORDER BY exercise_index
        """, (template_id,))
        exercise_rows = c.fetchall()

        exercises = []
        for ex_index, ex_name, ex_type in exercise_rows:
            # Load all sets for the current exercise, ordered by set_number
            c.execute("""
                SELECT reps, weight FROM template_sets
                WHERE template_id = ? AND exercise_index = ?
                ORDER BY set_number
            """, (template_id, ex_index))
            sets_data = c.fetchall()
            sets = [WorkoutSet(reps=r, weight=w) for r, w in sets_data]

            exercises.append(Exercise(name=ex_name, type=ex_type, sets=sets))

        # Append the fully constructed Template object to the list
        templates.append(Template(
            id=template_id,
            name=name,
            type=type_,
            exercises=exercises
        ))

    conn.close()
    return templates


def update_template(username: str, updated_template: Template):
    """
    Updates or replaces a template by name (case-insensitive).
    Deletes old records and inserts updated template data.
    """
    conn = get_connection()
    c = conn.cursor()

    # Find existing template by name (case-insensitive) for this user
    c.execute("""
        SELECT id FROM templates
        WHERE username = ? AND LOWER(name) = LOWER(?)
    """, (username, updated_template.name.strip()))
    result = c.fetchone()

    if result:
        existing_id = result[0]
        # Delete all sets, exercises, and the template itself for replacement
        c.execute("DELETE FROM template_sets WHERE template_id = ?", (existing_id,))
        c.execute("DELETE FROM template_exercises WHERE template_id = ?", (existing_id,))
        c.execute("DELETE FROM templates WHERE id = ? AND username = ?", (existing_id, username))

    # Insert the updated template record
    c.execute("""
        INSERT INTO templates (id, username, name, type)
        VALUES (?, ?, ?, ?)
    """, (updated_template.id, username, updated_template.name.strip(), updated_template.type))

    # Insert updated exercises and their sets
    for i, exercise in enumerate(updated_template.exercises or []):
        c.execute("""
            INSERT INTO template_exercises (template_id, exercise_index, name, type)
            VALUES (?, ?, ?, ?)
        """, (updated_template.id, i, exercise.name, exercise.type))

        for j, s in enumerate(exercise.sets):
            c.execute("""
                INSERT INTO template_sets (template_id, exercise_index, set_number, reps, weight)
                VALUES (?, ?, ?, ?, ?)
            """, (updated_template.id, i, j, s.reps, s.weight))

    conn.commit()
    conn.close()
