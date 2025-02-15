from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from assistant_demo import PostgreSQLAssistant

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/query", methods=["POST"])
def handle_query():
    data = request.json
    query = data.get("query", "")

    if not query:
        return jsonify({"error": "Query is required"}), 400

    assistant = PostgreSQLAssistant()
    try:
        results = assistant.hybrid_search(query)
        if results:
            response = assistant.generate_response(query, results)
            return jsonify({"response": response})
        else:
            return jsonify({"response": "No relevant documents found."})
    finally:
        assistant.close()

if __name__ == "__main__":
    app.run(debug=True)
