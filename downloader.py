# downloader.py
import os
import requests
from urllib.parse import urlparse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Função para baixar a imagem
def download_image(image_url, filename):
    try:
        response = requests.get(image_url)
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"[INFO] Imagem salva: {filename}")
    except Exception as e:
        print(f"[ERRO] Falha ao baixar a imagem: {e}")

# Função para salvar as imagens, títulos e descrições
def save_product_data(title, description, image_url):
    # Criar uma pasta para salvar as imagens e os dados
    base_dir = "image_data"
    safe_title = title.replace(" ", "_").replace("/", "_").replace("\\", "_")
    product_dir = os.path.join(base_dir, safe_title)

    if not os.path.exists(product_dir):
        os.makedirs(product_dir)

    # Salvar a imagem
    image_filename = os.path.join(product_dir, f"{safe_title}.jpg")
    download_image(image_url, image_filename)

    # Salvar o título e descrição em um arquivo de texto
    description_filename = os.path.join(product_dir, "description.txt")
    with open(description_filename, "w", encoding="utf-8") as f:
        f.write(f"Título: {title}\n")
        f.write(f"Descrição: {description}\n")
    print(f"[INFO] Dados do produto salvos: {product_dir}")
