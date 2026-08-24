# 🎙️ Persian-English AI Language Learning Chatbot

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/Flask-2.x-black?style=for-the-badge&logo=flask&logoColor=white" alt="Flask" />
  <img src="https://img.shields.io/badge/LangChain-Ollama-orange?style=for-the-badge&logo=langchain&logoColor=white" alt="LangChain" />
  <img src="https://img.shields.io/badge/LLM-Llama_3.1_(8B)-blueviolet?style=for-the-badge&logo=meta&logoColor=white" alt="Llama 3.1" />
  <img src="https://img.shields.io/badge/TTS-Tacotron2_%2B_HiFi--GAN-red?style=for-the-badge" alt="Tacotron2" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT License" />
</p>

---

## 📖 Overview

**AI-chatbot** is an intelligent, bilingual language learning assistant designed specifically for Persian speakers learning English. It provides an immersive conversational experience through **natural language understanding**, **Speech-to-Text (STT)** voice input, and **hybrid bilingual Text-to-Speech (TTS)** voice synthesis that seamlessly combines Persian and English in a single voice response.

The system also includes an **automated FAQ engine** that detects recurring user questions using fuzzy matching and automatically curates a dynamic Frequently Asked Questions dashboard.

---

## ✨ Key Features

- 🧠 **Local LLM Intelligence (Ollama + Llama 3.1 8B)**:
  - Powered by `langchain-ollama` using local Llama 3.1 8B.
  - Tailored system prompt to explain English grammar, vocabulary, and sentence structure in clear Persian with practical examples.
  - Contextual conversation memory (retains recent conversation turns).

- 🗣️ **Hybrid Bilingual Text-to-Speech (TTS)**:
  - **Intelligent Segmentation**: Automatically detects English and Persian segments in the same response using regular expressions and `langdetect`.
  - **Persian Voice Synthesis**: Synthesizes natural-sounding Persian speech via **Tacotron2 (Multi-Speaker)** and **HiFi-GAN vocoder** using reference speaker audio.
  - **English Voice Synthesis**: Generates clear, speed-controlled English pronunciation via `pyttsx3`.
  - **Seamless Audio Merging**: Combines mixed-language audio chunks into a unified `.wav` stream using `pydub`.

- 🎙️ **Speech-to-Text (STT) Voice Input**:
  - Direct microphone voice input via Web Speech API (`SpeechRecognition` / `webkitSpeechRecognition`) configured for `fa-IR`.
  - Real-time speech transcription with pulsing visual recording status.

- 📊 **Dynamic FAQ Intelligence & Auto-Clustering**:
  - Automatically identifies frequently asked questions using string similarity (`difflib.SequenceMatcher` with $>85\%$ threshold).
  - Automatically aggregates ask counts into SQLite database.
  - Generates a real-time `/faq` dashboard for questions asked 3 or more times.

- 💻 **Modern, Responsive RTL User Interface**:
  - Floating expandable chat widget with sleek gradient accents.
  - Natural word-by-word streaming typing effect with adaptive delays.
  - Audio playback button on every bot message with interactive loading animations.
  - Session-based user tracking and local storage history caching.

---

## 🏗️ Architecture & Data Flow

```
                      ┌───────────────────────────────────────────────┐
                      │              User Browser (UI)                │
                      │  - Text Input / Web Speech STT (fa-IR)        │
                      │  - Word-by-Word Typing Animation              │
                      │  - Audio Player for TTS Speech Output         │
                      └──────────────────────┬────────────────────────┘
                                             │
                                     HTTP Requests
                                             │
                                             ▼
                      ┌───────────────────────────────────────────────┐
                      │                 Flask App                     │
                      │                 (app.py)                      │
                      │  - Session & Student ID Tracking (UUID)       │
                      │  - SQLite Database (ChatHistory & FAQEntry)   │
                      └──────┬──────────────────────┬─────────────────┘
                             │                      │
                   /chat     │                      │   /speak
                             ▼                      ▼
        ┌───────────────────────────────┐  ┌──────────────────────────────────┐
        │       LLM Engine (chat.py)    │  │       Bilingual TTS (TTS.py)     │
        │  - LangChain Ollama Client    │  │  1. Segment Text (fa vs en)      │
        │  - Model: llama3.1:8b         │  │  2. Persian -> Tacotron2 +       │
        │  - Persian Tutor Prompting    │  │                HiFi-GAN          │
        │  - SequenceMatcher FAQ Logger │  │  3. English -> pyttsx3           │
        └───────────────────────────────┘  │  4. Pydub Audio Stitching (.wav) │
                                           └──────────────────────────────────┘
```

