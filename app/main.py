from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from urllib.request import urlopen
import pandas as pd
import unittest
import glob
import os
import requests
from bs4 import BeautifulSoup
import unicodedata
import arrow
import numpy as np
import time
from time import mktime
import datetime
from sklearn.preprocessing import OrdinalEncoder
import chromedriver_binary



#El rango de fechas que se desea (el limite superior del rango siemopre sera al dia de hoy)

ahora = datetime.datetime.utcnow()
hoy = ahora.strftime('%d')
mes_hoy = ahora.strftime('%m')

primer_dia = hoy
primer_mes = mes_hoy


def scrap_sniim(primer_dia,primer_mes):
    #NAPS
    nap1 = 3
    nap2 = 2*nap1
    nap3 = 3*nap1
    nap4 = 10
    nap = 3
    nap2 = nap*2
    nap3 = nap2*2

    #DEFINIMOS OPCIONES
    options = webdriver.ChromeOptions()
    #options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    #construccion de url
    fecha_hoy = datetime.datetime.utcnow()
    segundo_dia = fecha_hoy.strftime('%d')
    segundo_mes = fecha_hoy.strftime('%m')
    url_inicial = 'http://www.economia-sniim.gob.mx/Consolidados.asp?dqdia='+primer_dia+'&dqmes='+primer_mes+'&dqanio=2022&aqdia='+segundo_dia+'&aqmes='+segundo_mes+'&aqanio=2022&Prod=1&Edo=&punto=&det='
    #LISTAS QUE NECESITAMOS
    productos = []
    lista_productos = []
    lista_op1 = []
    links=[]
    #EMPEZAMOS DRIVER Y BS4  
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options) 
    driver.get(url_inicial) 
    soup = BeautifulSoup(driver.page_source, "html.parser")
    time.sleep(8)
    option = soup.find_all("select",{"name":"Prod"})
    for o in option:
        opciones = o.find_all('option')
        for j in opciones:
            opciones_text = j.text.strip()
            lista_productos.append(opciones_text)
    
    lista_op = list(opciones)
    for l in lista_op:
        #print(l['value'])
        lista_op1.append(l['value'])
    lista_op1_series = pd.Series(lista_op1)
    lista_productos_series = pd.Series(lista_productos)
    #valores = list(df_1['Valor'])
    for v in lista_op1:
        #print(i)
        url1 = 'http://www.economia-sniim.gob.mx/Consolidados.asp?Prod='+str(v)+'&dqdia='+primer_dia+'&dqmes='+primer_mes+'&dqanio=2022&aqdia='+segundo_dia+'&aqmes='+segundo_mes+'&aqanio=2022&Edo=&punto=&det='
        links.append(url1)
    links_series = pd.Series(links)
    df_1 = pd.concat([lista_op1_series,lista_productos_series,links_series],axis=1)
    df_1.rename(columns={0:'Valor',1:'Producto',2:'Link'},inplace=True)
    
    lista_links = list(df_1['Link'])
    elements_lista = []
    elements_lista_links = []
    for s in lista_links:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(s)
        time.sleep(nap)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        time.sleep(nap)
        elements = soup.find_all('table')
        time.sleep(nap)
        for e in elements:
            links = e.find_all("a")
            for link in links:
                links1 = link.text.strip()
                links2 = link['href']
                elements_lista.append(links1)
                elements_lista_links.append(links2)
    
    elements_lista_serie = pd.Series(elements_lista)
    elements_links_serie = pd.Series(elements_lista_links)
    df11 = pd.concat([elements_lista_serie,elements_links_serie],axis=1)
    #df11 es productos links
    #limpiamos base la df11
    #df1 = df11.loc[df11[0] !='Regresar a Seleccionar Producto, Estado o Punto de Cotización',:] #funciona
    df1 = df11[(df11[0] != 'Regresar a Seleccionar Producto, Estado o Punto de Cotización') & (df11[0] != 'info_sniim@economia.gob.mx')] #funciona
    df1.dropna(inplace=True)
    df1.rename(columns={0:'Central',1:'Link'},inplace=True)
    df1['Central_1'] = df1['Central'].replace({' ':''}, regex=True)
    df1['Central_1'] = df1['Central_1'].str.replace('[^\w\s]','')
    df1['Central_1'] = df1['Central_1'].str.replace(r'\d+','')
    #centrales = pd.Series(df1['Central_1'].unique())
    #centrales = centrales.str.replace(r'\d+','')
    #centrales = centrales.replace({' ':''},regex=True)
    #centrales.drop_duplicates(inplace=True)

    #lista_no = ['ClickaquíparaverúltimafechaLunes_','ClickaquíparaverúltimafechaMartes_','ClickaquíparaverúltimafechaViernes_','ClickaquíparaverúltimafechaJueves_','ClickaquíparaverúltimafechaMiércoles_']
    #lista_no = lista_no.str.replace(u'\xa0', u' ')
    df1['Central_11'] = df1['Central_1'].str.replace(u'\xa0', u' ')
    df1['Central_11'] = df1['Central_11'].str.replace(' ','_')

    df1.drop('Central_1',inplace=True,axis=1)
    #centrales = centrales.reset_index()
    #centrales_final =centrales.drop(centrales.index[[19,20,43,48,49]])
    #centrales_final.drop(columns={'index'},inplace=True)
    df_nodisp_lunes = df1[(df1['Central_11'] == 'ClickaquíparaverúltimafechaLunes_')]
    df_nodisp_martes = df1[(df1['Central_11'] == 'ClickaquíparaverúltimafechaMartes_')]
    df_nodisp_miercoles = df1[(df1['Central_11'] == 'ClickaquíparaverúltimafechaMiércoles_')]
    df_nodisp_jueves = df1[(df1['Central_11'] == 'ClickaquíparaverúltimafechaJueves_')]
    df_nodisp_viernes = df1[(df1['Central_11'] == 'ClickaquíparaverúltimafechaViernes_')]

    df_nodisp_final = pd.concat([df_nodisp_lunes,df_nodisp_martes,df_nodisp_miercoles,df_nodisp_jueves,
                                 df_nodisp_viernes])


    df_final = df1.drop(df1[df1['Central_11']=='ClickaquíparaverúltimafechaMartes_'].index) #bien 
    df_final2 = df_final.drop(df_final[df_final['Central_11']=='ClickaquíparaverúltimafechaViernes_'].index) #bien 
    df_final3 = df_final2.drop(df_final2[df_final2['Central_11']=='ClickaquíparaverúltimafechaJueves_'].index) #bien 
    df_final4 = df_final3.drop(df_final3[df_final3['Central_11']=='ClickaquíparaverúltimafechaMiércoles_'].index) #bien 
    df_final5 = df_final4.drop(df_final4[df_final4['Central_11']=='ClickaquíparaverúltimafechaMartes_'].index) #bien 
    df_final6 = df_final5.drop(df_final5[df_final5['Central_11']=='ClickaquíparaverúltimafechaLunes_'].index) #bien 


    #print(df1['Central_11'].unique())
    #print(df_final6['Central_11'].unique())

    #centrales_final_1 = list(df_final6['Central_11'].unique())
    #centrales_finales = list(centrales_final[0])

    #DF_FINAL6 Y CENRALES_FINAL_1 SON LOS BUENOS (solo falta quitar unos)
    url_madre = 'http://www.economia-sniim.gob.mx/'

    links_bien = []
    for i in df_final6['Link']:
        url = url_madre + i
        links_bien.append(url)

    df_final6['Links_Bien'] = links_bien #bienHASTA AQUI
    
    links_bien1 = []
    for p in df_nodisp_final['Link']:
        url2 = url_madre + p
        links_bien1.append(url2)
    
    df_nodisp_final['Links_Bien'] = links_bien1

    
    #MANIPULAMOS
    df_final6.drop('Link',axis=1,inplace=True)
    df_nodisp_final.drop('Link',axis=1,inplace=True)

    #TRABAJAMOS
    enc = OrdinalEncoder()
    enc.fit(df_final6[["Central_11"]])
    df_final6[["Central_11"]] = enc.transform(df_final6[["Central_11"]])
    df_final6['Central_1'] = df_final6['Central'].str.replace('[^\w\s]','')
    df_final6['Central_1'] = df_final6['Central_1'].replace({' ':'_'}, regex=True)
    df_final6.drop('Central',axis=1,inplace=True)
    df_final6 = df_final6[(df_final6['Links_Bien'] != 'http://www.economia-sniim.gob.mx/JavaScript:history.go(-1);')] #funciona

           
    
    return df_final6, df_nodisp_final

