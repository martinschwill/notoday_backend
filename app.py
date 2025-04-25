from flask import Flask, jsonify, request
from database.symptoms import symptoms

app = Flask(__name__)



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

if __name__ == '__main__':
    app.run(debug=True)