# backend/models.py

from dataclasses import dataclass
from typing import List, Optional
from datetime import date
import uuid

# ------------------ Workout Set ------------------

@dataclass
class WorkoutSet:
    reps: Optional[int]
    weight: Optional[float]  # lbs


# ------------------ Exercise ------------------
# Added optional duration and distance fields to support cardio exercises,
# while still supporting sets for strength/bodyweight exercises.

@dataclass
class Exercise:
    name: str
    type: str  # e.g. 'strength', 'bodyweight', 'cardio', etc.
    sets: Optional[List[WorkoutSet]] = None  # Only for strength/bodyweight
    duration_minutes: Optional[float] = None  # For cardio exercises
    distance_mi: Optional[float] = None  # For cardio exercises


# ------------------ Workout ------------------

@dataclass
class Workout:
    id: str
    type: str
    date: date
    name: str
    sets: Optional[List[WorkoutSet]] = None  # Legacy or individual sets
    exercises: Optional[List[Exercise]] = None  # Full exercise list, supporting cardio & strength
    duration_minutes: Optional[int] = None  # Total workout duration (optional)
    distance_mi: Optional[float] = None  # Total workout distance (optional)

    @staticmethod
    def create(
        type: str,
        date: date,
        name: str,
        sets: Optional[List[WorkoutSet]] = None,
        exercises: Optional[List[Exercise]] = None,
        duration_minutes: Optional[int] = None,
        distance_mi: Optional[float] = None,
    ) -> 'Workout':
        return Workout(
            id=str(uuid.uuid4()),
            type=type,
            date=date,
            name=name,
            sets=sets,
            exercises=exercises,
            duration_minutes=duration_minutes,
            distance_mi=distance_mi,
        )


# ------------------ Template ------------------

@dataclass
class Template:
    id: str
    name: str
    type: str
    exercises: Optional[List[Exercise]] = None  # Use the updated Exercise class

    @staticmethod
    def create(
        name: str,
        type: str,
        exercises: Optional[List[Exercise]] = None
    ) -> 'Template':
        return Template(
            id=str(uuid.uuid4()),
            name=name,
            type=type,
            exercises=exercises
        )
