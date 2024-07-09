import os
import requests

def divide_arquivo(file_path, tamanho_parte=50 * 1024 * 1024):  # 50 MB
    file_name = os.path.basename(file_path)
    parte = 1
    with open(file_path, 'rb') as f:
        while True:
            dados = f.read(tamanho_parte)
            if not dados:
                break
            with open(f"{file_name}.part{parte}", 'wb') as parte_file:
                parte_file.write(dados)
            parte += 1

def upload_part_s3(file_path, part_num, s3_client, bucket_name, filename):
    part_filename = f"{filename}.part{part_num}"
    s3_client.upload_file(file_path, bucket_name, part_filename)
    return f"Parte {part_num} enviada com sucesso."

def main():
    import boto3

    s3 = boto3.client('s3',
                      aws_access_key_id='SUA_CHAVE_DE_ACESSO',
                      aws_secret_access_key='SUA_CHAVE_SECRETA',
                      region_name='SUA_REGIAO')

    file_path = "seu_arquivo_grande.wav"
    divide_arquivo(file_path)

    file_name = os.path.basename(file_path)
    parts = [f"{file_name}.part{i}" for i in range(1, len(os.listdir()) + 1)]

    for part in parts:
        part_num = part.split('.')[-1].replace('part', '')
        message = upload_part_s3(part, part_num, s3, 'SEU_BUCKET', file_name)
        print(message)

if __name__ == "__main__":
    main()