df_prueba = scrap_sniim('08', '07')

df_1 = df_prueba[0]
df_2 = df_prueba[1]

def bs4W_sniim(url_x):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options) 
    driver.get(url_x)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    titulos = soup.find_all('td',class_='encabMER')
    titulo1 = titulos[0]
    titulo1 = titulo1.text.strip()
    titulo2 = titulos[1]
    titulo2 = titulo2.text.strip()
    df = pd.read_html(url_x,attrs={'align': 'center'}, header=0)[0]
    df['producto']  = titulo1
    df['central']  = titulo2
    df.drop([0],inplace=True)
    df.rename(columns={'Unnamed: 1':'Min','Unnamed: 2':'Max',
                       'Unnamed: 3':'Frec','Unnamed: 4':'Origen'},inplace=True)
    
    return df 



links = list(df_1['Links_Bien'])
lista_final = []
for i in links:
    #print(i)
    df_11 = bs4W_sniim(i)
    lista_final.append(df_11)
 
    


def bs4W_sniim2(url_y):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url_y)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    fecha = soup.find_all('td',class_='encabFEC')
    fecha = fecha[0]
    fecha = fecha.text.strip()
    titulos = soup.find_all('td',class_='encabMER')
    titulo1 = titulos[0]
    titulo1 = titulo1.text.strip()
    df = pd.read_html(url_y,attrs={'align': 'center'}, header=0)[0]
    df['fecha']  = fecha
    df['producto'] = titulo1
    #df['central']  = titulo2
    df.drop([0],inplace=True)
    df.rename(columns={'Unnamed: 1':'Min','Unnamed: 2':'Max',
                       'Unnamed: 3':'Frec','Unnamed: 4':'Origen'},inplace=True)
    df.drop(columns = {'Unnamed: 5'},inplace=True)
    
    return df 

links2 = list(df_2['Links_Bien'])

lista_final2 = []
for p in links2:
    #print(i)
    df_22 = bs4W_sniim2(p)
    lista_final2.append(df_22)
    
    
data_no_disp_final = pd.concat(lista_final2)
    
centrales = pd.concat(lista_final) #quedó en la cien 