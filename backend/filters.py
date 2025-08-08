# backend/filters.py

from typing import List, Optional
from datetime import date
from backend.models import Workout, Template


def filter_workouts_by_date_range(
    workouts: List[Workout], 
    start_date: Optional[date] = None, 
    end_date: Optional[date] = None
) -> List[Workout]:
    """
    Filters workouts to include only those within the optional start_date and end_date range (inclusive).
    """
    if start_date is None and end_date is None:
        return workouts

    filtered = []
    for workout in workouts:
        if start_date and workout.date < start_date:
            continue
        if end_date and workout.date > end_date:
            continue
        filtered.append(workout)
    return filtered


def filter_workouts_by_type(workouts: List[Workout], workout_type: Optional[str] = None) -> List[Workout]:
    """
    Filters workouts by checking if any exercises inside the workout matches the type.
    If no type is specified, returns all workouts.
    """
    if not workout_type:
        return workouts

    filtered_workouts = []
    for w in workouts:
        if w.exercises:
            for ex in w.exercises:
                if ex.type == workout_type:
                    filtered_workouts.append(w)
                    break # No need to check other exercises if one matches
        else:
            #If no exercises, fall back to workout's own type
            if w.type == workout_type:
                filtered_workouts.append(w)
    return filtered_workouts

def search_templates_by_name(
    templates: List[Template], 
    keyword: Optional[str] = None
) -> List[Template]:
    """
    Returns templates whose names contain the keyword (case-insensitive).
    If no keyword provided, returns all templates.
    """
    if not keyword:
        return templates
    keyword_lower = keyword.lower()
    return [t for t in templates if keyword_lower in t.name.lower()]
