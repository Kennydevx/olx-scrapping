from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os


# Função para coletar os links dos produtos
def get_product_links_selenium(driver, search_term):
    base_url = f"https://www.olx.com.br/brasil?q={search_term}"
    print(f"[INFO] Acessando URL de busca: {base_url}")
    driver.get(base_url)  # Carregar a página

    try:
        # Esperar até que os anúncios sejam carregados
        WebDriverWait(driver, 15).until(
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

# Função para coletar os detalhes de um produto específico
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

# Função de espera para garantir que a página foi completamente carregada
def wait_for_page_load(driver):
    WebDriverWait(driver, 30).until(
        lambda driver: driver.execute_script('return document.readyState') == 'complete'
    )
