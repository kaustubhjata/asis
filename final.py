import os
import uuid
from flask import Flask, request, render_template, jsonify
import pdfplumber
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from groq import Groq

# Load environment variables
load_dotenv()

# Initialize Flask App
app = Flask(__name__)

# Get Configurations from environment variables
groq_api_key = os.environ.get("GROQ_API_KEY")
groq_model = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

# Check Groq API Key
if not groq_api_key:
    print("WARNING: GROQ_API_KEY is not set in environment variables. Groq will fail.")
    groq_client = None
else:
    groq_client = Groq(api_key=groq_api_key)
    print(f"Model Selection: Using Groq API with model: {groq_model}")

# Function to extract text from PDF
def extract_pdf_text(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ''.join(page.extract_text() or '' for page in pdf.pages)
        return text.strip()
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None

# Templates for prompts
pdf_summary_template = """
Your task is to carefully read and thoroughly understand the attached PDF document. Then, craft a summary that is formal, accurate, and well-structured. Ensure that your response is clear, concise, and professional, providing a comprehensive overview of the content while maintaining precision.

Include the following elements in your response:

1. Title and Context
2. Key Sections
3. Important Definitions and Concepts
4. Key Insights
5. Contextual Relevance
6. Length and Detail

Use the following content:
{pdf_text}
"""

podcast_summary_template = """
You are a friendly and engaging podcast creator team. Your task is to read and understand the attached PDF document, capturing its content and intent in a clear and approachable way.

Using the PDF content, create a lively and engaging podcast episode. The goal is to make listeners feel like they are having a friendly chat with you over coffee. Use natural pauses, casual phrases, and a conversational tone throughout.

Make the script a two-person conversation between Host 1 and Host 2. Do not include any other hosts.
Format the conversation strictly as:
Host 1: [Host 1's dialogue]
Host 2: [Host 2's dialogue]

Example format:
Host 1: Welcome to our podcast! Today we are discussing this fascinating paper on AI.
Host 2: That's right! And what's interesting is how it approaches security...

Ensure the output only contains the conversation lines in this format. Do not add intro/outro metadata or markdown headers.

Use the following content:
{pdf_text}
"""

# Routes for Flask
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/voice_to_text', methods=['GET', 'POST'])
def voice_to_text():
    if request.method == 'POST':
        # Accept transcription sent by client-side browser speech recognition
        transcription = request.form.get('transcription') or (request.json.get('transcription') if request.json else None)
        
        if not transcription:
            return jsonify({"error": "No transcription text provided"}), 400
        
        print(f"Received transcription from client: {transcription}")
        prompt = f"Respond to the following transcription:\n\n{transcription}"
        
        response_text = ""
        if groq_client:
            try:
                completion = groq_client.chat.completions.create(
                    model=groq_model,
                    messages=[{"role": "user", "content": prompt}]
                )
                response_text = completion.choices[0].message.content
            except Exception as e:
                response_text = f"Groq Error: {e}"
        else:
            response_text = "Groq API is not configured. Please set GROQ_API_KEY in your environment."
        
        return jsonify({
            "transcription": transcription,
            "response": response_text
        })
    
    return render_template('speak.html')

@app.route('/pdf_summary', methods=['GET', 'POST'])
def pdf_summary():
    if request.method == 'POST':
        pdf_file = request.files.get('pdf_file')
        if pdf_file:
            upload_dir = "uploads"
            os.makedirs(upload_dir, exist_ok=True)
            
            # Secure and generate unique filename with UUID to prevent caching / collision issues
            filename = secure_filename(pdf_file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(upload_dir, unique_filename)
            
            try:
                pdf_file.save(file_path)
                pdf_text = extract_pdf_text(file_path)
            finally:
                # Delete uploaded file immediately after text extraction to clean up disk
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            if pdf_text:
                prompt = pdf_summary_template.format(pdf_text=pdf_text)
                summary_text = ""
                if groq_client:
                    try:
                        completion = groq_client.chat.completions.create(
                            model=groq_model,
                            messages=[{"role": "user", "content": prompt}]
                        )
                        summary_text = completion.choices[0].message.content
                    except Exception as e:
                        summary_text = f"Groq Error: {e}"
                else:
                    summary_text = "Groq API is not configured."
                
                return jsonify({"summary": summary_text})
            else:
                return jsonify({"error": "Failed to extract text from PDF"}), 400
            
    return render_template('pdf_summary.html')

@app.route('/podcast_summary', methods=['GET', 'POST'])
def podcast_generator():
    if request.method == 'POST':
        pdf_file = request.files.get('pdf_file')
        if pdf_file:
            upload_dir = "uploads"
            os.makedirs(upload_dir, exist_ok=True)
            
            # Secure and generate unique filename with UUID to prevent caching / collision issues
            filename = secure_filename(pdf_file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(upload_dir, unique_filename)
            
            try:
                pdf_file.save(file_path)
                pdf_text = extract_pdf_text(file_path)
            finally:
                # Delete uploaded file immediately after text extraction to clean up disk
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            if pdf_text:
                prompt = podcast_summary_template.format(pdf_text=pdf_text)
                podcast_content_text = ""
                if groq_client:
                    try:
                        completion = groq_client.chat.completions.create(
                            model=groq_model,
                            messages=[{"role": "user", "content": prompt}]
                        )
                        podcast_content_text = completion.choices[0].message.content
                    except Exception as e:
                        podcast_content_text = f"Groq Error: {e}"
                else:
                    podcast_content_text = "Groq API is not configured."
                
                print(f"Generated podcast text of length {len(podcast_content_text)}")
                return jsonify({"podcast_content": podcast_content_text})
            else:
                return jsonify({"error": "Failed to extract text from PDF"}), 400
            
    return render_template('podcast_summary.html')

# Keep legacy routes with dummy status to prevent frontend breakages
@app.route('/read_aloud', methods=['POST'])
def read_aloud_content():
    return jsonify({"status": "Voice output is now handled client-side in the web browser."})

@app.route('/stop_speech', methods=['POST'])
@app.route('/stop_speaking', methods=['POST'])
def stop_speaking_route():
    return jsonify({"status": "Voice output is now handled client-side in the web browser."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)