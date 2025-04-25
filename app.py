from flask import Flask, jsonify, request
from database.symptoms import symptoms
from flask_cors import CORS

app = Flask(__name__)
CORS(app)



# Endpoint to get all symptoms
@app.route('/symptoms', methods=['GET'])
def get_symptoms(): 
    return jsonify(symptoms)

# # Endpoint to add a new symptom
# @app.route('/symptoms', methods=['POST'])
# def add_symptom():
#     new_symptom = request.json
#     symptoms.append(new_symptom)
#     return jsonify({"message": "Symptom added successfully"}), 201

@app.route('/list/<int:user_id>', methods=['POST'])
def set_list(user_id): 
    data = request.json
    symptoms_list = data.get('symptoms', [])
    date = data.get('date', None)  # Extract the date from the payload
    
    # Here you would typically save the symptoms list to a database
    # For this example, we'll just return it as a response
    print(f"User ID: {user_id}, Symptoms: {symptoms_list}, Date: {date}")
    return jsonify({"user_id": user_id, "symptoms": symptoms_list, "date": date}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)