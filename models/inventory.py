class Inventory:
    def __init__(self, user_id, name, category, location, qty, price):
        self.user_id = user_id
        self.name = name
        self.category = category
        self.location = location
        self.qty = qty
        self.price = price

    def save_to_db(self, inventory_collection):
        user_inv_data = {
            "user_id": self.user_id,
            "name": self.name,
            "category": self.category,
            "location": self.location,
            "qty": self.qty,
            "price": self.price
        }
        inventory_collection.insert_one(user_inv_data)

    @staticmethod
    def find_by_user(user_id, inventory_collection):
        return inventory_collection.find({"user_id": user_id})

