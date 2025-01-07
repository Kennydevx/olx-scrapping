from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from urllib.parse import urlparse
import os
import time

# Função para configurar o Selenium com o Chrome
def configure_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Modo headless (sem interface gráfica)
    chrome_options.add_argument("--disable-gpu")  # Desabilita o uso da GPU para desempenho
    chrome_options.add_argument("--no-sandbox")  # Desabilita o sandbox do Chrome

    # Alterar User-Agent para parecer com um navegador real
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    # Adicionar cabeçalhos HTTP adicionais (como Accept-Language e Accept-Encoding)
    chrome_options.add_argument("accept-language=pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7")
    chrome_options.add_argument("accept-encoding=gzip, deflate, br")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(30)  # Timeout global para carregamento de páginas
    return driver

# Função para realizar scraping com Selenium e coletar links dos produtos
def get_product_links_selenium(driver, search_term):
    base_url = f"https://www.olx.com.br/brasil?q={search_term}"
    print(f"[INFO] Acessando URL de busca: {base_url}")
    driver.get(base_url)  # Carregar a página

    try:
        # Esperar até que os anúncios sejam carregados
        WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "olx-ad-card__link-wrapper"))
        )
        print("[INFO] Procurando pelos links dos produtos...")

        # Buscar os elementos que contêm os links dos produtos
        product_elements = driver.find_elements(By.CLASS_NAME, "olx-ad-card__link-wrapper")

        # Extrair os links dos produtos encontrados
        product_links = [element.get_attribute("href") for element in product_elements if element.get_attribute("href")]
        print(f"[INFO] Total de links de produtos encontrados: {len(product_links)}")

        return product_links
    except Exception as e:
        print(f"[ERRO] Falha ao obter links: {e}")
        return []

# Função para esperar o carregamento completo da página
def wait_for_page_load(driver):
    WebDriverWait(driver, 30).until(
        lambda driver: driver.execute_script('return document.readyState') == 'complete'
    )

# Função para acessar e extrair detalhes de um produto
def get_product_details(driver, product_url):
    print(f"\n[INFO] Acessando o produto: {product_url}")
    try:
        driver.get(product_url)
        wait_for_page_load(driver)  # Aguardar carregamento completo da página
        
        # Esperar até que o título do produto esteja disponível
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1.olx-text"))
        )

        title = driver.find_element(By.CSS_SELECTOR, "h1.olx-text").text
        print(f"[INFO] Título encontrado: {title}")

        description_element = driver.find_elements(By.CSS_SELECTOR, ".ad__sc-1sj3nln-1")
        description = description_element[0].text if description_element else "Descrição não disponível."
        print(f"[INFO] Descrição encontrada: {description}")

        image_element = driver.find_elements(By.CSS_SELECTOR, "picture img")
        image_url = image_element[0].get_attribute("src") if image_element else None
        if image_url:
            print(f"[INFO] Imagem encontrada: {image_url}")
            image_filename = os.path.join("images", os.path.basename(urlparse(image_url).path))
            download_image(image_url, image_filename)
        else:
            print("[AVISO] Imagem principal não encontrada.")
            image_filename = None

        return {
            "title": title,
            "description": description,
            "image_url": image_url,
            "image_filename": image_filename
        }

    except Exception as e:
        print(f"[ERRO] Falha ao obter detalhes do produto {product_url}: {e}")
        return None

# Função para baixar a imagem
def download_image(image_url, filename):
    try:
        if not os.path.exists("images"):
            os.makedirs("images")

        response = requests.get(image_url)
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"[INFO] Imagem salva: {filename}")
    except Exception as e:
        print(f"[ERRO] Falha ao baixar a imagem: {e}")

# Função principal
def main():
    search_term = input("Digite o termo de pesquisa: ")

    # Configurar o Selenium
    driver = configure_driver()

    try:
        # Realizar o scraping
        product_links = get_product_links_selenium(driver, search_term)

        if not product_links:
            print("[AVISO] Nenhum produto encontrado para a pesquisa.")
            return

        # Processar os produtos
        product_details = []
        for idx, product_url in enumerate(product_links):
            print(f"\n[INFO] Processando o produto {idx + 1} de {len(product_links)}...")
            details = get_product_details(driver, product_url)
            if details:
                product_details.append(details)

            # Reiniciar o WebDriver após obter os dados de cada produto
            print("[INFO] Reiniciando o WebDriver...")
            driver.quit()  # Fechar o driver atual
            driver = configure_driver()  # Reiniciar o driver

        # Exibir os detalhes dos produtos
        if product_details:
            print(f"\n[INFO] Detalhes dos produtos encontrados ({len(product_details)}):")
            for details in product_details:
                print(f"Produto: {details['title']}")
                print(f"Descrição: {details['description']}")
                print(f"Imagem: {details['image_filename']}")
                print("\n")
        else:
            print("[AVISO] Nenhum detalhe de produto foi extraído.")

    finally:
        # Fechar o navegador após a execução
        driver.quit()

# Executar o script
if __name__ == "__main__":
    main()
