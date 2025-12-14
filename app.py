from flask import Flask, render_template, request, jsonify, session, send_file
from flask_sqlalchemy import SQLAlchemy
import uuid
import os
from datetime import datetime
from difflib import SequenceMatcher

# ➡️ IMPORT YOUR NEW TTS MODULE
import TTS 

app = Flask(__name__)

app.secret_key = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat_history.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Setup Database
db = SQLAlchemy(app)

class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(36), nullable=False, unique=True)
    messages = db.Column(db.Text, nullable=False, default='[]')

class FAQEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    ask_count = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

@app.before_request
def ensure_student_id():
    if 'student_id' not in session:
        session['student_id'] = str(uuid.uuid4())

def similar(a, b):
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()

@app.route('/')
def home():
    return render_template('index.html', student_id=session['student_id'])

@app.route('/faq')
def faq_page():
    return render_template('faq.html')

@app.route('/get-faq')
def get_faq():
    faqs = FAQEntry.query.filter(FAQEntry.ask_count >= 3).order_by(FAQEntry.ask_count.desc()).limit(10).all()
    return jsonify({
        'faqs': [
            {'question': f.question, 'answer': f.answer, 'count': f.ask_count}
            for f in faqs
        ]
    })

@app.route('/speak', methods=['POST'])
def speak_text():
    """
    Endpoint for generating audio. Now delegates logic to TTS.py.
    """
    try:
        data = request.get_json()
        text = data.get('text', '').strip() if data else ''
    except Exception:
        return jsonify({'error': 'Invalid request format'}), 400

    if not text:
        return jsonify({'error': 'متن خالی است'}), 400

    try:
        # ➡️ CALL THE FUNCTION FROM TTS.py
        audio_path = TTS.generate_audio(text)
        
        # Send the file back to the browser
        return send_file(audio_path, mimetype="audio/wav")

    except ValueError as e:
        # Handle validation errors (empty text after cleaning)
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        # Handle server/inference errors
        print(f"Server Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat_route():
    user_message = request.json.get('message', '').strip()
    if not user_message:
        return jsonify({'response': 'لطفاً یک پیام وارد کنید.'})
    
    chat_history = session.get('chat_history', [])
    if not isinstance(chat_history, list):
        chat_history = []

    context = ""
    for msg in chat_history[-4:]:
        role = "User" if msg['sender'] == 'user' else "Assistant"
        context += f"{role}: {msg['text']}\n"
    
    full_prompt = (
        "You are a helpful assistant for Persian speakers. "
        "Keep answers short, clear, and useful. "
        "If the user asks about English grammar, explain with examples.\n\n"
        f"{context}User: {user_message}\nAssistant:"
    )
    
    try:
        # Assuming 'chat.py' exists
        from chat import get_response
        answer = get_response(full_prompt)
        
        # FAQ Logic
        existing_faqs = FAQEntry.query.all()
        found_similar = False
        for faq in existing_faqs:
            if similar(user_message, faq.question) > 0.85:
                faq.ask_count += 1
                db.session.commit()
                found_similar = True
                break
        
        if not found_similar:
            new_faq = FAQEntry(question=user_message, answer=answer)
            db.session.add(new_faq)
            db.session.commit()
        
        chat_history.append({'sender': 'user', 'text': user_message})
        chat_history.append({'sender': 'bot', 'text': answer})
        if len(chat_history) > 16:
            chat_history = chat_history[-16:]
        session['chat_history'] = chat_history
        
        return jsonify({'response': answer})
        
    except Exception as e:
        print(f"[Error] {e}")
        return jsonify({'response': 'متاسفانه مشکلی پیش آمد.'})

if __name__ == '__main__':
    print("✅ ربات با TTS فارسی فعال شد!")
    app.run(host='0.0.0.0', port=5000, debug=True)