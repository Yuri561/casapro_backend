

from flask import Blueprint, request, jsonify
from models.user_model import User
from models.inventory import Inventory
from utils.config import users_collection
from utils.config import inventory_collection
import logging


# Create Blueprint for auth routes
auth_routes = Blueprint("auth_routes", __name__)

#logging.basicConfig(filename="error.log", level=logging.ERROR)


@auth_routes.route("/register", methods=["POST"])
def register():
    try:
        data = request.json
        username = data.get("username")
        password = data.get("password")
        email = data.get("email")

        if not username or not password or not email:
            return jsonify({"error": "All fields are required"}), 400

        # Check if the user already exists
        if User.find_by_username(username, users_collection):
            return jsonify({"error": "Username already exists"}), 400

        # Create and save new user
        user = User(username, password, email)
        user.save_to_db(users_collection)


        response = jsonify({"message": "User registered successfully"})
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, PUT, DELETE"

        return response, 201

    except Exception as e:
        logging.error(f"Error in register route: {str(e)}")
        response = jsonify({"error": "Internal server error"})
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response, 500


@auth_routes.route("/login", methods=["POST"])
def login():
    try:
        data = request.json
        username = data.get("username")
        password = data.get("password")

        # Find user in database
        user_data = User.find_by_username(username, users_collection)

        # Verify user credentials
        if user_data and User.verify_password(user_data["password"], password):
            return jsonify({
                "message": "Login successful",
                "user": {
                    "username": user_data["username"],
                    "user_id": user_data["username"]
                    }
            }), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401

    except Exception as e:
        logging.error(f"Error in login route: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@auth_routes.route("/inventory", methods=["POST"])
def inventory():
    try:
        data = request.json
        user_id = data.get("user_id")
        user_inventory = list(inventory_collection.find({"user_id": user_id}))

        # ✅ Convert ObjectId to string
        for item in user_inventory:
            item["_id"] = str(item["_id"])

        if user_inventory:
            return jsonify({
                "message": "Inventory successfully loaded",
                "user_inventory": user_inventory
            }), 200
        else:
            return jsonify({"error": "No inventory found for this user"}), 404

    except Exception as e:
        logging.error(f"Error in inventory route: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@auth_routes.route('/inventory/<item_id>', methods=['PUT'])
def update_inventory(item_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    modified_count = Inventory.update_item(item_id, data, inventory_collection)
    if modified_count:
        return jsonify({"message": "Inventory updated successfully"}), 200
    else:
        return jsonify({"error": "Inventory item not found or no changes made"}), 404

@auth_routes.route('/inventory/add/<user_id>', methods=['POST'])
def add_inventory(user_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        new_item = Inventory(
            user_id=user_id,
            name=data.get("name"),
            category=data.get("category"),
            quantity= int(data.get("quantity")),
            location=data.get("location"),
            price=data.get("price")
        )
        insert_id = new_item.save_to_db(inventory_collection)
        return jsonify({"message": "Item added successfully", "item_id": insert_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_routes.route('/inventory/delete/<item_id>/<decrement>', methods=['PATCH'])
def update_quantity(item_id, decrement):
    try:
        modified_count = Inventory.updated_quantities(item_id, inventory_collection, int(decrement))
        if modified_count:
            return jsonify({"message": "Item updated successfully", "modified_count": modified_count}), 200
        else:
            return jsonify({"error": "Item not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_routes.route('/inventory/delete/<item_id>', methods=['Delete'])
def delete_inventory(item_id):
    try:
        modified_count = Inventory.delete_item(item_id, inventory_collection)
        if modified_count:
            return jsonify({"message": "Item updated successfully", "modified_count": modified_count}), 200
        else:
            return jsonify({"error": "Item not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

