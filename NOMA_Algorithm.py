import sys
import simpy
import cmath as cmth
import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon # Librería para dibujar los hexagonos
import pandas as pd
import numpy as np
import math as mth
import random
import operator
import copy



class Simulacion(object):
    """Esta clase representa a una Simulación de eventos discretos"""
    # DEFINICIÓN DE CONSTANTES, LISTAS Y VARIABLES
    umbralArribos = 0
    # Número de subportadoras, en NBIoT son 48 subportadoras de 3.75Khz
    S = 48
    # Lista de frecuencias para subportadoras NB-IoT de banda 1920 MHz
    Subportadoras = list(np.zeros(S))# np.linspace(1920e6, 1920180000, S + 1)
    # Número de clústers ó grupos
    C = 48
    # Número de dispositivos por grupo, 2 o 4
    K = 4
    # Número de dispositivos tipo uRLLC
    U = 0
    # Número de dispositivos tipo mMTC
    M = 0
    # Lista de grupos NOMA: [tipo_dispositivo, ID_dispositivo]
    # donde tipo_dispositivo =1 URLLC, tipo_dispositivo =2 MTC
    NOMA_clusters = []
    # hu: lista de ganancias de dispositivos tipo uRLLC
    hu = []
    # hu_sorted: lista de ganancias de dispositivos tipo uRLLC
    hu_sorted = []
    # hm: lista de ganancias de dispositivos tipo MTC
    hm = []
    # hm_sorted: lista de ganancias de dispositivos tipo MTC
    hm_sorted = []
    # Listausuarios = [Id, ganancia_canal, tasa_transmision bps, potencia watts, (variable booleana de asignacion a grupo NOMA), id_grupoNOMA, rango_grupoNOMA, valor sin ocupar]
    ListaUsuariosmMTC=[]
    ListaUsuariosuRLLC=[]
    sortedListaUsuariosmMTC = []
    sortedListaUsuariosuRLLC = []
    cerosEliminar = 0
    r_cell = 500
    N0 = 5.012e-21 #-173 #dBm/Hz
    BW = 3.75e3
    kmax = 4
    #Tasa a satisfacer por usuarios URLLC
    Ruth = 0
    #Tasa a satisfacer por usuarios MTC
    Rmth = 0
    # PuMax : máximo presupuesto de potencia de dispositivo uRLLC;
    PuMax = .2 # 23 dBm
    # PmMax : máximo presupuesto de potencia de dispositivo MTC;
    PmMax = .2 # 23 dBm
    Pm = 0
    Pu = 0
    # Ru : minima tasa de transmision de dispositivo uRLLC;
    Ru = 0
    # Rm : minima tasa de transmision de dispositivo MTC;
    Rm = 0
    #Grupos NOMA con tasas insatisfechas
    Cns = []
    #Tasas alcanzadas por cada grupo NOMA
    Rates = []
    #S^ -> S prima que no sé realmente para que se usa
    Sv = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]  
    #Conjunto de subportadoras establecidos
    Sac = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]  
    #gamma = 0 #variable binaria que indica 1 si el cluster se asigna a subportadora
    #alpha = 0 #variable binaria que asigna mtc al rango unesimo de los clusters
    #beta = 0 #variable binaria que asigna urllc al rango unesimo de los clusters

