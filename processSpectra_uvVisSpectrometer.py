# max reed
# april 2, 2024
# this is a better version of my script for reading in spectra files. the only required user input necessary is a starting string to sort
# which files in the present directory you want to look at (if you don't do this, all .SP files get read in), and the identity of a wavelength
# to zero at. the former is on line 82, the latter on line 96. comment out line 99 if you don't want to zero at any wavelength.
# NOTE: in theory by adjusting the readSpectrumFile function alone, you can make this work with ANY output text file containing spectra.

import os
#import matplotlib.pyplot as plt

class Spectrum:
	def __init__(self, name, time, date, wavelengths,absorbances):
		self.name = name
		self.time = time
		self.date = date
		self.wavelengths = wavelengths
		self.absorbances = absorbances
		# when the spectrum is read in, automatically calculate the timestamp in minutes (since the start of the month).
		hour = float(self.time[:2])
		minute = float(self.time[3:5])
		second = float(self.time[6:8])
		day = float(self.date[-2:])
		self.time_mins = day * 24 * 60 + hour*60 + minute + second/60
	def zeroAbsorbance(self,wavelengthToZeroAt): # zeros the spectrum at a wavelength of interest.
		canZero = False
		indexOfZeroWavelength = 0
		for i in range(len(self.wavelengths)):
			if self.wavelengths[i] == wavelengthToZeroAt:
				canZero = True
				indexOfZeroWavelength = i
		if (canZero):
			absorbanceToSubtract = self.absorbances[indexOfZeroWavelength]
			for j in range(len(self.absorbances)):
				self.absorbances[j] = self.absorbances[j] - absorbanceToSubtract
		else:
			print("Cannot zero spectrum " + self.name + " at the wavelength " + str(wavelengthToZeroAt) + " nm. This discrete wavelength isn't in the spectrum.")
	def findAbsorbance(self,wavelengthToFind):
		isPresent = False
		indexOfWavelength = 0
		for i in range(len(self.wavelengths)):
			if self.wavelengths[i] == wavelengthToFind:
				isPresent = True
				indexOfWavelength = i
		if isPresent:
			return self.absorbances[indexOfWavelength]
		else:
			return 0 # it seems suitable to me to return 0 if a spectrum doesn't have an absorbance at a particular wavelength. makes it easy for graphing.


def readSpectrumFile(fileName):
	# this first bit is hard coded. i rely on the file having three lines, then a line with the day, then a line with
	# the time, then 81 lines with other random stuff, then after that the spectrum. as far as i can tell this is constant.
	thisFile = open(fileName)
	for k in range(3):
		thisFile.readline()
	thisDay = thisFile.readline().split()
	thisTime = thisFile.readline().split()
	time_thisFile = thisTime[0]
	day_thisFile = thisDay[0]
	for k in range(81):
		thisFile.readline()
	# now we read the spectrum. we won't assume any particular spectrum length.
	readSpectrum = True
	wavelengths_thisFile = []
	absorbances_thisFile = []
	while(readSpectrum):
		thisLine = thisFile.readline()
		if len(thisLine)<3:
			readSpectrum=False
		else:
			entries = thisLine.split()
			wavelengths_thisFile.append(float(entries[0]))
			absorbances_thisFile.append(float(entries[1]))
	# within this function, i generate a Spectrum object for the file being read in. not sure if this is good practice, but it avoids having to pass
	# the variables necessary for making the object back from this function.
	thisSpectrum = Spectrum(fileName,time_thisFile,day_thisFile,wavelengths_thisFile,absorbances_thisFile)
	return thisSpectrum

# determine the spectrum (.SP) files in the directory with our desired prefix.
dir_list = os.listdir('.')
prunedList = []
required_name_start = "TIOL"
required_name_end = ".SP"
for file in dir_list:
	if len(file)>3:
		nameLength = len(required_name_start)
		endLength = len(required_name_end)
		fileStart = file[:nameLength]
		fileEnd = file[-endLength:]
		if fileStart == required_name_start and fileEnd == required_name_end:
			prunedList.append(file)
