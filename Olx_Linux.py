# Se mejora la velocidad de extracción, reduciendo la espera haciendo clic
# al momento de que los elementos estén completamente cargados.

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

ubicacion_driver = '/mnt/3E09D94559310A77/Documents/Programacion/' \
                   'Aprendiendo_Programacion/01_Python/' \
                   '01-02_Web_Scraping_Compilation/Resources/' \
                   'chromedriver_Linux/chromedriver'

opts = Options()
# opts.add_argument('--no-sandbox')    # Por un problema en la version del webdriver

driver = webdriver.Chrome(ubicacion_driver, options=opts)
# driver.implicitly_wait(5)
driver.get('https://www.olx.com.ec/')

# Para hacer clic 3 veces en el botón cargar más
for i in range(3):
    try:  # Para evitar que dé un error por la imposibilidad de dar click

        # Para esperar en lo que carga la información y encontrar boton cargar más
        boton = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//button[@data-aut-id="btnLoadMore"]')
            )
        )
        try:
            # Espera hasta que todas las imagenes de artículos estén cargadas
            WebDriverWait(driver, 10).until(
                # EC.element_to_be_clickable((By.XPATH, '//img'))
                EC.presence_of_all_elements_located((By.XPATH, '//img'))
            )
        finally:
            # Dar clic
            boton.click()

    except:
        pass

# Extraer todos los anuncios en una lista
anuncios = driver.find_elements(By.XPATH, '//li[@data-aut-id="itemBox"]')
print(len(anuncios))
for anuncio in anuncios:
    # Imprimir por cada anuncio el precio y la descripción
    precio = anuncio.find_element(By.XPATH, './/span[@data-aut-id="itemPrice"]').text
    print(precio)
    descripcion = anuncio.find_element(By.XPATH, './/span[@data-aut-id="itemTitle"]').text
    print(descripcion)

driver.quit()