def formacionUsuarios(sim):
    # Division de usuarios entre U y M
    sim.U = sim.umbralArribos / 4
    sim.M = sim.umbralArribos - (sim.umbralArribos / 4)
    
    # Usuarios uniformemente distribuidos dentro de la celda entre .1 a 500m
    for i in range (0, int(sim.U)):
        d = mth.sqrt(np.random.uniform(0, 1) * (sim.r_cell ** 2))
        ple = 3
        rayleighGain = random.expovariate(1)
        h = ( d ** (-ple) ) * rayleighGain
        # Listausuarios = [Id, ganancia_canal, tasa_transmision bps, potencia watts, (variable booleana de asignacion a grupo NOMA), id_grupoNOMA, rango_grupoNOMA, valor sin ocupar]
        sim.ListaUsuariosuRLLC.append([i, h, 0, .2, False, 0, 0, 0])

    for j in range (int(sim.U), int(sim.U + sim.M)):
        d = mth.sqrt(np.random.uniform(0, 1) * (sim.r_cell ** 2))
        ple = 3
        rayleighGain = random.expovariate(1)
        h = ( d ** (-ple) ) * rayleighGain
        # Listausuarios = [Id, ganancia_canal, tasa_transmision bps, potencia watts, (variable booleana de asignacion a grupo NOMA), id_grupoNOMA, rango_grupoNOMA, valor sin ocupar]
        sim.ListaUsuariosmMTC.append([j, h, 0, .2, False, 0, 0, 0])

    # Ordenamiento de dispositivos basada en su ganancia de canal promedio(descendentemente)
    L1 = sorted(sim.ListaUsuariosmMTC, key=operator.itemgetter(1), reverse=True)
    sim.sortedListaUsuariosmMTC = L1
    L2 = sorted(sim.ListaUsuariosuRLLC, key=operator.itemgetter(1), reverse=True)
    sim.sortedListaUsuariosuRLLC = L2


# Algoritmo para el agrupamiento de dispositivos (clustering NOMA)

# Se empiezan a agrupar usuarios con una alta ganancia de canal promedio,
# en la recepción tipo SIC se decodifican primero los usuarios con una alta ganancia de canal promedio antes que los de baja ganancia  de canal promedio
# Los rangos de los dispositivos uRLLC deben ser menores que los MTC para que sea eficiente la decodificación SIC

def algoritmoAgrupamiento(sim):
    # j es la última posición de asignación de usuarios URLLC
    j = 0
    # AGRUPAMIENTO DE USUARIOS URLLC
    # Solo para grupos de 4 usuarios
    for i in range(0, int(sim.U)):
        # i corresponde al número de dispositivos uRLLC [U]

        if i < sim.C:
            # Asignar los dispositivos uRLLC a rangos bajos de los primeros grupos
            # Lista de grupos NOMA: [tipo_dispositivo, ID_dispositivo]
            # donde tipo_dispositivo =1 URLLC, tipo_dispositivo =2 MTC
            sim.NOMA_clusters.append([[1, sim.sortedListaUsuariosuRLLC[i][0]], False, False, False])
            sim.sortedListaUsuariosuRLLC[i][5] = i
            sim.sortedListaUsuariosuRLLC[i][6] = 0
            sim.sortedListaUsuariosuRLLC[i][4] = True

        else:
            # Si el número de dispositivos uRLLC [U] es mayor que el numero de grupos NOMA [C], los dispositivos sobrantes
            # serán asignados a los siguientes rangos del grupo
            sim.NOMA_clusters[j][1] = [1, sim.sortedListaUsuariosuRLLC[i][0]]
            sim.sortedListaUsuariosuRLLC[i][5] = j
            sim.sortedListaUsuariosuRLLC[i][6] = 1
            sim.sortedListaUsuariosuRLLC[i][4] = True
            j = j + 1

    # print('Indice j quedó en', j)
    sim.cerosEliminar = j
    # sim.NOMA_clusters[j][1]

    w=0
    x=0

    #Agregar ceros a lista
    for g in range(0,j):
        sim.sortedListaUsuariosmMTC.insert(0, 0)

    # AGRUPAMIENTO DE USUARIOS mMTC
    # Solo para grupos de 4 usuarios
    for i in range(j, int(sim.M)):
        # Si el número de dispositivos mMTC [M] es mayor que el numero de grupos NOMA [C], los dispositivos sobrantes
        # serán asignados a los siguientes rangos del grupo, última posición de asignación

        if i < (sim.C):
            # Asignar los dispositivos mmtc a los rangos mas bajos de los primeros grupos
            # Lista de grupos NOMA: [tipo_dispositivo, ID_dispositivo]
            # donde tipo_dispositivo =1 URLLC, tipo_dispositivo =2 MTC
            sim.NOMA_clusters[j][1] = [2, sim.sortedListaUsuariosmMTC[i][0]]
            sim.sortedListaUsuariosmMTC[i][5] = i
            sim.sortedListaUsuariosmMTC[i][6] = 1
            sim.sortedListaUsuariosmMTC[i][4] = True
            j = j + 1

        elif i < (2*sim.C):
            # Asignar los dispositivos mMTC a los siguientes rangos del grupo
            sim.NOMA_clusters[w][2] = [2, sim.sortedListaUsuariosmMTC[i][0]]
            sim.sortedListaUsuariosmMTC[i][5] = w
            sim.sortedListaUsuariosmMTC[i][6] = 2
            sim.sortedListaUsuariosmMTC[i][4] = True
            w = w + 1

        elif i < (3*sim.C):
            # Asignar los dispositivos mMTC a los siguientes rangos del grupo
            sim.NOMA_clusters[x][3] = [2, sim.sortedListaUsuariosmMTC[i][0]]
            sim.sortedListaUsuariosmMTC[i][5] = x
            sim.sortedListaUsuariosmMTC[i][6] = 3
            sim.sortedListaUsuariosmMTC[i][4] = True
            x = x + 1

        else:
            #print('Se asignaron',i, 'usuarios y eran ', sim.M, ' usuarios tipo maquina MTC' )
            break;
    # Eliminar ceros que se agregaron a lista
    del sim.sortedListaUsuariosmMTC[0:sim.cerosEliminar]


