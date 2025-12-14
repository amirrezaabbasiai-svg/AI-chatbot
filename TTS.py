import os
import subprocess
import uuid
import re
import emoji
from pydub import AudioSegment
import pyttsx3
from langdetect import detect, LangDetectException


# --------------------------------------------
# CONFIG
# --------------------------------------------
TTS_DIR = r"F:\TTS2\Persian-MultiSpeaker-Tacotron2"
REF_WAV = r"F:\TTS2\Persian-Tacotron2-on-ManaTTS\sample.wav"

VALID_CHARS_PATTERN = re.compile(r'[^\u0600-\u06FFa-zA-Z0-9.,?! ]')
PERSIAN_CHARS = re.compile(r'[\u0600-\u06FF]')
ENGLISH_CHARS = re.compile(r'[A-Za-z]')

ENGLISH_TEMP_PATH = os.path.join(os.path.dirname(__file__), "temp_en.wav")


# --------------------------------------------
# LANGUAGE DETECTION
# --------------------------------------------
def detect_lang(word: str):
    """Strict English/Persian detection."""
    if ENGLISH_CHARS.search(word):
        return "en"
    if PERSIAN_CHARS.search(word):
        return "fa"

    try:
        d = detect(word)
        return "en" if d == "en" else "fa"
    except LangDetectException:
        return "fa"


def segment_text(text: str):
    words = text.strip().split()
    if not words:
        return []

    segments = []
    current_lang = detect_lang(words[0])
    current_chunk = words[0]

    for w in words[1:]:
        lang = detect_lang(w)
        if lang == current_lang:
            current_chunk += " " + w
        else:
            segments.append((current_lang, current_chunk))
            current_lang = lang
            current_chunk = w

    segments.append((current_lang, current_chunk))
    return segments


# --------------------------------------------
# ENGLISH TTS (pyttsx3)
# --------------------------------------------
def init_pyttsx3():
    """Initialize pyttsx3 with slower English speed."""
    try:
        engine = pyttsx3.init()
        zira_voice_found = False
        # Select English voice
        for v in engine.getProperty("voices"):
            if "english" in v.name.lower():
                engine.setProperty("voice", v.id)
                zira_voice_found = True
                break
        if not zira_voice_found:
            print("warning: zira voice not found, using default English voice")
        # Set slower speed (default ~200)
        engine.setProperty("rate", 100)   # <<< ADJUSTED SPEED
        return engine
    except Exception as e:
        print("pyttsx3 init error:", e)
        return None


def generate_english_audio(text: str):
    """Generate English audio using system TTS."""
    engine = init_pyttsx3()
    if engine is None:
        raise RuntimeError("pyttsx3 failed to initialize")

    # Remove emojis and unsupported characters
    cleaned = emoji.replace_emoji(text, replace="")

    # Delete old temp file
    if os.path.exists(ENGLISH_TEMP_PATH):
        os.remove(ENGLISH_TEMP_PATH)

    engine.save_to_file(cleaned, ENGLISH_TEMP_PATH)
    engine.runAndWait()

    # Force cleanup if stuck
    if hasattr(engine, "_inLoop") and engine._inLoop:
        engine.endLoop()

    if not os.path.exists(ENGLISH_TEMP_PATH):
        raise RuntimeError("English audio generation failed")

    return ENGLISH_TEMP_PATH


# --------------------------------------------
# PERSIAN TTS (Tacotron2)
# --------------------------------------------
def generate_persian_audio(text: str):
    cleaned = emoji.replace_emoji(text, replace="")
    cleaned = VALID_CHARS_PATTERN.sub(" ", cleaned).strip()

    if not cleaned:
        raise RuntimeError("No Persian text after cleaning")

    uid = uuid.uuid4().hex
    out_name = f"tts_output_{uid}"

    cmd = [
        "python", "inference.py",
        "--vocoder", "HiFiGAN",
        "--text", cleaned,
        "--ref_wav_path", REF_WAV,
        "--test_name", out_name
    ]

    try:
        subprocess.run(
            cmd,
            cwd=TTS_DIR,
            check=True,
            text=True,
            capture_output=True
        )
    except subprocess.CalledProcessError:
        raise RuntimeError("Persian TTS error during inference")

    result_path = os.path.join(TTS_DIR, "results", out_name + ".wav")

    if not os.path.exists(result_path):
        raise RuntimeError("Missing Persian wav file: " + result_path)

    return result_path


# --------------------------------------------
# MAIN AUDIO GENERATOR
# --------------------------------------------
def generate_audio(text: str):
    segments = segment_text(text)
    if not segments:
        raise RuntimeError("Empty text")

    final_audio = AudioSegment.empty()

    # Output final file
    output_path = os.path.join(TTS_DIR, "results", f"final_{uuid.uuid4().hex}.wav")

    for lang, chunk in segments:
        try:
            if lang == "en":
                wav = generate_english_audio(chunk)
            else:
                wav = generate_persian_audio(chunk)

            audio = AudioSegment.from_wav(wav)
            final_audio += audio

        except Exception as e:
            print(f"Segment error ({chunk}):", e)
            continue

    # Export mixed audio
    final_audio.export(output_path, format="wav")

    # Cleanup temp English wav
    if os.path.exists(ENGLISH_TEMP_PATH):
        os.remove(ENGLISH_TEMP_PATH)

    return output_path
