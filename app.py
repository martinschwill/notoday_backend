from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import os
import secrets
from flask_mail import Mail, Message
import database.db_handler as db_handler # Import the db_handler module

app = Flask(__name__)
CORS(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # or your SMTP server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'martin@schwill.art'
app.config['MAIL_PASSWORD'] = 'kccu ivjx zopo husj'  # Use environment variable for security
mail = Mail(app)


# base_url = '10.2.40.94:5001'
base_url = '34.27.80.19'

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

### EMOTIONS ###

# Endpoint to get all emotions 
@app.route('/emo', methods=['GET'])
def get_emotions(): 
    emotions = db_handler.get_all_emotions()
    return jsonify(emotions)

# Endpoint to add a new emotion
@app.route('/emo', methods=['POST'])
def add_emotion():
    new_emotion = request.json
    db_handler.add_emotion(new_emotion)
    return jsonify({"message": "Emotion added successfully"}), 201




### USERS ###

# Endpoint to create a new user
@app.route('/users/create', methods=['POST'])
def create_user():
    user_data = request.json
    response = db_handler.create_user(user_data)
    if "error" in response:
        return jsonify(response), 400
    return jsonify(response), 201


##### USER CREATION ##### 
# Endpoint to get a user by name or email 
@app.route('/users/register', methods=['POST'])
def check_user():
    user_data = request.json
    user_name = user_data.get("user_name")
    user_email = user_data.get("user_email")
    user_password = user_data.get("user_password")
    
    # Check if the user exists by name or email
    if user_name and user_email:
        response = db_handler.get_user_by_name(user_name)
        if "error" in response:
            response = db_handler.get_user_by_email(user_email)
    elif user_name:
        response = db_handler.get_user_by_name(user_name)
    elif user_email:
        response = db_handler.get_user_by_email(user_email)
    else:
        return jsonify({"error": "User name or email is required"}), 400
    print(response) 
    if 'error' in response and response['error'] == "User not found":
        send_confirmation_email(4, user_name, user_password, user_email)
        return jsonify({"message": "Confirmation email sent."}), 200
    return jsonify(response), 401


@app.route('/confirm/<int:user_id>/<token>', methods=['GET'])
def confirm_email(user_id, token):
    response = db_handler.get_user_temp(user_id, token)
    if "error" in response:
        return jsonify(response), 404
    return Response("<h2>Account creation confirmed</h2>", mimetype='text/html')


# Endpoint to get a user by user_id
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = db_handler.get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user)

# Endpoint to add a slipup date for a user
@app.route('/users/slipup', methods=['POST'])
def add_slipup():
    slipup_data = request.json
    slipup_date = slipup_data.get("slipup_date")
    user_id = slipup_data.get("user_id")
    
    # Call the db_handler method to add the slipup date
    response = db_handler.add_user_slipup(user_id, slipup_date)
    
    # Check for errors in the response
    if "error" in response:
        return jsonify(response), 404
    return jsonify(response), 200

# Endpoint to get all slipups for a user
@app.route('/users/slipups/<int:user_id>', methods=['GET'])
def get_slipups(user_id):
    # Call the db_handler method to get the slipups
    response = db_handler.get_user_slipups(user_id)
    # Check for errors in the response
    if "error" in response:
        return jsonify(response), 404
    print(f"SLIPUPS: {response['slipups']}")
    return list(response['slipups']), 200

# Endpoint for logging in a user #
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

# Endpoint to add a new user_id-date record with symptoms
@app.route('/days', methods=['PUT'])
def add_symptoms():
    data = request.json
    user_id = data.get("user_id")
    date = data.get("date")
    symptoms = data.get("symptoms", [])
    
    response = db_handler.add_user_symptoms(user_id, date, symptoms)
    if "error" in response:
        return jsonify(response), 400
    return jsonify(response), 201

# Endpoint to check if a user_id-date combination exists
@app.route('/days/check', methods=['POST'])
def check_user_date():
    data = request.json
    user_id = data.get("user_id")
    date = data.get("date")
    print(f'{user_id}, {date}')
    exists = db_handler.check_user_date_exists(user_id, date)
    return jsonify({"exists": exists}), 200


@app.route('/days_symptoms/check', methods=['POST'])
def check_user_symptoms():
    data = request.json
    user_id = data.get("user_id")
    date = data.get("date")
    exists = db_handler.check_user_symptoms_exists(user_id, date)
    return jsonify({"exists": exists}), 200


