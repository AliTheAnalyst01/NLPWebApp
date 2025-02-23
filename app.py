from flask import Flask, render_template, request, redirect, jsonify
from api import NERProcessor
from utils.pdf_processor import read_pdf
from db import DataBase
import os
from dotenv import load_dotenv

# Initialize Flask application
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'development_key')

# Initialize components
dbo = DataBase()
ner_processor = NERProcessor()


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/perform_registration', methods=['POST'])
def perform_register():
    try:
        name = request.form.get('name_of_user')
        email = request.form.get('email_of_user')
        password = request.form.get('password_of_user')

        if not all([name, email, password]):
            return render_template('register.html', message='All fields are required')

        if dbo.insert(name, email, password):
            return render_template('login.html', message='Registration Successful. Please login')
        return render_template('register.html', message='Email already exists')

    except Exception as e:
        app.logger.error(f"Registration error: {str(e)}")
        return render_template('register.html', message='Registration failed')


@app.route('/perform_login', methods=['POST'])
def perform_login():
    try:
        email = request.form.get('email_of_user')
        password = request.form.get('password_of_user')
        if dbo.search(email, password):
            return redirect('/profile')
        return render_template('login.html', message='Incorrect credentials')

    except Exception as e:
        app.logger.error(f"Login error: {str(e)}")
        return render_template('login.html', message='Login failed')


@app.route('/profile')
def profile():
    return render_template('profile.html', ner_endpoint="/ner_interface")


@app.route("/ner_interface")
def ner_interface():
    return render_template('ner.html')


@app.route('/perform_ner', methods=['POST'])
def perform_ner():
    try:
        text = ""
        # File processing
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                if file.filename.endswith('.pdf'):
                    text = read_pdf(file)
                elif file.filename.endswith('.txt'):
                    text = file.read().decode('utf-8')

        # Text input fallback
        if not text:
            text = request.form.get('text', '').strip()

        if not text:
            return jsonify({"success": False, "error": "No input provided"}), 400

        result = ner_processor.process_text(text)
        return jsonify({"success": True, "result": result})

    except Exception as e:
        app.logger.error(f"NER error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('DEBUG', 'False').lower() in ['true', '1', 't']
    )