from img2vec_pytorch import Img2Vec
import torch
from PIL import Image
import numpy as np
import base64
from io import BytesIO
import psycopg2
import scipy.spatial.distance as dist
import statistics

def convertArray(numpyArray):
    newArray = []
    for elem in numpyArray:
        newArray.append(elem)
    return newArray


def extraerVector(imagen):
    img2vec = Img2Vec(cuda=False)
    vec = img2vec.get_vec(imagen, tensor=True)
    return vec


def resizeImagen(imagen):
    head, tail = imagen.split(',')
    imagen=Image.open(BytesIO(base64.b64decode(tail, '-_')))
    final_size = 224
    size = imagen.size
    ratio = float(final_size) / max(size)
    new_image_size = tuple([int(x * ratio) for x in size])
    imagen = imagen.resize(new_image_size, Image.ANTIALIAS)

    new_im = Image.new("RGB", (final_size, final_size))
    new_im.paste(imagen, ((final_size - new_image_size[0]) // 2, (final_size - new_image_size[1]) // 2))

    return new_im

def conectarAPostgres():
    conn = psycopg2.connect(
        host="localhost",
        database="proyectoGad",
        user="postgres",
        password="luxlp1996")
    return conn

def tensorToString(embeddingsVector):
    numpyVector = np.array(embeddingsVector.unsqueeze(0).tolist())

    stringVector = str(convertArray(numpyVector.flatten()))

    stringVector = '{' + stringVector[1:]
    stringVector = stringVector[:-1] + '}'

    return stringVector

def obtenerPokemonSimil(imagen):
    conn=conectarAPostgres()
    listasimilaridades=[]
    cr = conn.cursor()
    embeddingsVector = extraerVector(resizeImagen(imagen))
    cr.execute('Select * from imagenes;')
    listaimagenes = cr.fetchall()
    for i in listaimagenes:
        distancia = dist.euclidean(embeddingsVector, i[2])
        listasimilaridades.append(distancia)
    sorted_distancias = sorted(((v, i) for i, v in enumerate(listasimilaridades)))
    listaresultados = []
    listanombres = []
    contador = 0
    indice = 0
    while contador <= 4:
        if listaimagenes[sorted_distancias[indice][1]][1] not in listanombres:
            '''
            cr.execute('Select * from pokemon where pokemon.nombre = %s;',
                       [listaimagenes[sorted_distancias[indice][1]][1]])
            resultado = cr.fetchall()
            '''
            listaresultados.append((sorted_distancias[indice][0], listaimagenes[sorted_distancias[indice][1]][1], listaimagenes[sorted_distancias[indice][1]][3]))
            listanombres.append(listaimagenes[sorted_distancias[indice][1]][1])
            contador += 1
        indice += 1
    return listaresultados

def dimensionalidadintrinseca():
    conn = conectarAPostgres()
    cr = conn.cursor()
    cr.execute('select vector from imagenes')
    vectores = cr.fetchall()

    distancias = []

    for vector1 in vectores:
        for vector2 in vectores:
            distancias.append(dist.euclidean(vector1[0], vector2[0]))
    return (statistics.mean(distancias)^2)/(2*statistics.variance(distancias))
