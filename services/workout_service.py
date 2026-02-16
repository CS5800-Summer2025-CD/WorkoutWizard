from tinydb import TinyDB, Query
import random

class WorkoutService:
    def __init__(self, db_path, initial_data=None):
        self.db = TinyDB(db_path)
        self.Exercise = Query()
        
        if initial_data and len(self.db) == 0:
            print(f"--- LOG: Database empty. Seeding data to: {db_path} ---")
            self.db.insert_multiple(initial_data)
        else:
            # This is the part that was missing!
            print(f"--- LOG: Database at {db_path} already contains data. Skipping seeding. ---")

    def generate_plan(self, selected_types, selected_sports, selected_muscle_targets):
        """
        Filters exercises using OR logic within categories and AND logic between them.
        """
        all_conditions = []

        # Category 1: Types (OR logic)
        if selected_types:
            type_query = None
            for t in selected_types:
                if type_query is None:
                    type_query = self.Exercise.types.any(t)
                else:
                    type_query |= self.Exercise.types.any(t)
            all_conditions.append(type_query)

        # Category 2: Sports (OR logic)
        if selected_sports:
            sport_query = None
            for s in selected_sports:
                if sport_query is None:
                    sport_query = self.Exercise.sports.any(s)
                else:
                    sport_query |= self.Exercise.sports.any(s)
            all_conditions.append(sport_query)

        # Category 3: Muscle Targets (OR logic)
        if selected_muscle_targets:
            muscle_query = None
            for m in selected_muscle_targets:
                if muscle_query is None:
                    muscle_query = self.Exercise.muscle_targets.any(m)
                else:
                    muscle_query |= self.Exercise.muscle_targets.any(m)
            all_conditions.append(muscle_query)

        # Basic validation
        if not all_conditions:
            return [], "Please select at least one attribute to generate a workout."

        # Combine categories with AND logic
        final_query = all_conditions[0]
        for cond in all_conditions[1:]:
            final_query &= cond

        # Execute search
        matching_exercises = self.db.search(final_query)
        
        if matching_exercises:
            # Pick a random subset (Max 5) for the workout
            num_to_select = min(len(matching_exercises), 5)
            workout_plan = random.sample(matching_exercises, num_to_select)
            return workout_plan, None
        
        return [], "No exercises found matching your criteria. Try different selections!"