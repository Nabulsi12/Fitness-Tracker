# backend/db_fitness/workouts.py

from typing import List
from datetime import datetime
from backend.models import Workout, WorkoutSet, Exercise
from backend.db_fitness.connection import get_connection


def add_workout(username: str, workout: Workout):
    """
    Adds a workout including its exercises and sets to the database.
    Inserts cardio workouts with distance and duration, strength/bodyweight workouts with exercises and sets.
    """
    conn = get_connection()
    c = conn.cursor()

    try:
        # Insert main workout record
        c.execute("""
            INSERT INTO workouts (id, username, name, type, date, duration_minutes, distance_mi)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            workout.id,
            username,
            workout.name,
            workout.type,
            workout.date.isoformat(),
            workout.duration_minutes,
            workout.distance_mi,
        ))

        # Insert each exercise and its sets associated with this workout
        if workout.exercises:
            for i, exercise in enumerate(workout.exercises):
                c.execute("""
                    INSERT INTO workout_exercises (workout_id, exercise_index, name, type, duration_minutes, distance_mi)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (workout.id, 
                      i, 
                      exercise.name, 
                      exercise.type, 
                      exercise.duration_minutes if exercise.type == "cardio" else None, 
                      exercise.distance_mi if exercise.type == "cardio" else None
                    ))
                
                # Sets only for only strength/bodyweight workouts
                if exercise.type in ["strength", "bodyweight"] and exercise.sets:
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
        SELECT id, name, type, date, duration_minutes, distance_mi
        FROM workouts WHERE username = ?
    """, (username,))
    workout_rows = c.fetchall()

    workouts = []
    for workout_id, name, type_, date_str, duration, distance in workout_rows:
        # Fetch exercises for this workout ordered by index
        c.execute("""
            SELECT exercise_index, name, type, duration_minutes, distance_mi
            FROM workout_exercises
            WHERE workout_id = ? ORDER BY exercise_index
        """, (workout_id,))
        exercise_rows = c.fetchall()

        exercises = []
        for ex_index, ex_name, ex_type, dur_min, dist_mi in exercise_rows:
            if ex_type in ["strength", "bodyweight"]:
                # Fetch sets for each exercise ordered by set number
                c.execute("""
                    SELECT reps, weight FROM exercise_sets
                    WHERE workout_id = ? AND exercise_index = ?
                    ORDER BY set_number
                """, (workout_id, ex_index))

                sets = [WorkoutSet(reps=r, weight=w) for r, w in c.fetchall()]
                exercises.append(Exercise(name=ex_name, type=ex_type, sets=sets))
            
            elif ex_type == "cardio":
                # Cardio has no sets, add extra logic to store cardio details per exercise(not in DB schema)
                # Assign none to sets here to avoid confusion
                exercises.append(Exercise(
                    name=ex_name,
                    type=ex_type,
                    sets=None,
                    duration_minutes= dur_min,
                    distance_mi= dist_mi,
                    ))
            else:
                # Fallback: treat as strength/bodyweight with no sets
                exercises.append(Exercise(name=ex_name, type=ex_type, sets=[]))

        workouts.append(Workout(
            id=workout_id,
            name=name,
            type=type_,
            date=datetime.fromisoformat(date_str).date(),
            exercises=exercises or None,
            duration_minutes=duration,
            distance_mi=distance
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
        UPDATE workouts SET name = ?, type = ?, date = ?, duration_minutes = ?, distance_mi = ?
        WHERE id = ? AND username = ?
    """, (
        workout.name,
        workout.type,
        workout.date.isoformat(),
        workout.duration_minutes,
        workout.distance_mi,
        workout_id,
        username
    ))

    # Delete existing exercises and sets for the workout to replace with updated data
    c.execute("DELETE FROM workout_exercises WHERE workout_id = ?", (workout_id,))
    c.execute("DELETE FROM exercise_sets WHERE workout_id = ?", (workout_id,))

    # Insert updated exercises and sets
    for i, exercise in enumerate(workout.exercises or []):
        c.execute("""
            INSERT INTO workout_exercises (workout_id, exercise_index, name, type, duration_minutes, distance_mi)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (workout_id, i, exercise.name, exercise.type, exercise.duration_minutes, exercise.distance_mi))
        if exercise.type in ["strength", "bodyweight"] and exercise.sets:
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
