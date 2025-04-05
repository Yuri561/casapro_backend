from bson import ObjectId
from utils.config import inventory_collection
from datetime import datetime

class Inventory:
    def __init__(self,  user_id, name, category, location, quantity, price):
        self.user_id = user_id
        self.name = name
        self.category = category
        self.location = location
        self.quantity = quantity
        self.price = price

    def save_to_db(self, inventory_collection):
        user_inv_data = {
            "user_id": self.user_id,
            "name": self.name,
            "category": self.category,
            "location": self.location or "",
            "quantity": self.quantity,
            "price": self.price,
            "timestamp": datetime.now()
        }
        result = inventory_collection.insert_one(user_inv_data)
        return str(result.inserted_id)

    @staticmethod
    def record_change(category, change_type, amount, user_id, history_collection):
        history_collection.insert_one({
            "user_id": user_id,
            "category": category,
            "changeType": change_type,  # "added", "removed", "lowStock"
            "amount": amount,
            "timestamp": datetime.now()
        })


    @staticmethod
    def find_by_user(user_id, inventory_collection):
        return inventory_collection.find({"user_id": user_id})

    @staticmethod
    def update_item(item_id, updated_data, inventory_collection):
        result = inventory_collection.update_one(
            {"_id": ObjectId(item_id)},
            {"$set": updated_data}
        )
        return result.modified_count

    @staticmethod
    def insert_item(user_id, new_item, inventory_collection):
        document = {"user_id": user_id, **new_item}
        result = inventory_collection.insert_one(document)
        return str(result.inserted_id)

    @staticmethod
    def updated_quantities(item_id, decrement, inventory_collection):
        result = inventory_collection.update_one(
            {"_id": ObjectId(item_id)},
            {"$inc": {"quantity": -decrement}}
        )
        return result.modified_count

    @staticmethod
    def delete_item(item_id, inventory_collection):
        result = inventory_collection.delete(
            {"_id": ObjectId(item_id)}
        )
        return result.modified_count