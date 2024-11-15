# max reed
# nov. 15, 2024
# i often take the half-life of many different kinetic traces. this is a script for automating that.
# the accepted input is a text file in which the left-most column is time, and every other column is a kinetic trace.
# be sure to add an extra blank line to the end of the text file (that's how it knows when to stop reading).
# put this script in the same directory as your text file, then write the text file name on line 22 of this file.
# note that i assume the kinetic traces have already undergone baseline correcttion based on a reference wavelength.

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit # note that you need scipy installed for this script (and matplotlib).

# single exponential function.
def snglExp(x,A,tau,y0):
	result = y0 - A*np.exp(-x/tau)
	return result

time_runs = []
abs_runs = []

# start reading in a file.
fileName = "processMultipleThermalRevForTau_exampleInput"
dataFile = open(fileName + ".txt")
line = dataFile.readline()
data = line.split()
numRuns = len(data)-1
for k in range(numRuns):
	abs_runs.append([])
# stops reading when it reaches an empty line.
while len(line)>2:
	time_runs.append(float(data[0]))
	for j in range(1,len(data)):
		abs_runs[j-1].append(float(data[j]))
	line = dataFile.readline()
	data = line.split()

# convert the data read in as lists to numpy arrays to make manipulating the data easier.
time_runs = np.array(time_runs)
for k in range(numRuns):
	abs_runs[k]=np.array(abs_runs[k])
	plt.plot(time_runs,abs_runs[k])
abs_runs = np.array(abs_runs)
plt.show()

y0_all = []
A_all = []
tau_all = []

x_data = time_runs
numRunsWithThisTime = len(abs_runs)
for j in range(numRunsWithThisTime):
	y_data = abs_runs[j]
	plt.scatter(x_data,y_data)
	# note that curve fitting in python needs initial guesses for all parameters. you may need to alter these.
	popt, pcov = curve_fit(snglExp,x_data,y_data,p0=(0.1,100,0.1))
	A_this = popt[0]
	tau_this = popt[1]
	y0_this = popt[2]
	y_fit = snglExp(x_data,A_this,tau_this,y0_this)
	plt.plot(x_data,y_fit)
	# i'm graphing the data and the fit here to visually assure the fit is good, though if you know it'll be good you
	# can comment out all the plt. lines.
	plt.show()
	y0_all.append(y0_this)
	A_all.append(A_this)
	tau_all.append(tau_this)

y0_all = np.array(y0_all)
A_all = np.array(A_all)
tau_all = np.array(tau_all)

# print out all the tau values (which are half life times ln(2)). this is usually the only thing i care about,
# but you can of course print the other parameters too if you want.
print(tau_all)

