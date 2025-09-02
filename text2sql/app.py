from flask import Flask, request, jsonify
from flask_cors import CORS
import json, os
from dotenv import load_dotenv
from vertexai.preview.generative_models import GenerativeModel, GenerationConfig
import vertexai
load_dotenv()
app = Flask(__name__)
CORS(app)
SCHEMA = {} 
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
LOCATION = "us-central1"
MODEL_ID = "gemini-2.0-flash-lite"
vertexai.init(project=PROJECT_ID, location=LOCATION)
model = GenerativeModel(MODEL_ID)

def filter_schema(question, schema):
    relevant = {}
    question = question.lower()
    for table, columns in schema.items():
        if table.lower() in question:
            relevant[table] = columns
        else:
            for col in columns:
                if col.lower() in question:
                    relevant[table] = columns
                    break
    return relevant

def schema_to_text(schema):
    return "\n".join([f"Table: {table}({', '.join(columns)})" for table, columns in schema.items()])

def create_prompt(question, schema_text):
    return f"""
You are a helpful assistant that generates SQL queries.
Only use the schema provided below. Do not assume any data.

Schema:
{schema_text}

Question: {question}

SQL Query:
"""

def get_sql_from_gemini(prompt):
    config = GenerationConfig(temperature=0.0)
    response = model.generate_content(prompt, generation_config=config)
    return response.text.strip()

@app.route("/upload-schema", methods=["POST"])
def upload_schema():
    global SCHEMA
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    try:
        SCHEMA = json.loads(file.read().decode('utf-8'))
        return jsonify({'message': 'Schema uploaded successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/generate-sql", methods=["POST"])
def generate_sql():
    data = request.get_json()
    question = data.get("question", "")
    if not question:
        return jsonify({"error": "No question provided"}), 400
    if not SCHEMA:
        return jsonify({"error": "No schema uploaded yet"}), 400

    filtered = filter_schema(question, SCHEMA)
    if not filtered:
        return jsonify({"error": "No matching tables found"}), 400

    schema_text = schema_to_text(filtered)
    prompt = create_prompt(question, schema_text)
    try:
        sql = get_sql_from_gemini(prompt)
        return jsonify({"sql": sql})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