def algoritmoAsignacionRecursos(sim):
    #Inicialización
    # Potencias de dispositivos por default se inicializan a su máxima potencia
    #Suma de tasas acumulada
    sim.Ru = 0
    sim.Rm = 0
    # Conjunto de clusters de dispositivos con tasas insatisfechas
    sim.Cns = copy.deepcopy(sim.NOMA_clusters)
    # Se agrega una columna a cada cluster para
    for i in range(0, len(sim.Cns)):
        sim.Cns[i].append(1)
    #Mejor cluster que maximiza la tasa (C*)
    c_ = []
    #Tasas a satisfacer para dispositivos URLLC y mMTC
    sim.Ruth = mth.sqrt(np.random.uniform(.1, 20)) * 1e3
    sim.Rmth = mth.sqrt(np.random.uniform(.1, 2)) * 1e3

    while True:
        condicion1 = validacionTasasURLLC(sim)
        condicion2 = validacionTasasmMTC(sim)

        if (len(sim.Subportadoras) == 48) and (condicion1) and (condicion2):
            break

        #For para recorrer los 48 grupos no asignados de Cns
        for ci in range(0, len(sim.Cns)):
            #RTotal acumula las tasas de cada dispositivo por grupo y asi obtener la tasa alcanzada por grupo
            Rtotal = 0
            #Validación si es que hay grupos NOMA
            if sim.Cns[ci]:
                # For para recorrer los rangos del grupo
                for cn in range(0, sim.kmax):
                    R = 0
                    #Si es tipo URLLC
                    if sim.Cns[ci][cn][0] == 1:

                        u1 = sim.Cns[ci][cn][1]
                        u = busquedaDispositivouRLLC(u1,sim)

                        if sim.Cns[ci][sim.kmax] == 1:
                            Interferencias = calculoInterferenciauRLLC(u, sim)
                        else:
                            Interferencias=0

                        R = sim.Cns[ci][sim.kmax] * sim.BW * mth.log2(1 + (((abs(sim.sortedListaUsuariosuRLLC[u][1]) ** 2) * (sim.sortedListaUsuariosuRLLC[u][3])) / ((sim.N0 * sim.BW) + Interferencias)))
                        #Se asigna la tasa lograda a dispositivo URLLC
                        sim.sortedListaUsuariosuRLLC[u][2] = R

                    #Si es tipo mMTC
                    elif sim.Cns[ci][cn][0] == 2:

                        m1 = sim.Cns[ci][cn][1]
                        m = busquedaDispositivomMTC(m1, sim)

                        if sim.Cns[ci][sim.kmax] == 1:
                            Interferencias = calculoInterferenciamMTC(m, sim)
                        else:
                            Interferencias=0

                        R = sim.Cns[ci][sim.kmax] * sim.BW * mth.log2(1 + (((abs(sim.sortedListaUsuariosmMTC[m][1]) ** 2) * (sim.sortedListaUsuariosmMTC[m][3])) / ((sim.N0 * sim.BW) + Interferencias)))
                        #Se asigna la tasa lograda a dispositivo MTC
                        sim.sortedListaUsuariosmMTC[m][2] = R
                    Rtotal = Rtotal + R
            #Rates contiene el compendio de las tasas logradas por grupo
            sim.Rates.append([Rtotal])
        #Se escoge el mejor grupo que maximize la tasa
        c_ = sim.Rates.index(max(sim.Rates))

        # Actualizar variables
        sim.Cns[c_][sim.kmax] = 1

        sim.Sac[c_].append(max(sim.Rates))

        #sim.Sac = sim.Sac + 1
        sim.Sv = sim.Sv + 1
        #Obtener las tasas de los dispositivos mMTC y uRLLC del grupo NOMA
        tasas_de_clusterNOMA(c_, sim)
        #Actualizar potencias todos los dispositivos mMTC y uRLLC del grupo NOMA
        #actualizarPotenciasT(sim)
        actualizarPotencias(c_, len(sim.Sac[c_]), sim)

        if (sim.Ru >= sim.Ruth) and (sim.Rm >= sim.Rmth):
            #Se asigna grupo a Subportadora
            sim.Cns[c_].clear()
            sim.Subportadoras.append([c_, max(sim.Rates)])


