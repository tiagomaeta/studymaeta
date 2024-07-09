from flask import Flask, request, jsonify
import speech_recognition as sr
from gensim.summarization import summarize

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB

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
    app.logger.info("Recebendo requisição no endpoint /upload")

    if 'file' not in request.files:
        app.logger.error("Nenhum arquivo enviado no campo 'file'")
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    file = request.files['file']
    app.logger.info(f"Arquivo recebido: {file.filename}")

    try:
        transcribed_text = transcribe_audio(file)
        summary = summarize(transcribed_text, ratio=0.3)

        app.logger.info("Transcrição e sumarização bem-sucedidas")
        return jsonify({
            "transcription": transcribed_text,
            "summary": summary
        })
    except Exception as e:
        app.logger.error(f"Erro durante a transcrição: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
