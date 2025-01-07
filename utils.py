# utils.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
    driver.set_page_load_timeout(15)  # Timeout global para carregamento de páginas
    return driver

# Função para realizar scraping com Selenium e coletar links dos produtos
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
