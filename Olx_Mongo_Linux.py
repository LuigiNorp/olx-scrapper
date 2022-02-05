from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from pymongo import MongoClient


class BuscadorOlx:
    """
    Extrae la informacion del precio y descripción de los artículos contenidos en la página OLX Ecuador. Utiliza Selenium y una base de datos no
    relacional empleando MongoDB.
    Se puede cambiar
    :param articulo_buscado: Ingrese el nombre del articulo que busca
    :param selenium: Ingresar una tupla con los siguientes valores (n veces click cargar, pais)
    :param mongodb: Ingresar una tupla con las configuraciones para ingresar a mongoDB
            (cliente, base de datos, coleccion)
    """
    enlace = None
    driver = None

    @classmethod
    def __coleccion_mongodb(cls, tupla_configuraciones_mongodb):
        """
        Permite acceder al contenido de una colección mongodb que esté dentro de una base de datos proporcionada
            por el usuario que a su vez le pertenezca a un cliente definido por el usuario.
        :return: Devuelve la colección de mongodb con la que se está trabajando.
        """
        client = MongoClient(tupla_configuraciones_mongodb[0])
        db = client[tupla_configuraciones_mongodb[1]]
        col = db[tupla_configuraciones_mongodb[2]]
        return col

    @classmethod
    def __modificar_url(cls, texto_buscado: str, pais: str):
        """
        Verifica que el string introducido esté en el formato adecuado para hacer búsquedas a través de la url.
        Si un valor es diferente de None.
        :return: Si texto_buscado es diferente a None devuelve como string de la url
        'https://www.olx.com.ec/items/q-' + 'texto-buscado', (sustiuyendo en el texto buscado '  ' por '-').
        Si texto_buscado es None, se buscará por defecto en https://www.olx.com.ec/

        Ejemplo dando como valor de texto_buscado 'laptop dell', retorna:
        https://www.olx.com.ec/items/q-laptop-dell
        """
        if texto_buscado is not None:
            texto_buscado = str(texto_buscado).replace(' ', '-')
            cls.enlace = 'https://www.olx.com.' + pais + '/items/q-' + texto_buscado
        else:
            cls.enlace = 'https://www.olx.com.' + pais
        return cls.enlace

    @classmethod
    def __encontrar_boton_cargar_mas(cls):
        """
        Para esperar en lo que carga la información y encontrar boton cargar más
        """
        cls.__esperar_imagenes_cargadas()
        boton = WebDriverWait(cls.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//button[@data-aut-id="btnLoadMore"]')
            )
        )
        return boton

    @classmethod
    def __esperar_imagenes_cargadas(cls):
        """
        Espera hasta que todas las imagenes de artículos estén cargadas
        """
        WebDriverWait(cls.driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//img'))
        )

    @classmethod
    def __click_cargar_mas(cls, n_veces):
        """
        Espera a que las imagenes esten cargadas, detecta y hace click n veces en el boton cargar más.
        """
        for i in range(n_veces):
            try:
                cls.__encontrar_boton_cargar_mas().click()
                # cls.__esperar_imagenes_cargadas()
            except:
                pass

    @classmethod
    def __almacenar_e_imprimir(cls, anuncio, tupla_configuraciones_mongodb: tuple):
        """
        Almacena en una base de datos e imprime el precio y la descripción del anuncio
        """
        precio = anuncio.find_element(By.XPATH, './/span[@data-aut-id="itemPrice"]').text
        print("Precio: ", precio)
        descripcion = anuncio.find_element(By.XPATH, './/span[@data-aut-id="itemTitle"]').text
        print("Descripcion: ", descripcion)
        cls.__coleccion_mongodb(tupla_configuraciones_mongodb).insert_one({
            'precio': precio,
            'descripcion': descripcion
        })

    @classmethod
    def __lista_anuncios(cls):
        """
        Hace una lista de los anuncios contenidos en una página .
        """
        anuncios = cls.driver.find_elements(By.XPATH, '//li[@data-aut-id="itemBox"]')
        print(len(anuncios))
        return anuncios

    @classmethod
    def __extraer_anuncios_en_db(cls, tupla_configuraciones_mongodb: tuple):
        """
        Extrae el precio y descripción en cada anuncio detectado en la lista de anuncios. Y los almacena dentro
        de una coleccion en una base de datos de mongoDB.
        """
        cls.__esperar_imagenes_cargadas()
        for anuncio in cls.__lista_anuncios():
            cls.__almacenar_e_imprimir(anuncio, tupla_configuraciones_mongodb)

    @classmethod
    def __ejecutar_busqueda(cls, enlace, n_veces, ubicacion_driver, tupla_configuraciones_mongodb: tuple):
        """
        Se encarga de ingresar a la página por medio de Chromewebdriver, da clic n veces en el botón cargar,
        extrae los datos de precio y descripción de la página. Estos datos los almacena por default en una
        colección contenida en el localhost de mongodb.

        """
        opts = Options()
        cls.driver = webdriver.Chrome(ubicacion_driver, options=opts)
        cls.driver.get(enlace)
        cls.__click_cargar_mas(n_veces)
        cls.__extraer_anuncios_en_db(tupla_configuraciones_mongodb)
        cls.driver.quit()

    def __init__(self, articulo_buscado: str = None):
        """
        Permite extraer el precio y la descripcion de una lista obtenida de los articulos presentes en la url de
        olx.
        :param articulo_buscado: Ingrese el nombre del articulo que busca
        """
        self.n_veces = self.configuraciones_selenium()[0]
        self.pais = self.configuraciones_selenium()[1]
        self.ubicacion_driver = self.configuraciones_selenium()[2]
        self.enlace = self.__modificar_url(articulo_buscado, self.pais)
        self.__ejecutar_busqueda(self.enlace, self.n_veces, self.ubicacion_driver, self.configuraciones_mongodb())

    @staticmethod
    def configuraciones_selenium(n_veces: int = 3, pais: str = 'ec', ubicacion_driver: str = './chromedriver'):
        return n_veces, pais, ubicacion_driver

    @staticmethod
    def configuraciones_mongodb(cliente: str = 'localhost', basedatos: str = 'olx', coleccion: str = 'anuncios'):
        return cliente, basedatos, coleccion


if __name__ == '__main__':
    olx = BuscadorOlx()
