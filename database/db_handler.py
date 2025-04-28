from pymongo import MongoClient

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
    if users_collection.find_one({"user_id": user_data["user_id"]}):
        return {"error": "User ID already exists"}
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