---

## 📁 Repository Structure

```plaintext
AI-chatbot/
├── .github/
│   └── workflows/
│       └── python-app.yml       # GitHub Actions CI workflow (linting & testing)
├── static/
│   ├── app.js                   # Chatbox logic, Web Speech STT, TTS player, animations
│   └── style.css                # RTL modern styling, gradients, and animations
├── templates/
│   ├── index.html               # Main chat interface with floating widget
│   └── faq.html                 # Dynamic frequently asked questions page
├── app.py                       # Main Flask web server, database models, and routes
├── chat.py                      # LangChain Ollama LLM integration (Llama 3.1)
├── TTS.py                       # Hybrid Persian/English speech synthesis engine
├── requirements.txt             # Python dependencies
├── .gitignore                   # Ignored files and directories
├── LICENSE                      # MIT License
└── README.md                    # Project documentation
```

---

## ⚙️ Prerequisites & System Requirements

Before running the project, ensure you have the following installed on your machine:

1. **Python 3.10+**
2. **[Ollama](https://ollama.com/)** installed and running.
3. **[FFmpeg](https://ffmpeg.org/)** installed and added to your system `PATH` (required by `pydub` to process audio files).
4. **Persian TTS Model & HiFi-GAN Vocoder**:
   - The Persian TTS relies on [Persian-MultiSpeaker-Tacotron2](https://github.com/Adibian/Persian-MultiSpeaker-Tacotron2) or [ManaTTS-Persian-Tacotron2-Model](https://github.com/MahtaFetrat/ManaTTS-Persian-Tacotron2-Model).
   - A reference speaker audio `.wav` file for the multi-speaker embedding.

---

## 🚀 Installation & Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/amirrezaabbasiai-svg/AI-chatbot.git
cd AI-chatbot
```

### 2. Create and Activate a Virtual Environment

**On Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Python Dependencies

Create or use the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

*(If installing manually: `pip install flask flask-sqlalchemy langchain-ollama langchain-core pydub pyttsx3 langdetect emoji`)*

---

### 4. Set Up Ollama & Download LLM Model

Make sure Ollama is installed and running, then pull the `llama3.1:8b` model:

```bash
ollama pull llama3.1:8b
```

Verify that Ollama is accessible locally on default port `http://localhost:11434`.

---

### 5. Configure Persian Tacotron2 Model

In `TTS.py`, adjust the file system paths to match your local installation of the Persian Tacotron2 repository and reference audio:

```python
# TTS.py
TTS_DIR = r"path/to/Persian-MultiSpeaker-Tacotron2"
REF_WAV = r"path/to/sample.wav"
```

> **Note**: Ensure the directory contains `inference.py` and the `HiFiGAN` vocoder model weights configured.

---

### 6. Run the Application

Start the Flask development server:

```bash
python app.py
```

Once started, open your browser and navigate to:
- **Chat Interface**: [http://localhost:5000](http://localhost:5000)
- **FAQ Dashboard**: [http://localhost:5000/faq](http://localhost:5000/faq)

---

## 🔌 API Reference

| Endpoint | Method | Description | Request Body / Parameters | Response |
|---|---|---|---|---|
| `/` | `GET` | Renders the primary chat interface | None | HTML page |
| `/chat` | `POST` | Processes user text query via LLM and updates FAQ counts | `{"message": "string"}` | `{"response": "string"}` |
| `/speak` | `POST` | Converts bilingual text to speech and generates WAV audio | `{"text": "string"}` | Binary Audio (`audio/wav`) |
| `/faq` | `GET` | Renders the Frequently Asked Questions page | None | HTML page |
| `/get-faq` | `GET` | Fetches JSON array of top FAQs with $\ge 3$ ask counts | None | `{"faqs": [...]}` |

---

## 🧩 How It Works

### 1. Bilingual Text-to-Speech Workflow (`TTS.py`)
```
Input: "سلام! Today we are learning present perfect tense. آماده‌ای؟"
  │
  ├─► Segment 1 (fa): "سلام!" ──────────────────► Tacotron2 + HiFi-GAN ─► AudioChunk 1
  ├─► Segment 2 (en): "Today we are learning..." ─► pyttsx3 (Rate 100) ──► AudioChunk 2
  └─► Segment 3 (fa): "آماده‌ای؟" ───────────────► Tacotron2 + HiFi-GAN ─► AudioChunk 3
  │
  └─► Pydub Concatenation ──────────────────────► Export final_xxx.wav ─► Stream to client
```

### 2. Smart FAQ Aggregation Algorithm
When a user sends a message:
1. The app queries all existing questions in the database.
2. Uses Python's `SequenceMatcher` to calculate the string similarity ratio:
   $$\text{Ratio}(Q_{\text{user}}, Q_{\text{existing}}) > 0.85$$
3. If a similar question exists, its `ask_count` increments by 1.
4. If no match is found, a new `FAQEntry` is created.
5. The `/get-faq` endpoint filters and displays entries where `ask_count >= 3`.

---

## 🛠️ Configuration & Customization

| Parameter | File | Default Value | Description |
|---|---|---|---|
| `app.secret_key` | `app.py` | `'your-secret-key-change-in-production'` | Secret key for Flask sessions |
| `SQLALCHEMY_DATABASE_URI` | `app.py` | `'sqlite:///chat_history.db'` | Database connection string |
| `model` | `chat.py` | `"llama3.1:8b"` | Ollama model identifier |
| `temperature` | `chat.py` | `0.3` | LLM generation creativity / determinism |
| `TTS_DIR` | `TTS.py` | Path string | Location of Persian Tacotron2 codebase |
| `REF_WAV` | `TTS.py` | Path string | Reference speaker WAV for multi-speaker synthesis |
| Speech Rate | `TTS.py` | `100` | Words per minute rate for `pyttsx3` English speech |

---

## ❓ Troubleshooting & FAQs

<details>
<summary><b>1. Error initializing <code>pyttsx3</code> or no sound on Linux?</b></summary>
On Linux, install `espeak` and `ffmpeg`:
```bash
sudo apt-get update && sudo apt-get install -y espeak ffmpeg libespeak1
```
</details>

<details>
<summary><b>2. SpeechRecognition microphone not working in browser?</b></summary>
- Web Speech API requires HTTPS or `localhost` / `127.0.0.1`.
- Ensure microphone permissions are allowed in your browser settings.
- Google Chrome and Chromium-based browsers provide the best native support for Persian (`fa-IR`) speech recognition.
</details>

<details>
<summary><b>3. Ollama connection error (`Connection refused`)?</b></summary>
Ensure the Ollama service is running on your machine:
```bash
ollama serve
```
And verify `ollama list` shows `llama3.1:8b`.
</details>

<details>
<summary><b>4. Persian TTS inference fails?</b></summary>
- Verify that `TTS_DIR` and `REF_WAV` paths in `TTS.py` exist and point to valid directories on your machine.
- Verify that PyTorch and CUDA (if using GPU) are installed in the environment where `inference.py` runs.
</details>

---

## 🗺️ Roadmap

- [ ] Docker and Docker-Compose support for one-click setup.
- [ ] Migrate Persian TTS to FastSpeech2 / VITS for real-time low-latency inference.
- [ ] Multi-turn conversation persistence across multiple devices with user authentication.
- [ ] Interactive grammar quiz generator and voice pronunciation scoring.

---

## 📄 License

This project is open-source and licensed under the [MIT License](LICENSE).

---

## 🤝 Contributing & Acknowledgments

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/amirrezaabbasiai-svg/AI-chatbot/issues).

- **Ollama & LangChain**: For local LLM orchestration.
- **[Persian-MultiSpeaker-Tacotron2](https://github.com/Adibian/Persian-MultiSpeaker-Tacotron2)** & **[ManaTTS Dataset](https://github.com/MahtaFetrat/ManaTTS-Persian-Tacotron2-Model)** for Persian speech synthesis resources.