# Endpoint to update symptoms for an existing user_id-date record
@app.route('/days', methods=['PUT'])
def update_symptoms():
    data = request.json
    user_id = data.get("user_id")
    date = data.get("date")
    symptoms = data.get("symptoms", [])
    
    response = db_handler.update_user_symptoms(user_id, date, symptoms)
    if "error" in response:
        return jsonify(response), 404
    return jsonify(response), 200


# Endpoint to retrieve symptoms for x days in the past
@app.route('/days/past', methods=['POST'])
def get_past_symptoms():
    data = request.json
    user_id = data.get("user_id", None)
    days = data.get("days", None) 
    
    response = db_handler.get_symptoms_for_past_days(user_id, days)
    if "error" in response:
        return jsonify(response), 404
    return jsonify(response), 200


# Endpoint to add user-specific emotions
@app.route('/days_emo', methods=['POST'])
def add_emotions():
    data = request.json
    user_id = data.get('user_id', None)
    emotions_list = data.get('emotions', [])
    date = data.get('date', None)

    response = db_handler.add_user_emotions(user_id, date, emotions_list)
    if "error" in response:
        return jsonify(response), 400
    return jsonify(response), 201

# Endpoint to update user-specific emotions
@app.route('/days_emo', methods=['PUT'])
def update_emotions():
    data = request.json
    user_id = data.get('user_id', None)
    emotions_list = data.get('emotions', [])
    date = data.get('date', None)

    response = db_handler.add_user_emotions(user_id, date, emotions_list)
    print(response)
    if "error" in response:
        return jsonify(response), 400
    return jsonify(response), 201

# Endpoint to retrieve emotions for x days in the past
@app.route('/days_emo/past', methods=['GET'])
def get_past_emotions():
    user_id = request.args.get("user_id", type=int)
    days = request.args.get("days", type=int)
    
    response = db_handler.get_emotions_for_past_days(user_id, days)
    if "error" in response:
        return jsonify(response), 404
    return jsonify(response), 200

# Endpoint to check if a user_id-date combination exists for emotions
@app.route('/days_emo/check', methods=['POST'])
def check_user_date_emo():
    data = request.json
    user_id = data.get("user_id")
    date = data.get("date")
    exists = db_handler.check_user_emotions_exists(user_id, date)
    return jsonify({"exists": exists}), 200


#### ENDPOINTS FOR UNIFIED EMOTIONS AND SYMPTOMS #### 

@app.route('/entries', methods=['POST'])
def add_symptoms_and_emotions(): 
    data = request.json
    user_id = data.get("user_id")
    date = data.get("date")
    symptoms = data.get("symptoms", [])
    emotions = data.get("emotions", [])

    # Add symptoms
    response_symptoms = db_handler.add_user_symptoms(user_id, date, symptoms)
    if "error" in response_symptoms:
        return jsonify(response_symptoms), 400

    # Add emotions
    response_emotions = db_handler.add_user_emotions(user_id, date, emotions)
    if "error" in response_emotions:
        return jsonify(response_emotions), 400

    return jsonify({"message": "Symptoms and emotions added successfully"}), 201


@app.route('/entries', methods=['GET'])
def get_entries_for_user_date(): 
    user_id = request.args.get("user_id", type=int)
    date = request.args.get("date", type=str)

    # Retrieve symptoms and emotions 
    result = db_handler.get_symptoms_for_past_days(user_id, 0)
    if "error" in result:
        return jsonify(result), 404

    symptoms_emotions = {'symptoms': [], 'emotions': []} 
    symptoms_emotions['symptoms'] = result[0]['symptoms']
    symptoms_emotions['emotions'] = result[0]['emotions']
    return jsonify(symptoms_emotions), 200


## METHODS ## 

def send_confirmation_email(user_id, user_name, user_password, user_email):
        token = generate_confirm_token()
        # Save the token in your DB associated with the user for later verification
        db_handler.add_user_temp(user_id, user_name, user_email, user_password, user_token=token)
        confirm_url = f"http://{base_url}/confirm/{user_id}/{token}"
        msg = Message(
            subject="Confirm your email",
            sender=app.config['MAIL_USERNAME'],
            recipients=[user_email],
            html=f'<p>Please confirm your email by clicking <a href="{confirm_url}">here</a>.</p>'
        )
        # print(f"Sending email to: {user_email}, \nToken: {token}\nCredentials: {app.config['MAIL_USERNAME']}, {app.config['MAIL_PASSWORD']}")  
        mail.send(msg)
        return {"message": "Confirmation email sent."}

def generate_confirm_token(): 
    return secrets.token_urlsafe(32) 





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)