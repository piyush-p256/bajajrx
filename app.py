from flask import Flask, render_template, request, jsonify
from main.retrieval_generation import generation
from main.data_ingestion import data_ingestion
import json

# Initialize data ingestion and generation chain
vstore = data_ingestion("done")
chain = generation(vstore)

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get", methods=["POST", "GET"])
def chat():
    if request.method == "POST":
        msg = request.form["msg"]
        input = msg
        
        result = chain.invoke(
            {"input": input},
            config={
                "configurable": {"session_id": "Dhananjay_VStest"}
            },
        )["answer"]
        
        return str(result)

# 1. Health Check Endpoint
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200

# 2. Assessment Recommendation Endpoint
@app.route("/recommend", methods=["POST", "GET"])
def recommend_assessments():
    try:
        query = None
        
        # Handle POST request
        if request.method == "POST":
            if request.is_json:
                data = request.get_json()
                if data and "query" in data:
                    query = data["query"]
                else:
                    return jsonify({"error": "Missing 'query' field in request body"}), 400
            else:
                return jsonify({"error": "Content-Type must be application/json"}), 400
        
        # Handle GET request
        elif request.method == "GET":
            query = request.args.get("query")
            if not query:
                return jsonify({"error": "Missing 'query' parameter"}), 400
        
        # Process the query
        result = chain.invoke(
            {"input": query},
            config={
                "configurable": {"session_id": "Dhananjay_VStest"}
            },
        )["answer"]
        
        # Parse the result into JSON
        # Since result is expected to be in JSON format based on your template
        if isinstance(result, dict):
            return jsonify(result), 200
        else:
            # If result is a string containing JSON, parse it
            try:
                parsed_result = json.loads(result)
                return jsonify(parsed_result), 200
            except json.JSONDecodeError:
                # If parsing fails, return as a text response
                return jsonify({"error": "Failed to parse result as JSON", "raw_result": result}), 500
        
    except Exception as e:
        app.logger.error(f"Error in recommend endpoint: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)