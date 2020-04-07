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
    Subportadoras = np.zeros(S)# np.linspace(1920e6, 1920180000, S + 1)

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
    cerosEliminar = 0
    r_cell = 500
    N0 = 5.012e-21 #-173 #dBm/Hz
    BW = 3.75e3
    kmax = 4
    # Rm : minima tasa de transmision de dispositivo MTC;
    # Ru : minima tasa de transmision de dispositivo uRLLC;
    # PmMax : máximo presupuesto de potencia de dispositivo MTC;
    # PuMax : máximo presupuesto de potencia de dispositivo uRLLC;;
    PuMax = .2 #23 dBm
    PmMax = .2 #23 dBm
    Ru = 0
    Rm = 0
    Pm = 0
    Pu = 0


def formacionUsuarios(sim, umbral):
    sim.U = umbral / 4
    sim.M = umbral - (umbral / 4)

    for i in range (0, int(sim.U)):
        # Usuarios uniformemente distribuidos dentro de la celda entre .1 a 500m
        d = mth.sqrt(np.random.uniform(0, 1) * (sim.r_cell ** 2))
        ple = 3
        rayleighGain = random.expovariate(1)
        h = ( d ** (-ple) ) * rayleighGain
        sim.ListaUsuariosuRLLC.append([i, h, 0, .2, False, 0, 0])

    for j in range (int(sim.U), int(sim.U + sim.M)):
        # Usuarios uniformemente distribuidos dentro de la celda entre .1 a 500m
        d = mth.sqrt(np.random.uniform(0, 1) * (sim.r_cell ** 2))
        ple = 3
        rayleighGain = random.expovariate(1)
        h = ( d ** (-ple) ) * rayleighGain
        sim.ListaUsuariosmMTC.append([j, h, 0, .2, False, 0, 0])

    # Agrupamiento de dispositivos MTC
    # Clasificación de dispositivos basada en su ganancia de canal promedio (descendentemente)
    # PROMEDIO DE GANANCIAS DE CANAL
    listaordenada = sorted(sim.ListaUsuariosmMTC, key=operator.itemgetter(1), reverse=True)
    sim.sortedListaUsuariosmMTC = listaordenada
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
    listaordenada2 = sorted(sim.ListaUsuariosuRLLC, key=operator.itemgetter(1), reverse=True)
    sim.sortedListaUsuariosuRLLC = listaordenada2




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
            sim.sortedListaUsuariosuRLLC[i][5] = i
            sim.sortedListaUsuariosuRLLC[i][6] = 0
            sim.sortedListaUsuariosuRLLC[i][4] = True
            # Se debe disminuir U
            # Quitar a h de la lista

        else:
            # Asignar los dispositivos uRLLC a los siguientes rangos del grupo
            sim.NOMA_clusters[j][1] = [1, sim.sortedListaUsuariosuRLLC[i][0]]
            sim.sortedListaUsuariosuRLLC[i][5] = j
            sim.sortedListaUsuariosuRLLC[i][6] = 1
            sim.sortedListaUsuariosuRLLC[i][4] = True
            j = j + 1

    print('indice j quedó en', j)
    sim.cerosEliminar = j
    #Ultima posición de asignación
    #sim.NOMA_clusters[j][1]

    w=0
    x=0
    #Agregar ceros a lista
    for g in range(0,j):
        sim.sortedListaUsuariosmMTC.insert(0, 0)

    #HACERLO CON FORS y KMAX dado

    for i in range(j, int(sim.M)):
        # Si el número de dispositivos mMTC [M] es mayor que el numero de grupos NOMA [C], los dispositivos sobrantes
        # serán asignados a los siguientes rangos del grupo
        # Ultima posición de asignación

        if i < (sim.C):
            # Asignar los dispositivos mmtc a los rangos mas bajos de los primeros grupos
            sim.NOMA_clusters[j][1] = [2, sim.sortedListaUsuariosmMTC[i][0]]
            sim.sortedListaUsuariosmMTC[i][5] = i
            sim.sortedListaUsuariosmMTC[i][6] = 1
            sim.sortedListaUsuariosmMTC[i][4] = True
            j = j + 1

        elif i < (2*sim.C):
            # Asignar los dispositivos uRLLC a los siguientes rangos del grupo
            sim.NOMA_clusters[w][2] = [2, sim.sortedListaUsuariosmMTC[i][0]]
            sim.sortedListaUsuariosmMTC[i][5] = w
            sim.sortedListaUsuariosmMTC[i][6] = 2
            sim.sortedListaUsuariosmMTC[i][4] = True
            w = w + 1

        elif i < (3*sim.C):
            # Asignar los dispositivos uRLLC a los siguientes rangos del grupo
            sim.NOMA_clusters[x][3] = [2, sim.sortedListaUsuariosmMTC[i][0]]
            sim.sortedListaUsuariosmMTC[i][5] = x
            sim.sortedListaUsuariosmMTC[i][6] = 3
            sim.sortedListaUsuariosmMTC[i][4] = True
            x = x + 1

        else:
            print('indice quedó en',i, ' y eran ', sim.M, ' usuarios tipo maquina MTC' )
            break;



