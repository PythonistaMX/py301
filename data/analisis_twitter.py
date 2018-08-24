
# coding: utf-8

get_ipython().magic(u'pylab inline')
import csv, twitter, json, nltk
import networkx as nx
from functools import reduce
from matplotlib import pyplot as plt
from wordcloud import WordCloud

CONSUMER_KEY, CONSUMER_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET = "", "", "", ""


def accede_a_tw(fuente):
    (CONSUMER_KEY,
     CONSUMER_SECRET,
     OAUTH_TOKEN,
     OAUTH_TOKEN_SECRET) = open(
            fuente, 'r').read().splitlines()
    auth = twitter.oauth.OAuth(OAUTH_TOKEN,
                           OAUTH_TOKEN_SECRET,
                           CONSUMER_KEY,
                           CONSUMER_SECRET)
    return twitter.Twitter(auth=auth)

def carga_lista(archivo):
    try:
        f = open(archivo, "r")
        lista = [elemento.replace(" ", "") for elemento in reduce(lambda x,y: x + y, 
                [linea for linea in csv.reader(f, dialect="unix")])]
    except IOError:
        lista = []
    else:
        f.close()
    return lista


def busqueda_tw(tw, termino):
    return tw.search.tweets(q=termino, lang="es", count="500")["statuses"]


def guarda_tuits(tuits, archivo):
    with open(archivo, "w") as f:
        json.dump(tuits, f, indent=1)


def carga_tuits(archivo):
    try:
        f = open(archivo, "r")
        resultado = json.load(f)
    except IOError:
        resultado = []
    else:
        f.close()
    return resultado


def mezcla_tuits(actuales, nuevos):
    for tuit in nuevos: 
        if tuit["id"] not in [actual["id"] for actual in actuales]:
            actuales.append(tuit)
    return actuales

def limpiar(texto):
    tokenizer = nltk.RegexpTokenizer(r'\w+')
    limpio = tokenizer.tokenize(texto)    
    return limpio 

def analiza_menciones(tuits):
    pares = []
    nodos = []
    for tuit in tuits:
        usuario = tuit["user"]["screen_name"]
        nodos.append(usuario)
        menciones = [mencion["screen_name"] for mencion in tuit["entities"]["user_mentions"]]
        for mencion in menciones:
            if mencion != [] and usuario != mencion:
                par = (usuario, mencion)
                pares.append(par)
    nodos = list(set(nodos))
    pares = list(set(pares))
    G = nx.Graph()
    G.add_nodes_from(nodos)
    G.add_edges_from(pares)
    plt.figure(figsize=(32,32))
    nx.draw_networkx(G)
    
def refina_texto(tuits, lista, termino):
    lista_negra = carga_lista(lista) + [palabra.replace("@", "") for palabra in termino.split()]
    texto =""
    for i in range(0, len(lista_negra)):
        lista_negra[i] = lista_negra[i].lower()
    for tuit in tuits:
        texto += (tuit["text"] + " ")
        depurador = nltk.RegexpTokenizer(r'\w+')
    limpio = depurador.tokenize(texto)
    texto = ""
    for termino in limpio:
        termino = termino.lower()
        if  termino not in lista_negra:
            texto += (termino + " ") 
    return str(texto)

def nube(texto):
    wordcloud = WordCloud().generate(texto)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.show()
    
def main(archivo="tuits.json", lista="lista_negra.csv"): 
    termino = input("Término de búsqueda: ")
    tuits_previos = carga_tuits(archivo)
    tw = accede_a_tw("credenciales.txt")
    tuits_recientes = busqueda_tw(tw, termino)
    tuits = mezcla_tuits(tuits_previos, tuits_recientes)
    guarda_tuits(tuits, archivo)
    analiza_menciones(tuits)
    return refina_texto(tuits, lista, termino)


