from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow requests from WordPress

@app.route("/api/message", methods=["POST"])
def message():
    data = request.get_json()
    name = data.get("name", "")
    email = data.get("email", "")
    message = data.get("message", "")
    
    # You can add email sending, DB saving, etc.
    return jsonify({"success": True, "message": f"Received message from {name}"})

if __name__ == "__main__":
    app.run()
