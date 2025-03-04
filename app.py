from flask import Flask, request, jsonify
from flask_cors import CORS
from rag_system import answer_legal_question
import logging
import os
import time

# Set up logging
logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Simple API key (replace with proper auth in production)
API_KEY = os.environ.get('LEGALUNA_API_KEY', 'default-api-key-for-development')

@app.route('/api/chat', methods=['POST'])
def chat():
    # Start timing for performance monitoring
    start_time = time.time()
    
    # Get request data
    data = request.json
    
    # Basic authentication
    provided_key = request.headers.get('X-API-Key')
    if provided_key != API_KEY:
        logging.warning(f"Unauthorized access attempt from {request.remote_addr}")
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get query from request
    query = data.get('query', '')
    if not query.strip():
        return jsonify({'error': 'Empty query'}), 400
    
    try:
        # Process query through RAG system
        response = answer_legal_question(query)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        logging.info(f"Query processed in {processing_time:.2f} seconds")
        
        return jsonify({
            'response': response,
            'processing_time': round(processing_time, 2)
        })
    except Exception as e:
        logging.error(f"Error processing query: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'An error occurred while processing your request',
            'details': str(e)
        }), 500

# Basic health check endpoint
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'Legaluna API'})

if __name__ == '__main__':
    # In development
    app.run(host='0.0.0.0', port=5000, debug=True)