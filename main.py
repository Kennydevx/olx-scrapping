from utils import configure_driver, get_product_links_selenium
from downloader import save_product_data
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Função para esperar o carregamento completo da página
def wait_for_page_load(driver):
    WebDriverWait(driver, 15).until(
        lambda driver: driver.execute_script('return document.readyState') == 'complete'
    )

# Função para acessar e extrair detalhes de um produto
def get_product_details(driver, product_url):
    print(f"\n[INFO] Acessando o produto: {product_url}")
    try:
        driver.get(product_url)
        wait_for_page_load(driver)  # Aguardar carregamento completo da página
        
        # Esperar até que o título do produto esteja disponível
        WebDriverWait(driver, 10).until(
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
            save_product_data(title, description, image_url)  # Salvar os dados para o treinamento
        else:
            print("[AVISO] Imagem principal não encontrada.")

        return {
            "title": title,
            "description": description,
            "image_url": image_url
        }

    except Exception as e:
        print(f"[ERRO] Falha ao obter detalhes do produto {product_url}: {e}")
        return None

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
        for idx, product_url in enumerate(product_links):
            print(f"\n[INFO] Processando o produto {idx + 1} de {len(product_links)}...")
            details = get_product_details(driver, product_url)

            # Reiniciar o WebDriver após processar cada produto
            print("[INFO] Reiniciando o WebDriver...")
            driver.quit()  # Fechar o WebDriver atual
            driver = configure_driver()  # Recriar um novo WebDriver
            time.sleep(2)  # Dar um tempo para garantir que o WebDriver seja reiniciado corretamente

        print("[INFO] Scraping finalizado.")
    finally:
        # Fechar o navegador após a execução
        driver.quit()

# Executar o script
if __name__ == "__main__":
    main()
