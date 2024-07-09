from flask import Flask, request, jsonify
import os
import boto3
import speech_recognition as sr
from gensim.summarization import summarize

app = Flask(__name__)

# Configurar boto3
s3 = boto3.client('s3',
                  aws_access_key_id='SUA_CHAVE_DE_ACESSO',
                  aws_secret_access_key='SUA_CHAVE_SECRETA',
                  region_name='SUA_REGIAO')

BUCKET_NAME = 'SEU_BUCKET'

app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024  # 2 GB

def transcribe_audio(audio_file_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file_path) as source:
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
    filename = file.filename

    # Salvar arquivo localmente
    file.save(filename)

    # Fazer upload do arquivo para o S3
    s3.upload_file(filename, BUCKET_NAME, filename)

    # Remover o arquivo localmente
    os.remove(filename)

    return jsonify({"message": f"Arquivo {filename} enviado com sucesso."}), 200

@app.route('/process', methods=['POST'])
def process_file():
    filename = request.form['filename']

    # Baixar o arquivo do S3
    s3.download_file(BUCKET_NAME, filename, filename)

    # Transcrever e sumarizar o arquivo
    transcribed_text = transcribe_audio(filename)
    summary = summarize(transcribed_text, ratio=0.3)

    # Remover o arquivo localmente
    os.remove(filename)

    return jsonify({
        "transcription": transcribed_text,
        "summary": summary
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
