

from flask import Blueprint, request, jsonify
from models.user_model import User
from models.inventory import Inventory
from utils.config import users_collection
from utils.config import inventory_collection, inventory_history_collection
import logging
from bson import ObjectId

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


@auth_routes.route('/inventory/<item_id>', methods=['PUT'])
def update_inventory(item_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    modified = Inventory.update_item(item_id, data, inventory_collection)
    if modified:
        # Record the change
        Inventory.record_change(
            category=data.get("category"),
            change_type="updated",
            amount=0,
            user_id=data.get("user_id"),
            history_collection=inventory_history_collection
        )
        return jsonify({"message": "Inventory updated successfully"}), 200

    return jsonify({"error": "Item not found or no changes"}), 404

@auth_routes.route('/inventory/add/<user_id>', methods=['POST'])
def add_inventory(user_id):
    data = request.get_json() or {}
    try:
        new_item = Inventory(
            user_id=user_id,
            name=data["name"],
            category=data["category"],
            quantity=int(data["quantity"]),
            location=data["location"],
            price=float(data["price"])
        )
        inserted_id = new_item.save_to_db(inventory_collection)

        Inventory.record_change(
            category=new_item.category,
            change_type="added",
            amount=new_item.quantity,
            user_id=user_id,
            history_collection=inventory_history_collection
        )

        return jsonify({"message": "Item added successfully", "item_id": inserted_id}), 201
    except KeyError:
        return jsonify({"error": "Missing fields"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_routes.route('/inventory/update-quantity/<item_id>/<int:decrement>', methods=['PATCH'])
def update_quantity(item_id, decrement):
    modified = Inventory.updated_quantities(item_id, decrement, inventory_collection)
    if modified:
        # Fetch the item to get its category & user_id
        doc = inventory_collection.find_one({"_id": ObjectId(item_id)})
        Inventory.record_change(
            category=doc["category"],
            change_type="removed",
            amount=decrement,
            user_id=doc["user_id"],
            history_collection=inventory_history_collection
        )
        return jsonify({"message": "Quantity updated", "modified_count": modified}), 200

    return jsonify({"error": "Item not found"}), 404

@auth_routes.route('/inventory/delete/<item_id>', methods=['DELETE'])
def delete_inventory(item_id):
    deleted = Inventory.delete_item(item_id, inventory_collection)
    if deleted:
        return jsonify({"message": "Item deleted successfully", "deleted_count": deleted}), 200
    return jsonify({"error": "Item not found"}), 404