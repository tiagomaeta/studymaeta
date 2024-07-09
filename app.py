from flask import Flask, request, jsonify
import speech_recognition as sr
from gensim.summarization import summarize

app = Flask(__name__)

def transcribe_audio(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio, language="pt-BR")
        return text
    except sr.UnknownValueError:
        return "Não foi possível entender o áudio"
    except sr.RequestError:
        return "Erro ao conectar com o serviço de reconhecimento"

@app.route('/')
def index():
    return "Serviço de transcrição e sumarização de áudio está ativo!"

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    file = request.files['file']
    transcribed_text = transcribe_audio(file)
    if transcribed_text.startswith("Erro"):
        return jsonify({"error": transcribed_text}), 500

    summary = summarize(transcribed_text, ratio=0.3)

    return jsonify({
        "transcription": transcribed_text,
        "summary": summary
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
