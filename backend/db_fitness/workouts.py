# backend/db_fitness/workouts.py

from typing import List
from datetime import datetime
from backend.models import Workout, WorkoutSet, Exercise
from backend.db_fitness.connection import get_connection


def add_workout(username: str, workout: Workout):
    """
    Adds a workout including its exercises and sets to the database.
    """
    conn = get_connection()
    c = conn.cursor()

    try:
        # Insert main workout record
        c.execute("""
            INSERT INTO workouts (id, username, name, type, date, duration_minutes, distance_mi, intensity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            workout.id,
            username,
            workout.name,
            workout.type,
            workout.date.isoformat(),
            workout.duration_minutes,
            workout.distance_mi,
            workout.intensity,
        ))

        # Insert each exercise and its sets associated with this workout
        if workout.exercises:
            for i, exercise in enumerate(workout.exercises):
                c.execute("""
                    INSERT INTO workout_exercises (workout_id, exercise_index, name, type)
                    VALUES (?, ?, ?, ?)
                """, (workout.id, i, exercise.name, exercise.type))

                for j, s in enumerate(exercise.sets):
                    c.execute("""
                        INSERT INTO exercise_sets (workout_id, exercise_index, set_number, reps, weight)
                        VALUES (?, ?, ?, ?, ?)
                    """, (workout.id, i, j, s.reps, s.weight))

        conn.commit()

    except Exception as e:
        # Propagate exceptions to calling code; no swallowing errors here
        raise

    finally:
        conn.close()


def get_all_workouts(username: str) -> List[Workout]:
    """
    Fetches all workouts for a user, including all nested exercises and sets.
    Returns a list of fully constructed Workout objects.
    """
    conn = get_connection()
    c = conn.cursor()

    # Get basic workout info for all workouts belonging to the user
    c.execute("""
        SELECT id, name, type, date, duration_minutes, distance_mi, intensity
        FROM workouts WHERE username = ?
    """, (username,))
    rows = c.fetchall()

    workouts = []
    for row in rows:
        workout_id, name, type_, date_str, duration, distance, intensity = row

        # Fetch exercises for this workout ordered by index
        c.execute("""
            SELECT exercise_index, name, type FROM workout_exercises
            WHERE workout_id = ? ORDER BY exercise_index
        """, (workout_id,))
        exercise_rows = c.fetchall()

        exercises = []
        for ex_index, ex_name, ex_type in exercise_rows:
            # Fetch sets for each exercise ordered by set number
            c.execute("""
                SELECT reps, weight FROM exercise_sets
                WHERE workout_id = ? AND exercise_index = ?
                ORDER BY set_number
            """, (workout_id, ex_index))

            sets = [WorkoutSet(reps=r, weight=w) for r, w in c.fetchall()]
            exercises.append(Exercise(name=ex_name, type=ex_type, sets=sets))

        workouts.append(Workout(
            id=workout_id,
            name=name,
            type=type_,
            date=datetime.fromisoformat(date_str).date(),
            exercises=exercises or None,
            duration_minutes=duration,
            distance_mi=distance,
            intensity=intensity
        ))

    conn.close()
    return workouts


def update_workout(username: str, workout_id: str, workout: Workout):
    """
    Updates an existing workout and all its nested exercises and sets.
    """
    conn = get_connection()
    c = conn.cursor()

    # Update core workout data
    c.execute("""
        UPDATE workouts SET name = ?, type = ?, date = ?, duration_minutes = ?, distance_mi = ?, intensity = ?
        WHERE id = ? AND username = ?
    """, (
        workout.name,
        workout.type,
        workout.date.isoformat(),
        workout.duration_minutes,
        workout.distance_mi,
        workout.intensity,
        workout_id,
        username
    ))

    # Delete existing exercises and sets for the workout to replace with updated data
    c.execute("DELETE FROM workout_exercises WHERE workout_id = ?", (workout_id,))
    c.execute("DELETE FROM exercise_sets WHERE workout_id = ?", (workout_id,))

    # Insert updated exercises and sets
    for i, exercise in enumerate(workout.exercises or []):
        c.execute("""
            INSERT INTO workout_exercises (workout_id, exercise_index, name, type)
            VALUES (?, ?, ?, ?)
        """, (workout_id, i, exercise.name, exercise.type))

        for j, s in enumerate(exercise.sets):
            c.execute("""
                INSERT INTO exercise_sets (workout_id, exercise_index, set_number, reps, weight)
                VALUES (?, ?, ?, ?, ?)
            """, (workout_id, i, j, s.reps, s.weight))

    conn.commit()
    conn.close()


def delete_workout(username: str, workout_id: str):
    """
    Deletes a workout and all associated exercises and sets.
    """
    conn = get_connection()
    c = conn.cursor()

    # Delete all sets for this workout
    c.execute("DELETE FROM exercise_sets WHERE workout_id = ?", (workout_id,))
    # Delete all exercises for this workout
    c.execute("DELETE FROM workout_exercises WHERE workout_id = ?", (workout_id,))
    # Delete the workout record itself for this user
    c.execute("DELETE FROM workouts WHERE id = ? AND username = ?", (workout_id, username))

    conn.commit()
    conn.close()
