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

def upload_part(file_path, part_num, url, filename):
    files = {'file': open(file_path, 'rb')}
    data = {'part': part_num, 'filename': filename}
    response = requests.post(url, files=files, data=data)
    return response

def merge_parts(filename, total_parts, merge_url):
    merge_data = {'filename': filename, 'part_count': total_parts}
    response = requests.post(merge_url, data=merge_data)
    return response

def main():
    file_path = "seu_arquivo_grande.wav"
    url = 'https://studymaeta-production.up.railway.app/upload'
    merge_url = 'https://studymaeta-production.up.railway.app/merge'
    divide_arquivo(file_path)

    file_name = os.path.basename(file_path)
    parts = [f"{file_name}.part{i}" for i in range(1, len(os.listdir()) + 1)]

    for part in parts:
        part_num = part.split('.')[-1].replace('part', '')
        response = upload_part(part, part_num, url, file_name)
        print(response.json())

    response = merge_parts(file_name, len(parts), merge_url)
    print(response.json())

if __name__ == "__main__":
    main()
