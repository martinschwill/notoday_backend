from pymongo import MongoClient
from datetime import datetime, timedelta
import os 

# MongoDB connection setup
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(mongo_uri)
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

def add_user_slipup(user_id, slipup_date):
    result = users_collection.update_one(
        {"user_id": user_id},
        {"$push": {"slipups": slipup_date}}
    )
    if result.matched_count == 0:
        return {"error": "User not found"}
    return {"message": "Slipup date updated successfully"}

def get_user_slipups(user_id):
    user = users_collection.find_one({"user_id": user_id})
    if not user:
        return {"error": "User not found"}
    slipups = user['slipups'] if 'slipups' in user else []
    return {"slipups": slipups}

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


### days operations ###

# Method to check if a user_id-date combination exists
def check_user_date_exists(user_id, date):
    record = db["user_symptoms"].find_one({"user_id": user_id, "date": date})
    return record is not None

# Method to add a new user_id-date record with symptoms
def add_user_symptoms(user_id, date, symptoms):
    if check_user_date_exists(user_id, date):
        return {"error": "Record for this user and date already exists"}
    
    db["user_symptoms"].insert_one({
        "user_id": user_id,
        "date": date,
        "symptoms": symptoms
    })
    return {"message": "Symptoms added successfully"}

# Method to update symptoms for an existing user_id-date record
def update_user_symptoms(user_id, date, symptoms):
    result = db["user_symptoms"].update_one(
        {"user_id": user_id, "date": date},
        {"$set": {"symptoms": symptoms}}
    )
    if result.matched_count == 0:
        return {"error": "Record not found for this user and date"}
    return {"message": "Symptoms updated successfully"}

# Method to retrieve symptoms for x days in the past
def get_symptoms_for_past_days(user_id, days):
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    records = list(db["user_symptoms"].find(
        {"user_id": user_id, "date": {"$gte": start_date}},
        {"_id": 0}
    ))
    if not records:
        return {"error": "No records found for the given user and date range"}
    return records

### Emotions operations ###
def get_all_emotions():
    return list(db["emotions"].find({}, {"_id": 0}))  # Exclude MongoDB's _id field

def add_emotion(new_emotion):
    db["emotions"].insert_one(new_emotion)

def add_user_emotions(user_id, date, emotions):
    if check_user_date_exists(user_id, date):
        return {"error": "Emotions for this user and date already exists"}
    
    db["user_emotions"].insert_one({
        "user_id": user_id,
        "date": date,
        "emotions": emotions
    })
    return {"message": "Emotions added successfully"}

def update_user_emotions(user_id, date, emotions):
    result = db["user_symptoms"].update_one(
        {"user_id": user_id, "date": date},
        {"$set": {"emotions": emotions}}
    )
    if result.matched_count == 0:
        return {"error": "Record not found for this user and date"}
    return {"message": "Emotions updated successfully"}

def get_emotions_for_past_days(user_id, days):
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    records = list(db["user_emotions"].find(
        {"user_id": user_id, "date": {"$gte": start_date}},
        {"_id": 0}
    ))
    if not records:
        return {"error": "No records found for the given user and date range"}
    return records

def check_user_emotions_exists(user_id, date):
    record = db["user_symptoms"].find_one({"user_id": user_id, "date": date})
    print(f'RECORD: {record}')
    return record is not None