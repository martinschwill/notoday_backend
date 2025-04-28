from pymongo import MongoClient
from datetime import datetime

# MongoDB connection setup
client = MongoClient("mongodb://localhost:27017/")
db = client["notoday_db"]
symptoms_collection = db["symptoms"]
users_collection = db["users"]

# Symptoms operations
def get_all_symptoms():
    return list(symptoms_collection.find({}, {"_id": 0}))  # Exclude MongoDB's _id field

def add_symptom(new_symptom):
    symptoms_collection.insert_one(new_symptom)

# Users operations
def create_user(user_data):
    if users_collection.find_one({"user_name": user_data["user_name"]}):
        return {"error": "User Name already exists"}
    users_collection.insert_one(user_data)
    return {"message": "User created successfully"}

def get_user_by_id(user_id):
    return users_collection.find_one({"user_id": user_id}, {"_id": 0})  # Exclude MongoDB's _id field

def update_user_last_date_sober(user_id, last_date_sober):
    result = users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"last_date_sober": last_date_sober}}
    )
    if result.matched_count == 0:
        return {"error": "User not found"}
    return {"message": "User updated successfully"}

def login_user(user_name, user_password):
    # Find the user by user_name
    user = users_collection.find_one({"user_name": user_name})
    if not user:
        return {"error": "User not found"}
    
    # Check if the password matches
    if user["user_password"] != user_password:
        return {"error": "Invalid password"}
    
    # Return success response
    return {"message": "Login successful", "user_id": user["user_id"]}

def get_user_days_since_sober(user_id):
    user = users_collection.find_one({"user_id": user_id}) 
    if not user or "last_date_sober" not in user:
        return {"error": "User not found or last_date_sober not set"}
    
    # Parse last_date_sober if it's a string
    last_date_sober = user["last_date_sober"]
    if isinstance(last_date_sober, str):
        last_date_sober = datetime.fromisoformat(last_date_sober)  # Convert ISO 8601 string to datetime
    
    # Calculate the difference in days
    days_since_sober = (datetime.now() - last_date_sober).days
    return days_since_sober