numSpectraFiles = len(prunedList)

# read in all the spectra as objects.
allSpectraObjects = []
wavelengthToZeroAt = 550.0
for file in prunedList:
	allSpectraObjects.append(readSpectrumFile(file))
	allSpectraObjects[-1].zeroAbsorbance(wavelengthToZeroAt)
# 	testWavelengths = allSpectraObjects[-1].wavelengths
# 	testAbsorbances = allSpectraObjects[-1].absorbances
# 	plt.plot(testWavelengths,testAbsorbances)
# plt.show()

# sort the spectra by their timestamps
sortedID = 0
while (sortedID<(numSpectraFiles-1)):
	if allSpectraObjects[sortedID].time_mins<allSpectraObjects[sortedID+1].time_mins:
		# if the sample with the earlier timestamp comes first, proceed to the next sample.
		sortedID = sortedID + 1
	else:
		# swap the objects in the list if they're out of order, and restart. this is a very inefficient but very simple sorting algorithm.
		transferObject = allSpectraObjects[sortedID]
		allSpectraObjects[sortedID] = allSpectraObjects[sortedID+1]
		allSpectraObjects[sortedID+1] = transferObject
		sortedID = 0

# zero the times
zeroTime = allSpectraObjects[0].time_mins
for i in range(len(allSpectraObjects)):
	allSpectraObjects[i].time_mins = allSpectraObjects[i].time_mins - zeroTime

# find all wavelengths reported.
allWavelengths = []
for i in range(len(allSpectraObjects)):
	these_wavelengths = allSpectraObjects[i].wavelengths
	for entry in these_wavelengths:
		if not entry in allWavelengths:
			allWavelengths.append(entry)

# sort the wavelengths from lowest to highest
sortedID = 0
while (sortedID<(len(allWavelengths)-1)):
	if allWavelengths[sortedID]<allWavelengths[sortedID+1]:
		# if the sample with the lower wavelength comes first, proceed to the next sample.
		sortedID = sortedID + 1
	else:
		# swap the wavelengths in the list if they're out of order, and restart. this is a very inefficient but very simple sorting algorithm.
		transferObject = allWavelengths[sortedID]
		allWavelengths[sortedID] = allWavelengths[sortedID+1]
		allWavelengths[sortedID+1] = transferObject
		sortedID = 0

# make the output file.
outputFileName = required_name_start + "_allWavelengths.txt"
outputWriter = open(outputFileName,"w") # this makes a new file if one doesn't exist. it also overwrites any content if a file does exist.

# make headings containing the file names
outputWriter.write("File Names\t")
for i in range(numSpectraFiles):
	outputWriter.write(str(allSpectraObjects[i].name) + "\t")
outputWriter.write("\n")

# make the column headings. the leftmost is the label saying the leftmost column is wavelengths, the others are the timestamps of the spectra.
outputWriter.write("Wavelength (nm)\t")
for i in range(numSpectraFiles):
	outputWriter.write(str(allSpectraObjects[i].time_mins) + "\t")
outputWriter.write("\n")

# write the output spectra (finally!). note that here i individually check if each spectrum has an absorbance for the wavelength being printed. as you
# can see above in the Spectrum class's findAbsorbance function, you get 0 returned if the spectrum doens't have an absorbance at the wavelength of interest.
for i in range(len(allWavelengths)):
	thisWavelength = allWavelengths[i]
	outputWriter.write(str(thisWavelength) + "\t")
	for j in range(numSpectraFiles):
		outputWriter.write(str(allSpectraObjects[j].findAbsorbance(thisWavelength)) + "\t")
	outputWriter.write("\n")

outputWriter.close()
print("Successfully processed " + str(numSpectraFiles) + " spectra files.")
