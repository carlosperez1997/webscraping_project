from  selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time
import os
from os.path  import basename
import requests
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys

def GAME_webscraping(juego, consola, num):
    driver = webdriver.Chrome(ChromeDriverManager().install())

    driver.get("http://www.game.es")
    time.sleep(3)

    # Cookies
    try: 
        driver.find_element_by_id("btnOverlayCookiesClose").click()
    except:
        pass

    # Search
    search = juego+' '+consola
    driver.find_element_by_id("searchinput").send_keys(search)
    time.sleep(1)
    driver.find_element_by_id("submitsearch").click()
    time.sleep(2)

    content = driver.page_source
    soup = BeautifulSoup(content)

    titulos = soup.findAll("h3",class_="title")
    tipo_precios = soup.findAll("h4",class_="buy--type")
    plataformas = soup.findAll(class_="btn btn-link btn-sm")
    precios = soup.findAll(class_="buy--price")
    imagenes = soup.findAll(class_="img-responsive")

    products = pd.DataFrame(columns=['p_titulo','p_imagen','p_precio'])    

    for item, tipo, plataforma, price, img in zip(titulos, tipo_precios, plataformas, precios, imagenes):
        titulo_juego = item.get_text().replace('\n','')
        tipo_precio = tipo.get_text().replace('\n','')
        machine = str.lower(plataforma.get_text()).replace('\n','')
        imagen = img.get("data-src")
            
        integer = price.find(class_="int").get_text()
        decimal = price.find(class_="decimal").get_text().rstrip("\n")
            
        n = len(decimal[1:]) 
        if n != 0:   
            precio = int(str(integer)+str(decimal[1:]))/10**n
        else:    
            precio = integer
            
            #if consola == 'PS3':
            #    consola = 'PlayStation 3'
            #if consola == 'PS4':
            #    consola = 'PlayStation 4'
            #if consola == 'PS5':
            #    consola = 'PlayStation 5'

        if tipo_precio == 'Comprar': #and str.lower(consola) in machine:
            #print(titulo_juego,'/',tipo_precio,'/',machine,'/',precio)
            products = products.append({'p_titulo':titulo_juego,'p_imagen':imagen,'p_precio':precio}, ignore_index=True)
        else:
            pass
                #print('---',titulo_juego,'/',tipo_precio,'/',machine,'/',precio)

    time.sleep(2)
    driver.close()

    return(products.head(num))


def FNAC_webscraping(juego, consola, num):

    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get("http://www.fnac.es")
    time.sleep(4)

    # Cookies
    cookies = driver.find_elements_by_class_name("onetrust-close-btn-handler")
    for x in cookies:
        try:
            x.click()
        except:
            pass
    
    content = driver.page_source
    soup = BeautifulSoup(content)

    categories = soup.findAll(class_="CategoryNav-link js-CategoryNav-link")
    for cat in categories:
        category = str(cat.get_text()).lower()
        if 'videojuegos' in category:
            new_link = cat.get('href')

    driver.get(new_link)
    time.sleep(2)

    elements = driver.find_elements_by_class_name("Header__aisle-list")
    elements[0].click()
    
    opciones = driver.find_elements_by_class_name("select-option")

    for op in opciones:
        #print(op.text)
        if op.text == 'Videojuegos':
            op.click()
            break

    search = juego+' '+consola
    driver.find_element_by_id("Fnac_Search").send_keys(search)
    driver.find_element_by_class_name("Header__search-submit").click()
    
    content = driver.page_source
    soup = BeautifulSoup(content)

    titulos = soup.findAll(class_="Article-title js-minifa-title js-Search-hashLink")
    precios = soup.findAll(class_="userPrice")
    imagenes = soup.findAll(class_="Article-itemVisualImg")

    products = pd.DataFrame(columns=['p_titulo','p_imagen','p_precio'])

    for t, p, i in zip(titulos,precios,imagenes):
        titulo = t.get_text().replace('\n','').lstrip()
        price = p.get_text().replace('\n','').replace(' ','').replace(',','.')[:-1] 
        
        if str(i.get("src"))[:4] == 'http':
            imagen = str(i.get("src"))
        else:
            imagen = str(i.get("data-lazyimage"))
        
        #print(titulo,price,imagen)
        
        products = products.append({'p_titulo':titulo,'p_imagen':imagen,'p_precio':price}, ignore_index=True)

    time.sleep(2)
    driver.close()

    return(products.head(num))


