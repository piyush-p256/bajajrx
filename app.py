from flask import Flask, request, jsonify
import functools
import os
from dotenv import load_dotenv

load_dotenv()

from main.document_ingestion import ingest_document
from main.semantic_retrieval import embed_chunks, build_faiss_index, retrieve_relevant_chunks
from main.llm_answer import generate_llm_answers_together
from sentence_transformers import SentenceTransformer
app = Flask(__name__)

# Authorization Decorator
def require_bearer_token(view_func):
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        expected_token = '82f5af99c6ce321fdbd4196aabc8f25feef8593924eb979ec060644672dca027'
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid Authorization header'}), 401
        token = auth_header.split(' ', 1)[1]
        if token != expected_token:
            return jsonify({'error': 'Invalid token'}), 401
        return view_func(*args, **kwargs)
    return wrapper

# Optional Health Check Endpoint
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200

# Core HackRx Run Endpoint
@app.route('/hackrx/run', methods=['POST'])
@require_bearer_token
def hackrx_run():
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400

    data = request.get_json()
    documents = data.get('documents')
    questions = data.get('questions')

    if not documents or not questions or not isinstance(questions, list):
        return jsonify({'error': 'Invalid input: documents and questions are required'}), 400

    try:
        if isinstance(documents, str):
            chunks = ingest_document(documents)
        else:
            return jsonify({'error': 'Only a single document URL is supported for now.'}), 400

        if not chunks:
            return jsonify({'error': 'No text chunks extracted from document.'}), 500

        embeddings, texts, metadata = embed_chunks(chunks)
        index = build_faiss_index(embeddings)

        model = SentenceTransformer('all-MiniLM-L6-v2')
        top_k = 2
        relevant_chunks = retrieve_relevant_chunks(chunks, index, model, questions, top_k=top_k)

        llm_answers = generate_llm_answers_together(questions, relevant_chunks)

        return jsonify({
            'answers': llm_answers,
            'num_chunks': len(chunks)
        }), 200

    except Exception as e:
        return jsonify({'error': f'Document processing, retrieval, or LLM answer failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
