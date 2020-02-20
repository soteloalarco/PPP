import numpy as np;  # NumPy package for arrays, random number generation, etc
import matplotlib.pyplot as plt  # for plotting
from scipy.stats import poisson
import random

# Simulation window parameters
r = 10;  # radius of disk
xx0 = 0;
yy0 = 0;  # centre of disk
areaTotal = np.pi * r ** 2;  # area of disk

# Point process parameters
lambda0 = 20/areaTotal;  # intensity (ie mean density) of the Poisson process
rep=10000
#np.random.seed(1)

numbPointsTotal=[]
for i in range(1,rep):
    # Simulate Poisson point process
    numbPoints = np.random.poisson(lambda0 * areaTotal);  # Poisson number of points
    theta = 2 * np.pi * np.random.uniform(0, 1, numbPoints);  # angular coordinates
    rho = r * np.sqrt(np.random.uniform(0, 1, numbPoints));  # radial coordinates

    # Convert from polar to Cartesian coordinates
    xx = rho * np.cos(theta);
    yy = rho * np.sin(theta);

    # Shift centre of disk to (xx0,yy0)
    xx = xx + xx0;
    yy = yy + yy0;

    numbPointsTotal.append(numbPoints)

    # Plotting
    #plt.scatter(xx, yy, edgecolor='b', facecolor='b', alpha=0.5, marker=".");
    #plt.xlabel("x");
    #plt.ylabel("y");
    #plt.axis('equal');
    #plt.show()

mu =  20 # parametro de forma
poisson = poisson(mu) # Distribución
x = np.arange(poisson.ppf(0.01),
              poisson.ppf(0.99))
fmp = poisson.pmf(x) # Función de Masa de Probabilidad
plt.plot(x, fmp, '--',  label="Función Masa de probabilidad (pmf)")
plt.title('Distribución Poisson con mu='+str(mu))
plt.ylabel('Probabilidad')
plt.xlabel('Valores')
plt.hist(numbPointsTotal, density=True, bins=35, label="Histograma")
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper right', borderaxespad=0.)
plt.show()