#        ********** SEGUNDA PARTE DEL ALGORITMO, AÚN SIN IMPLEMENTAR **********
#
#        if (sim.Ru >= sim.Ruth) and (sim.Rm >= sim.Rmth):
#
#            for k in range(len(sim.Subportadoras), sim.S):
#                sim.Rates = []
#
#                for ci in range(0, len(sim.Cns)):
#                    Rtotal = 0
#                    if sim.Cns[ci]:
#                        for cn in range(0, sim.kmax):
#                            R = 0
#                            if sim.Cns[ci][cn][0] == 1:
#
#                                u1 = sim.Cns[ci][cn][1]
#                                u = busquedaDispositivouRLLC(u1, sim)
#
#                                if sim.Cns[ci][sim.kmax] == 1:
#                                    Interferencias = calculoInterferenciauRLLC(u, sim)
#                                else:
#                                    Interferencias = 0
#
#                                R = sim.Cns[ci][sim.kmax] * sim.BW * mth.log2(1 + (((abs(sim.sortedListaUsuariosuRLLC[u][1]) ** 2) * (sim.sortedListaUsuariosuRLLC[u][3])) / ((sim.N0 * sim.BW) + Interferencias)))
#                                sim.sortedListaUsuariosuRLLC[u][2] = R
#
#                            elif sim.Cns[ci][cn][0] == 2:
#
#                                m1 = sim.Cns[ci][cn][1]
#                                m = busquedaDispositivomMTC(m1, sim)
#
#                                if sim.Cns[ci][sim.kmax] == 1:
#                                    Interferencias = calculoInterferenciamMTC(m, sim)
#                                else:
#                                    Interferencias = 0
#
#                                R = sim.Cns[ci][sim.kmax] * sim.BW * mth.log2(1 + (((abs(
#                                    sim.sortedListaUsuariosmMTC[m][1]) ** 2) * (sim.sortedListaUsuariosmMTC[m][3])) / ((sim.N0 * sim.BW) + Interferencias)))
#                                sim.sortedListaUsuariosmMTC[m][2] = R
#
#                            Rtotal = Rtotal + R
#                sim.Rates.append([Rtotal])
#                # sim.Sac = sim.Sac + 1
#                sim.Sv = sim.Sv + 1
#                actualizarPotencias(c_, len(sim.Sac[c_]), sim)

# Validación que las tasas de dispositivos URLLC esten satisfechas de acuerdo con un umbral Ruth
def validacionTasasURLLC(sim):
    for Ru in range(0, len(sim.sortedListaUsuariosuRLLC)):
        if ((sim.sortedListaUsuariosuRLLC[Ru][2]) < (sim.Ruth)):
            return False
    return True

# Validación que las tasas de dispositivos mMTC esten satisfechas de acuerdo con un umbral Rmth
def validacionTasasmMTC(sim):
    for Rm in range(0, len(sim.sortedListaUsuariosmMTC)):
        if ((sim.sortedListaUsuariosmMTC[Rm][2]) < (sim.Rmth)):
            return False
    return True


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

