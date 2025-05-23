

from flask import Blueprint, request, jsonify, make_response


from models.budget import Budget
from models.user_model import User
from models.inventory import Inventory
from utils.auth import token_required
from utils.config import users_collection, budget_collection
from utils.config import inventory_collection
from utils.config import inventory_history_collection
from utils.config import  TOKEN_KEY
import logging
from bson import ObjectId

# Create Blueprint for auth routes
auth_routes = Blueprint("auth_routes", __name__)

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

        user_data = User.find_by_username(username, users_collection)

        if user_data and User.verify_password(user_data["password"], password):
            token = User.encode_auth_token(user_data["username"])
            if not token:
                return jsonify({"error": "Token generation failed"}), 500

            response = jsonify({
                "message": "Login successful",
                "token": token,
                "user": {
                    "username": user_data["username"],
                    "user_id": str(user_data["username"])
                }
            })
            response.set_cookie(
                "access_token",
                token,
                max_age=3600,
                httponly=True,
                samesite="None",
                secure=True
            )
            return response
        else:
            return jsonify({"error": "Invalid credentials"}), 401

    except Exception as e:
        logging.error(f"Error in login route: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@auth_routes.route("/logout", methods=["POST"])
@token_required
def logout(current_user_id):
    try:
        resp = make_response({"message": "Successfully logged out"})
        resp.delete_cookie("access_token")
        return resp, 200
    except Exception as e:
        logging.error(f"Logout error: {e}")
        return jsonify({"error": "Logout failed"}), 500


@auth_routes.route("/verify", methods=["GET"])
@token_required
def verify(current_user_id):
    try:
        user = users_collection.find_one({"user_id": current_user_id})
        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({
            "message": "Token valid",
            "user_id": str(user["user_id"]),
            "username": user["username"]
        }), 200

    except Exception as e:
        logging.error(f"error fetching data {e}")
        return jsonify({"error": "Internal server error"}), 500

#inventory history route
@auth_routes.route('/inventory/history', methods=['GET'])
@token_required
def get_inventory_history(current_user_id):
    try:
        history = list(inventory_history_collection.find({"user_id": str(current_user_id)}))
        for entry in history:
            entry["_id"] = str(entry["_id"])
            entry["timestamp"] = entry["timestamp"].isoformat()
        return jsonify({"history": history}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# show inventory
@auth_routes.route("/inventory", methods=["POST"])
@token_required
def inventory(current_user_id):
    try:
        print("Fetching inventory for user:", current_user_id)
        user_inventory = list(inventory_collection.find({"user_id": str(current_user_id)}))
        print(f"Found {len(user_inventory)} items")
        for item in user_inventory:
            item["_id"] = str(item["_id"])
        return jsonify({
            "message": "Inventory successfully loaded",
            "user_inventory": user_inventory
        }), 200
    except Exception as e:
        logging.error(f"Error in inventory route: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# update an item

@auth_routes.route('/inventory/<item_id>', methods=['PUT'])
@token_required
def update_inventory(item_id, current_user_id):
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
            user_id=current_user_id,
            history_collection=inventory_history_collection
        )
        return jsonify({"message": "Inventory updated successfully"}), 200

    return jsonify({"error": "Item not found or no changes"}), 404

#add inventory
@auth_routes.route('/inventory/add', methods=['POST'])
@token_required
def add_inventory(current_user_id):
    data = request.get_json() or {}
    try:
        new_item = Inventory(
            user_id=str(current_user_id),
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
            user_id=current_user_id,
            history_collection=inventory_history_collection
        )

        return jsonify({"message": "Item added successfully", "item_id": str(inserted_id)}), 201
    except KeyError:
        return jsonify({"error": "Missing fields"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#update one
@auth_routes.route('/inventory/update-quantity/<item_id>/<int:decrement>', methods=['PATCH'])
@token_required
def update_quantity(current_user_id, item_id, decrement):
    doc = inventory_collection.find_one({"_id": ObjectId(item_id)})
    if not doc or doc["user_id"] != current_user_id:
        return jsonify({"error": "Unauthorized or item not found"}), 403
    modified = Inventory.updated_quantities(item_id, decrement, inventory_collection)
    if modified:
        # Fetch the item to get its category & user_id
        doc = inventory_collection.find_one({"_id": ObjectId(item_id)})
        Inventory.record_change(
            category=doc["category"],
            change_type="removed",
            amount=decrement,
            user_id=current_user_id,
            history_collection=inventory_history_collection
        )
        return jsonify({"message": "Quantity updated", "modified_count": modified}), 200

    return jsonify({"error": "Item not found"}), 404

#delete inventory
@auth_routes.route('/inventory/delete/<item_id>', methods=['DELETE'])
@token_required
def delete_inventory(current_user_id, item_id):
    doc = inventory_collection.find_one({"_id": ObjectId(item_id)})
    if not doc or doc["user_id"] !=current_user_id:
        return jsonify({"error": "Unauthorized or item not found"}), 403
    deleted = Inventory.delete_item(item_id, inventory_collection)
    if deleted:
        return jsonify({"message": "Item deleted successfully", "deleted_count": deleted}), 200
    return jsonify({"error": "Item not found"}), 404

@auth_routes.route('/budget-goal/add', methods=["POST"])
@token_required
def add_budget(current_user_id):
    data = request.get_json()
    try:
        budget_instance = Budget(
            user_id=current_user_id,
            limit=data["limit"],
            category=data["category"]
        )

        result = budget_instance.add_budget(data, budget_collection)

        if "error" in result: #checking for duplicate since model returns dict with error key
            return jsonify(result), 409
        return jsonify({"message": "Budget goal successfully created", **result}), 201

    except KeyError:
        return jsonify({"error": "Missing required budget data"}), 400
    except Exception as err:
        return jsonify({"error": f"Cannot add budget goal: {str(err)}"}), 500


@auth_routes.route('/budget-goal', methods=["GET"])
@token_required
def get_budget(current_user_id):
    try:
        user_budget = list(budget_collection.find({"user_id": str(current_user_id)}))
        for doc in user_budget:
            doc["_id"] = str(doc["_id"])
        if user_budget:
            return jsonify(user_budget), 200
        else:
            return jsonify({"error_message": "no budget found for this user"}), 400
    except Exception as e:
        logging.error(f"Error in inventory route: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500




@auth_routes.route('/remove-goal/', methods=["DELETE"])
@token_required
def remove_budget(current_user_id):
    try:
        data = request.get_json()
        category = data.get("category")
        if not category:
            return jsonify({"error": "Category is required"}), 400
        result = budget_collection.delete_one({
            "user_id": current_user_id,
            "category": category
        })
        if result.deleted_count == 0:
            return jsonify({"error_message": "No matching goal found"}), 404
        return jsonify({"message": "Budget goal removed successfully"}), 200
    except Exception as e:
        logging.error(f"Error removing budget goal: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
