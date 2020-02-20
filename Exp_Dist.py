import numpy as np;  # NumPy package for arrays, random number generation, etc
import matplotlib.pyplot as plt  # for plotting
import random
from scipy.stats import expon


rep=100000
Lambda=1
numbPointsTotal=[]

for i in range(1,rep):
    # Simulate Poisson point process
    numbPoints = random.expovariate(Lambda)

    numbPointsTotal.append(numbPoints)

    # Plotting
    #plt.scatter(xx, yy, edgecolor='b', facecolor='b', alpha=0.5, marker=".");
    #plt.xlabel("x");
    #plt.ylabel("y");
    #plt.axis('equal');
    #plt.show()

# Graficando Exponencial
exponencial = expon()
x = np.linspace(exponencial.ppf(0.01),
                exponencial.ppf(0.99), 100)
fp = exponencial.pdf(x) # Función de Probabilidad
plt.plot(x, fp, label="Función de densidad de probabilidad (pdf)")
plt.title('Distribución Exponencial representando ganancias de desvanecimiento tipo Rayleigh en potencia')
plt.ylabel('Probabilidad')
plt.xlabel('Valores')
plt.hist(numbPointsTotal, density=True, bins=150, label="Histograma")
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper right', borderaxespad=0.)
plt.show()