def CEX_webscraping(juego, consola, num):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    #driver.get('https://duckduckgo.com/')
    #print(driver.execute_script("return navigator.userAgent;"))

    # Setting UserAgent as Chrome/83.0.4103.97
    #driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'})
    #print(driver.execute_script("return navigator.userAgent;"))

    driver.get("https://es.webuy.com/")
    time.sleep(2)

    search = juego+' '+consola
    driver.find_element_by_name("stext").send_keys(search)
    time.sleep(1)
    driver.find_element_by_name("stext").send_keys(Keys.ENTER)
    driver.find_element_by_name("stext").send_keys(Keys.ENTER)

    time.sleep(1)
    driver.find_element_by_class_name("searchright").click()
    driver.find_element_by_class_name("close-text").click()
    time.sleep(0.5)
    driver.find_element_by_class_name("heartIcon_hover").click()
    driver.find_element_by_class_name("heartIcon_hover").click()

    content = driver.page_source
    soup = BeautifulSoup(content)

    #productos = soup.findAll({"class":"desc","h1":True})
    productos = soup.findAll(class_='t058-product-img')
    precios = soup.findAll(class_='priceTxt')
    imagenes = soup.findAll(class_='t058-product-img')

    print(productos)

    products = pd.DataFrame(columns=['p_titulo','p_imagen','p_precio'])

    for prod, price, img in zip(productos, precios, imagenes):
            
        producto = str(prod.get('alt')).replace('\n','').lstrip().rstrip()

        tag = str(price.get_text())
        if 'Vendemos' in tag:
            precio = tag[9:-1].replace('\n','')
            
        imagen = img.get('src').replace('\n','')
            
        #print(producto,'/',precio,'/',imagen)
            
        products = products.append({'p_titulo':producto,'p_imagen':imagen,'p_precio':precio}, ignore_index=True)
    
    driver.close()

    return(products.head(num))


def CARREFOUR_webscraping(juego, consola, num):
    driver = webdriver.Chrome(ChromeDriverManager().install())

    driver.get('https://duckduckgo.com/')
    print(driver.execute_script("return navigator.userAgent;"))

    # Setting UserAgent as Chrome/83.0.4103.97
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'})
    print(driver.execute_script("return navigator.userAgent;"))

    driver.get("https://www.carrefour.es/")
    time.sleep(2)

    driver.find_element_by_class_name("cookies__button").click()
    
    search = juego+' '+consola
    driver.find_element_by_class_name("search-bar").click()

    driver.find_element_by_class_name("ebx-search-box__input-query").send_keys(search)
    time.sleep(0.5)
    driver.find_element_by_class_name("ebx-search-box__input-query").send_keys(Keys.ENTER)
    time.sleep(0.5)
    driver.find_element_by_class_name("ebx-search-box__search-button").click()

    content = driver.page_source
    soup = BeautifulSoup(content)

    productos = soup.findAll(class_='ebx-result-title ebx-result__title')
    imagenes = soup.findAll(class_='ebx-result-figure__img')
    precios = soup.findAll(class_='ebx-result-price__value')

    products = pd.DataFrame(columns=['p_titulo','p_imagen','p_precio'])

    for prod, img, price in zip(productos,imagenes,precios):
        producto = prod.get_text().replace('\n','')
        imagen = img.get("src")
        precio = str(price.get_text()[:-1]).replace('\n','').replace(',','.')
        
        products = products.append({'p_titulo':producto,'p_imagen':imagen,'p_precio':precio}, ignore_index=True)
        
        #print(producto,'/',imagen,'/',precio)

    return(products.head(num))
    