from flask import Flask, render_template, request, jsonify
from main.retrieval_generation import generation
from main.data_ingestion import data_ingestion
import json

# Initialize data ingestion and generation chain
vstore = data_ingestion("done")
chain = generation(vstore)

app = Flask(__name__)

# Mapping for test type codes to full descriptions
TEST_TYPE_MAPPING = {
    "A": "Ability & Aptitude",
    "B": "Biodata & Situational Judgement",
    "C": "Competencies", 
    "D": "Development & 360",
    "E": "Assessment Exercises",
    "K": "Knowledge & Skills",
    "P": "Personality & Behavior",
    "S": "Simulations"
}

# Function to convert test type codes to full descriptions
def convert_test_types(result):
    if "recommended_assessments" in result:
        for assessment in result["recommended_assessments"]:
            if "test_type" in assessment and isinstance(assessment["test_type"], list):
                expanded_types = []
                for type_code in assessment["test_type"]:
                    # Handle case where multiple codes are in one string (e.g., "BCP")
                    if len(type_code) > 1 and all(c in TEST_TYPE_MAPPING for c in type_code):
                        # Split the string into individual characters and convert each
                        for code in type_code:
                            expanded_types.append(TEST_TYPE_MAPPING[code])
                    elif type_code in TEST_TYPE_MAPPING:
                        expanded_types.append(TEST_TYPE_MAPPING[type_code])
                    else:
                        expanded_types.append(type_code)  # Keep as is if unknown
                assessment["test_type"] = expanded_types
    return result

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
        
      
        elif request.method == "GET":
            query = request.args.get("query")
            if not query:
                return jsonify({"error": "Missing 'query' parameter"}), 400
        
       
        result = chain.invoke(
            {"input": query},
            config={
                "configurable": {"session_id": "Dhananjay_VStest"}
            },
        )["answer"]
        
        
        if isinstance(result, dict):
            processed_result = convert_test_types(result)
            return jsonify(processed_result), 200
        else:
           
            try:
                parsed_result = json.loads(result)
                processed_result = convert_test_types(parsed_result)
                return jsonify(processed_result), 200
            except json.JSONDecodeError:
                # If parsing fails, return as a text response
                return jsonify({"error": "Failed to parse result as JSON", "raw_result": result}), 500
        
    except Exception as e:
        app.logger.error(f"Error in recommend endpoint: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)