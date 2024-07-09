from flask import Flask, request, jsonify
import os
import speech_recognition as sr
from gensim.summarization import summarize

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024  # 2 GB

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
    part_num = request.form['part']
    filename = request.form['filename']
    
    part_filename = f"{filename}.part{part_num}"
    file.save(part_filename)
    app.logger.info(f"Parte {part_num} do arquivo {filename} recebida.")

    return jsonify({"message": f"Parte {part_num} recebida com sucesso."}), 200

@app.route('/merge', methods=['POST'])
def merge_file():
    filename = request.form['filename']
    part_count = int(request.form['part_count'])
    full_filename = f"{filename}_full.wav"

    with open(full_filename, 'wb') as full_file:
        for part_num in range(1, part_count + 1):
            part_filename = f"{filename}.part{part_num}"
            with open(part_filename, 'rb') as part_file:
                full_file.write(part_file.read())
            os.remove(part_filename)
    
    transcribed_text = transcribe_audio(full_filename)
    summary = summarize(transcribed_text, ratio=0.3)
    
    return jsonify({
        "transcription": transcribed_text,
        "summary": summary
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
