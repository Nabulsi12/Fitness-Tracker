# backend/validators.py

from typing import List, Optional
from backend.models import Exercise

def validate_workout(
    workout_type: str,
    date: str,
    name: str,
    exercises: Optional[List[Exercise]] = None,
    duration: Optional[int] = None,
    distance: Optional[float] = None,
) -> Optional[str]:
    """
    Validates workout input based on its type.
    Returns an error string if invalid, otherwise None.
    """

    if not name:
        return "Workout name is required."

    if not date:
        return "Workout date is required."

    if workout_type in ["strength", "bodyweight"]:
        if not exercises or not isinstance(exercises, list):
            return "Exercises must be a non-empty list."

        for ex_i, ex in enumerate(exercises):
            if ex.type in ["strength", "bodyweight"]:
                if not ex.sets or not isinstance(ex.sets, list) or len(ex.sets) == 0:
                    return f"Exercise {ex_i + 1} ('{ex.name}') must have at least one set."

                for set_i, s in enumerate(ex.sets):
                    if not isinstance(s.reps, int) or s.reps <= 0:
                        return f"Exercise {ex_i + 1}, Set {set_i + 1}: Reps must be a positive integer."

                    if not isinstance(s.weight, (int, float)):
                        return f"Exercise {ex_i + 1}, Set {set_i + 1}: Weight must be a number."

                    if workout_type == "bodyweight" and s.weight < 50:
                        return f"Exercise {ex_i + 1}, Set {set_i + 1}: Weight must be equivalent to your bodyweight workouts."

                    if workout_type == "strength" and s.weight <= 0:
                        return f"Exercise {ex_i + 1}, Set {set_i + 1}: Weight must be greater than 0 for strength workouts."

            elif ex.type == "cardio":
                if ex.duration_minutes is None or ex.duration_minutes <= 0:
                    return f"Exercise {ex_i + 1} ('{ex.name}') must have a positive duration for cardio workouts."
                if ex.distance_mi is None or ex.distance_mi < 0:
                    return f"Exercise {ex_i + 1} ('{ex.name}') must have a non-negative distance for cardio workouts."
            else:
                # If unknown exercise type either skip or add validation
                pass
            
    elif workout_type == "cardio":
        if duration is None or not isinstance(duration, (int, float)) or duration <= 0:
            return "Cardio duration must be a positive number."

        if distance is None or not isinstance(distance, (int, float)) or distance < 0:
            return "Cardio distance must be 0 or more."

    else:
        return f"Invalid workout type: {workout_type}"

    return None
