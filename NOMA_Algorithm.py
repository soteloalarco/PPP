import sys
import numpy as np
import math as mth
import simpy
import cmath as cmth
import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon # Librería para dibujar los hexagonos
import random
import operator



class Simulacion(object):

    """Esta clase representa a una Simulación de eventos discretos"""
    # DEFINICIÓN DE CONSTANTES, LISTAS Y VARIABLES

    # Número de subportadoras, en NBIoT son 48 subportadoras de 3.75Khz
    S = 48

    # Lista de frecuencias para subportadoras NB-IoT de banda 1920 MHz
    Subportadoras = np.linspace(1920e6, 1920180000, S + 1)

    # Número de clústers/grupos
    C = 48
    # Número de dispositivos por grupo, 2 o 4
    K = 4
    # Número de dispositivos tipo uRLLC
    U = 0
    # Número de dispositivos tipo mMTC
    M = 0

    # Lista de grupos NOMA
    NOMA_clusters = []

    # hu: lista de ganancias de dispositivos tipo uRLLC
    hu = []
    # hu1: lista de ganancias de dispositivos tipo uRLLC
    hu1 = []
    # hu_sorted: lista de ganancias de dispositivos tipo uRLLC
    hu_sorted = []

    # hm: lista de ganancias de dispositivos tipo MTC
    hm = []
    # hm1: lista de ganancias de dispositivos tipo MTC
    hm1 = []
    # hm_sorted: lista de ganancias de dispositivos tipo MTC
    hm_sorted = []
    umbralArribos = 0 # Número de arribos a simular (CONDICIÓN DE PARO)
    # ListaEstacionesBase = [ID, posicion, contador_UE, [CH0,CH1,CH2,CH3,CH4,CH5,CH6,CH7,CH8,CH9]]
    #donde CH lista anidada [Tipo, distancia a UE]
    ListaEstacionesBase = []
    #Listausuarios=[Id, ganancia canal, Agrupamiento]
    ListaUsuariosmMTC=[]
    ListaUsuariosuRLLC=[]
    sortedListaUsuariosmMTC = []
    sortedListaUsuariosuRLLC = []
    r_cell = 500
    N0 = -173 #dBm/Hz
    PuMax = 23 #dBm
    PmMax = 23 #


def formacionUsuarios(sim, umbral):
    sim.U = umbral / 4
    sim.M = umbral - (umbral / 4)

    for i in range (0, int(sim.U)):
        # Usuarios uniformemente distribuidos dentro de la celda entre .1 a 500m
        d = mth.sqrt(np.random.uniform(0, 1) * (sim.r_cell ** 2))
        ple = 3
        rayleighGain = random.expovariate(1)
        h = ( d ** (-ple) ) * rayleighGain
        sim.ListaUsuariosuRLLC.append([i, h, False])

    for j in range (int(sim.U), int(sim.U + sim.M)):
        # Usuarios uniformemente distribuidos dentro de la celda entre .1 a 500m
        d = mth.sqrt(np.random.uniform(0, 1) * (sim.r_cell ** 2))
        ple = 3
        rayleighGain = random.expovariate(1)
        h = ( d ** (-ple) ) * rayleighGain
        sim.ListaUsuariosmMTC.append([j, h, False])

    # Agrupamiento de dispositivos MTC
    # Clasificación de dispositivos basada en su ganancia de canal promedio (descendentemente)
    # PROMEDIO DE GANANCIAS DE CANAL
    sim.sortedListaUsuariosmMTC = sorted(sim.ListaUsuariosmMTC, key=operator.itemgetter(1), reverse=True)
    #Agrupamiento de dispositivos uRLLC
    # Clasificación de dispositivos basada en su ganancia de canal promedio (descendentemente)
    # PROMEDIO DE GANANCIAS DE CANAL
    # hu2 = 0
    # for j in range(0, len(S)):
    #    #Ir calculando la ganancia del canal para cada subportadora
    #    #hu = coficientes de canal para usuario u, u aún se debe definir
    #    hu2 = hu2 + hu[j]/S
    # h#u1.append(hu2)

    # hu_sorted = hu1.sort(reverse = True)
    sim.sortedListaUsuariosuRLLC = sorted(sim.ListaUsuariosuRLLC, key=operator.itemgetter(1), reverse=True)



# Algoritmo para el agrupamiento de dispositivos (clustering NOMA)

# Se empiezan a agrupar usuarios con una alta ganancia de canal promedio,
# en la recepción tipo SIC se decodifican primero los usuarios con una alta ganancia de canal promedio antes que los de baja ganancia  de canal promedio
# Los rangos de los dispositivos uRLLC deben ser menores que los MTC para que sea eficiente la decodificación SIC
# PREGUNTA: La ganancia de canal considera las pérdidas por la distancia o solo al desvanecimiento
def algoritmoAgrupamiento(sim):
    j = 0
    for i in range(0, int(sim.U)):
        # Si el número de dispositivos uRLLC [U] es mayor que el numero de grupos NOMA [C], los dispositivos sobrantes
        # serán asignados a los siguientes rangos del grupo
        if i < sim.C:
            # Asignar los dispositivos uRLLC a rangos bajos de los primeros grupos
            sim.NOMA_clusters.append([[1, sim.sortedListaUsuariosuRLLC[i][0]], False, False, False])
            sim.sortedListaUsuariosuRLLC[i][2] = True
            # Se debe disminuir U
            # Quitar a h de la lista

        else:
            # Asignar los dispositivos uRLLC a los siguientes rangos del grupo
            sim.NOMA_clusters[j][1] = [1, sim.sortedListaUsuariosuRLLC[i][0]]
            sim.sortedListaUsuariosuRLLC[i][2] = True
            j = j + 1
    print('indice j quedó en', j)
    #Ultima posición de asignación
    #sim.NOMA_clusters[j][1]

    w=0
    x=0

    for i in range(0, int(sim.M)):
        # Si el número de dispositivos mMTC [M] es mayor que el numero de grupos NOMA [C], los dispositivos sobrantes
        # serán asignados a los siguientes rangos del grupo
        # Ultima posición de asignación

        if i < sim.C:
            # Asignar los dispositivos mmtc a los rangos mas bajos de los primeros grupos
            sim.NOMA_clusters[j][1] = [2, sim.sortedListaUsuariosmMTC[i][0]]
            sim.sortedListaUsuariosmMTC[i][2] = True
            j = j + 1

        elif i < 2*sim.C:
            # Asignar los dispositivos uRLLC a los siguientes rangos del grupo
            sim.NOMA_clusters[w][2] = [2, sim.sortedListaUsuariosmMTC[i][0]]
            sim.sortedListaUsuariosmMTC[i][2] = True
            w = w + 1

        elif i < 3*sim.C:
            # Asignar los dispositivos uRLLC a los siguientes rangos del grupo
            sim.NOMA_clusters[x][3] = [2, sim.sortedListaUsuariosmMTC[i][0]]
            sim.sortedListaUsuariosmMTC[i][2] = True
            x = x + 1

        else:
            print('indice quedó en',i, ' y faltaron ', sim.M, ' usuarios tipo maquina MTC' )
            break;





sim = Simulacion()
sim.r_cell = 500
sim.umbralArribos = 200
formacionUsuarios(sim, sim.umbralArribos)
algoritmoAgrupamiento(sim)