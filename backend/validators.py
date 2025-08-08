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
    intensity: Optional[str] = None
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
            if not ex.sets or not isinstance(ex.sets, list):
                return f"Exercise {ex_i + 1} ('{ex.name}') must have at least one set."

            for set_i, s in enumerate(ex.sets):
                if not isinstance(s.reps, int) or s.reps <= 0:
                    return f"Exercise {ex_i + 1}, Set {set_i + 1}: Reps must be a positive integer."

                if not isinstance(s.weight, (int, float)):
                    return f"Exercise {ex_i + 1}, Set {set_i + 1}: Weight must be a number."

                if workout_type == "bodyweight" and s.weight < 0:
                    return f"Exercise {ex_i + 1}, Set {set_i + 1}: Weight must be 0 or more for bodyweight workouts."

                if workout_type == "strength" and s.weight <= 0:
                    return f"Exercise {ex_i + 1}, Set {set_i + 1}: Weight must be greater than 0 for strength workouts."

    elif workout_type == "cardio":
        if duration is None or not isinstance(duration, (int, float)) or duration <= 0:
            return "Cardio duration must be a positive number."

        if distance is None or not isinstance(distance, (int, float)) or distance < 0:
            return "Cardio distance must be 0 or more."

        if intensity not in ["Low", "Medium", "High"]:
            return "Cardio intensity must be one of: Low, Medium, or High."

    else:
        return f"Invalid workout type: {workout_type}"

    return None
