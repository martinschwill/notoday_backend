from flask import Flask, jsonify, request
from flask_cors import CORS
import database.db_handler as db_handler # Import the db_handler module

app = Flask(__name__)
CORS(app)

### SYMPTOMS ###

# Endpoint to get all symptoms
@app.route('/symptoms', methods=['GET'])
def get_symptoms(): 
    symptoms = db_handler.get_all_symptoms()
    return jsonify(symptoms)

# Endpoint to add a new symptom
@app.route('/symptoms', methods=['POST'])
def add_symptom():
    new_symptom = request.json
    db_handler.add_symptom(new_symptom)
    return jsonify({"message": "Symptom added successfully"}), 201

# Endpoint to add user-specific symptoms
@app.route('/list/<int:user_id>', methods=['POST'])
def set_list(user_id): 
    data = request.json
    symptoms_list = data.get('symptoms', [])
    date = data.get('date', None)  # Extract the date from the payload
    # Here you would typically save the symptoms list to a database
    return jsonify({"user_id": user_id, "symptoms": symptoms_list, "date": date}), 200

### USERS ###

# Endpoint to create a new user
@app.route('/users', methods=['POST'])
def create_user():
    user_data = request.json
    response = db_handler.create_user(user_data)
    if "error" in response:
        return jsonify(response), 400
    return jsonify(response), 201

# Endpoint to get a user by user_id
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = db_handler.get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user)

@app.route('/login', methods=['POST'])
def login():
    login_data = request.json
    user_name = login_data.get("user_name")
    user_password = login_data.get("user_password")
    
    # Call the db_handler method to validate the user
    response = db_handler.login_user(user_name, user_password)
    
    # Check for errors in the response
    if "error" in response:
        return jsonify(response), 401  # Unauthorized
    
    return jsonify(response), 200  # OK


# Endpoint to get the number of days since a user was last sober
@app.route('/users/<int:user_id>/days_since_sober', methods=['GET'])
def get_days_since_sober(user_id):
    response = db_handler.get_user_days_since_sober(user_id)
    if isinstance(response, int): 
        return jsonify({"days_since_sober": response}), 200
    else:     
        return jsonify(response), 404
    

# Endpoint to update a user's last_date_sober
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user_data = request.json
    last_date_sober = user_data.get('last_date_sober')
    response = db_handler.update_user_last_date_sober(user_id, last_date_sober)
    if "error" in response:
        return jsonify(response), 404
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)