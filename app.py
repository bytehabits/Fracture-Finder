from flask import Flask, render_template, request, jsonify, redirect, Response
from flask_cors import CORS
from functools import wraps
import openai
import base64
import os
import uuid
from werkzeug.utils import secure_filename
import logging
logging.basicConfig(level=logging.DEBUG)

UPLOAD_FOLDER = '/ff/www/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

openai.api_key = 'KEY'

app = Flask(__name__)
CORS(app)  
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


USERNAME = 'Username'
PASSWORD = 'Password'

def basic_auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.authorization
        if not auth or not (auth.username == USERNAME and auth.password == PASSWORD):
            return Response(
                'Could not verify your access level for that URL.\n'
                'You have to login with proper credentials.', 401,
                {'WWW-Authenticate': 'Basic realm="Login Required"'}
            )
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
@basic_auth_required
def index():
    return redirect("/index.html", code=302)

@app.route("/index.html") 
@basic_auth_required
def hello(): 
    return render_template('index.html') 

@app.route('/analyze', methods=['POST'])
def analyze():
    if request.method == 'OPTIONS':
        response = jsonify(success=True)
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        file.save(filepath)

        try:
            with open(filepath, "rb") as image_file:
                response = openai.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Is there a bone in the image? If not, simply state This is not a bone. If so, is it intact or broken? Please confirm with a confidence level on a percentage scale. Provide a detailed explanation."},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64.b64encode(image_file.read()).decode()}"}}
                            ]
                        }
                    ],
                    max_tokens=300
                )

                result = response.choices[0].message.content
                return jsonify({"result": result})

        except Exception as e:
            return jsonify({"error": str(e)}), 500

        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

    return jsonify({"error": "Invalid file format"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
