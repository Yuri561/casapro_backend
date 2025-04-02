from bson import ObjectId
from utils.config import inventory_collection

class Inventory:
    def __init__(self, user_id, name, category, location, quantity, price):
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
            "location": self.location,
            "quantity": self.quantity,
            "price": self.price
        }
        inventory_collection.insert_one(user_inv_data)

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
    def delete_item(item_id, inventory_collection):
        result = inventory_collection.delete_one({"_id": ObjectId(item_id)})
        return result.deleted_count