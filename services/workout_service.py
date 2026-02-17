import os
from azure.cosmos import CosmosClient

class WorkoutService:
    def __init__(self):
        # Fetch credentials from environment variables
        url = os.environ.get('COSMOS_URI')
        key = os.environ.get('COSMOS_KEY')
        db_name = os.environ.get('COSMOS_DATABASE', 'WorkoutDB')
        container_name = os.environ.get('COSMOS_CONTAINER', 'Exercises')

        # Initialize the Cosmos Client
        self.client = CosmosClient(url, credential=key)
        self.database = self.client.get_database_client(db_name)
        self.container = self.database.get_container_client(container_name)

    def generate_plan(self, selected_types, selected_sports, selected_muscle_targets):
        """
        Queries Cosmos DB using SQL-like syntax to filter exercises.
        """
        # Base query
        query_text = "SELECT * FROM c WHERE 1=1"
        parameters = []

        # Logic to handle array filtering in Cosmos DB (ARRAY_CONTAINS)
        if selected_types:
            # Check if any of the user's selected types exist in the exercise's 'types' array
            type_clauses = []
            for i, t in enumerate(selected_types):
                type_clauses.append(f"ARRAY_CONTAINS(c.types, @type{i})")
                parameters.append({"name": f"@type{i}", "value": t})
            query_text += " AND (" + " OR ".join(type_clauses) + ")"

        if selected_sports:
            sport_clauses = []
            for i, s in enumerate(selected_sports):
                sport_clauses.append(f"ARRAY_CONTAINS(c.sports, @sport{i})")
                parameters.append({"name": f"@sport{i}", "value": s})
            query_text += " AND (" + " OR ".join(sport_clauses) + ")"

        if selected_muscle_targets:
            muscle_clauses = []
            for i, m in enumerate(selected_muscle_targets):
                muscle_clauses.append(f"ARRAY_CONTAINS(c.muscle_targets, @muscle{i})")
                parameters.append({"name": f"@muscle{i}", "value": m})
            query_text += " AND (" + " OR ".join(muscle_clauses) + ")"

        # Execute the query
        items = list(self.container.query_items(
            query=query_text,
            parameters=parameters,
            enable_cross_partition_query=True
        ))

        if not items:
            return None, "No exercises found matching those criteria."

        return items, None