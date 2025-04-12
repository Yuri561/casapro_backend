#budget model
from datetime import datetime
from bson import ObjectId

class Budget:
    def __init__(self, user_id, limit, category ):
        self.user_id = user_id
        self.limit = limit
        self.category = category
        self.createdat = datetime.now()
        self.updatedat = datetime.now()

    def save_to_db(self, budget_collection):
        budget_data = {
            "user_id": self.user_id,
            "category": self.category.lower(),
            "limit": float(self.limit),
            "createdAt": self.createdat,
            "updatedAt": self.updatedat,
            "timestamp": datetime.now()
        }

        result = budget_collection.insert_one(budget_data)
        return str(result.inserted_id)

    def add_budget(self, budget_goal, budget_collection):
        existing_goal = budget_collection.find_one({
            "user_id": self.user_id,
            "category": budget_goal["category"]
        })
        if existing_goal:
            return {"error": "Budget goal for this category already exists."}

        budget_doc = {
            "user_id": self.user_id,
            **budget_goal,
            "timestamp": datetime.now()
        }
        result = budget_collection.insert_one(budget_doc)
        return {"inserted_id": str(result.inserted_id)}
    @staticmethod
    def remove_budget(inserted_id, budget_collection):
        result = budget_collection.delete_one({"_id": ObjectId(inserted_id)})
        return result
