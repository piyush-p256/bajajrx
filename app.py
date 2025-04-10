from flask import Flask, render_template, request, jsonify
from main.retrieval_generation import generation
from main.data_ingestion import data_ingestion

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
        
        # Format the response
        # This is a placeholder - adjust based on what chain.invoke actually returns
        formatted_response = {
            "recommended_assessments": [
                {
                    "url": "https://example.com/assessment1",
                    "adaptive_support": "Yes",
                    "description": "Sample assessment based on query",
                    "duration": 60,
                    "remote_support": "Yes",
                    "test_type": ["Technical", "Coding"]
                }
                # Add more assessments based on your actual data
            ]
        }
        
        return jsonify(formatted_response), 200
        
    except Exception as e:
        app.logger.error(f"Error in recommend endpoint: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)