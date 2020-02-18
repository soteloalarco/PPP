import numpy as np;  # NumPy package for arrays, random number generation, etc
import matplotlib.pyplot as plt  # for plotting
import random
from scipy.stats import expon


rep=1000000
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
plt.plot(x, fp)
plt.title('Distribución Exponencial')
plt.ylabel('probabilidad')
plt.xlabel('valores')
plt.hist(numbPointsTotal, density=True, bins=150)
plt.show()