def algoritmoAsignacionRecursos(sim):
    #Inicialización
    sim.Ru = 0
    sim.Rm = 0
    sim.Pm = sim.PmMax
    sim.Pu = sim.PuMax
    sim.sortedListaUsuariosmMTC
    sim.sortedListaUsuariosuRLLC
    sim.Subportadoras

    Sv = 0
    Sac = [] #conjunto de subcanales establecidos
    Cns = sim.NOMA_clusters.copy() #Conjunto de clusters de dispositivos con tasas insatisfechas
    c_ = 0 #Mejor cluster que maximiza la tasa

    #Eliminar ceros que se agregaron a lista
    del sim.sortedListaUsuariosmMTC[0:sim.cerosEliminar]

    Ruth = mth.sqrt(np.random.uniform(.1, 20)) * 1e3
    Rmth = mth.sqrt(np.random.uniform(.1, 2)) * 1e3

    #while len(sim.Subportadoras) != 0 & sim.Ru < Ruth & sim.Rm < Rmth:


        #gamma = 0 #variable binaria que indica 1 si el cluster se asgna a subportadora
        #alpha = 0 #variable binaria que asigna mtc al kth rango de los clusters
        #beta= 0 #variable binaria que asigna urllc al kth rango de los clusters

        #la tasa de transmision alcanzada del dispositivo mtc, Rm
        # URLLC no interfieren a los mMTC por que estos tienen rangos mas altos

    sim.Rm = []
    sim.Ru = []



    for ci in range(0, len(Cns)):
        R=0
        Rtotal=0
        for cn in range(0, sim.kmax):

            if Cns[ci][cn][0] == 1:

                u1 = Cns[ci][cn][1]
                u = busquedaDispositivouRLLC(u1,sim)
                Interferencias = calculoInterferenciauRLLC(u, sim)

                R = sim.BW * mth.log2(1 + (((abs(sim.sortedListaUsuariosuRLLC[u][1]) ** 2) * (sim.sortedListaUsuariosuRLLC[u][3])) / ((sim.N0 * sim.BW) + Interferencias)))
                Rtotal = Rtotal + R
            else:

                m1 = Cns[ci][cn][1]
                m = busquedaDispositivomMTC(m1, sim)

                Interferencias = calculoInterferenciamMTC(m, sim)

                R = sim.BW * mth.log2(1 + (((abs(sim.sortedListaUsuariosmMTC[m][1]) ** 2) * (sim.sortedListaUsuariosmMTC[m][3])) / ((sim.N0 * sim.BW) + Interferencias)))
                Rtotal = Rtotal + R
        Cns[ci].append(Rtotal)
    #c_ = max()



def busquedaDispositivomMTC(m, sim):
    for i in range(0,len(sim.sortedListaUsuariosmMTC)):
        if sim.sortedListaUsuariosmMTC[i][0] == m:
            break
    return i


def busquedaDispositivouRLLC(u, sim):
    for i in range(0,len(sim.sortedListaUsuariosuRLLC)):
        if sim.sortedListaUsuariosuRLLC[i][0] == u:
            break
    return i



def calculoInterferenciauRLLC(u,sim):
    Int1 = 0
    Int2 = 0
    I = 0
    for i in range(0, len(sim.sortedListaUsuariosuRLLC)):
        if sim.sortedListaUsuariosuRLLC[i][6] >= sim.sortedListaUsuariosuRLLC[u][6]:
            if sim.sortedListaUsuariosuRLLC[i][0] != sim.sortedListaUsuariosuRLLC[u][0]:
                I = (( abs( sim.sortedListaUsuariosuRLLC[i][1] )**2 ) * ( sim.sortedListaUsuariosuRLLC[i][3] ))
                Int2 = Int2 + I

    I = 0
    for i in range(0, len(sim.sortedListaUsuariosmMTC)):
        #Se puede quitar
        if sim.sortedListaUsuariosmMTC[i][6] >= sim.sortedListaUsuariosuRLLC[u][6]:
            I = (( abs( sim.sortedListaUsuariosmMTC[i][1] )**2 ) * ( sim.sortedListaUsuariosmMTC[i][3] ))
            Int1 = Int1 + I

    return Int1 + Int2

def calculoInterferenciamMTC(m,sim):
    Int = 0
    I = 0
    for i in range(0, len(sim.sortedListaUsuariosmMTC)):
        if sim.sortedListaUsuariosmMTC[i][6] >= sim.sortedListaUsuariosmMTC[m][6]:
            if sim.sortedListaUsuariosmMTC[i][0] != sim.sortedListaUsuariosmMTC[m][0]:
                I = (( abs( sim.sortedListaUsuariosmMTC[i][1] )**2 ) * ( sim.sortedListaUsuariosmMTC[i][3] ))
                Int = Int + I
    return Int


sim = Simulacion()
sim.r_cell = 500
sim.umbralArribos = 200 #192
formacionUsuarios(sim, sim.umbralArribos)
algoritmoAgrupamiento(sim)
algoritmoAsignacionRecursos(sim)