#Calcula la Interferencia de los dispositivos del grupo NOMA para un dispositivo URLLC
def calculoInterferenciauRLLC(u,sim):
    Int1 = 0
    Int2 = 0
    for i in range(0, len(sim.sortedListaUsuariosuRLLC)):
        if (sim.sortedListaUsuariosuRLLC[i][6] > sim.sortedListaUsuariosuRLLC[u][6]) and (sim.sortedListaUsuariosuRLLC[u][5] == sim.sortedListaUsuariosuRLLC[i][5]):
            I = (( abs( sim.sortedListaUsuariosuRLLC[i][1] )**2 ) * ( sim.sortedListaUsuariosuRLLC[i][3] ))
            Int2 = Int2 + I

    for i in range(0, len(sim.sortedListaUsuariosmMTC)):
        if (sim.sortedListaUsuariosmMTC[i][6] >= sim.sortedListaUsuariosuRLLC[u][6]) and (sim.sortedListaUsuariosuRLLC[u][5] == sim.sortedListaUsuariosmMTC[i][5]):
            I = (( abs( sim.sortedListaUsuariosmMTC[i][1] )**2 ) * ( sim.sortedListaUsuariosmMTC[i][3] ))
            Int1 = Int1 + I

    Int3 = Int1 + Int2
    return Int3

#Calcula la Interferencia de los dispositivos del grupo NOMA para un dispositivo MTC
def calculoInterferenciamMTC(m,sim):
    # URLLC no interfieren a los mMTC, por que estos tienen rangos mas altos
    Int = 0
    for i in range(0, len(sim.sortedListaUsuariosmMTC)):
        if (sim.sortedListaUsuariosmMTC[i][6] > sim.sortedListaUsuariosmMTC[m][6]) and (sim.sortedListaUsuariosmMTC[m][5] == sim.sortedListaUsuariosmMTC[i][5]):
            I = (( abs( sim.sortedListaUsuariosmMTC[i][1] )**2 ) * ( sim.sortedListaUsuariosmMTC[i][3] ))
            Int = Int + I
    return Int

def actualizarPotenciasT(sim):
    for i in range (0,len(sim.sortedListaUsuariosuRLLC)):
        sim.sortedListaUsuariosuRLLC[i][3] = sim.sortedListaUsuariosuRLLC[i][3] / (sim.Sac + 1)
    for i in range (0,len(sim.sortedListaUsuariosmMTC)):
        sim.sortedListaUsuariosmMTC[i][3] = sim.sortedListaUsuariosmMTC[i][3] / (sim.Sac + 1)

def actualizarPotencias(cluster, Sac, sim):
    for i in range (0, sim.kmax):
        if sim.Cns[cluster][i][0] == 1:
            a = busquedaDispositivouRLLC(sim.Cns[cluster][i][1], sim)
            sim.sortedListaUsuariosuRLLC[a][3] = sim.sortedListaUsuariosuRLLC[a][3]/( Sac + 1 )
        elif sim.Cns[cluster][i][0] == 2:
            b = busquedaDispositivomMTC(sim.Cns[cluster][i][1], sim)
            sim.sortedListaUsuariosmMTC[b][3] = sim.sortedListaUsuariosmMTC[b][3]/( Sac + 1 )

def tasas_de_clusterNOMA(cluster, sim):
    for i in range (0, sim.kmax):
        if sim.Cns[cluster][i][0] == 1:
            a = busquedaDispositivouRLLC(sim.Cns[cluster][i][1], sim)
            R1 = sim.sortedListaUsuariosuRLLC[a][2]
            sim.Ru = sim.Ru + R1
        elif sim.Cns[cluster][i][0] == 2:
            b = busquedaDispositivomMTC(sim.Cns[cluster][i][1], sim)
            R2 = sim.sortedListaUsuariosmMTC[b][2]
            sim.Rm = sim.Rm + R2


sim = Simulacion()
#radio de la celula
sim.r_cell = 500
sim.umbralArribos = 200   #192 Usuarios para que no sobren usuarios
formacionUsuarios(sim)
algoritmoAgrupamiento(sim)
algoritmoAsignacionRecursos(sim)