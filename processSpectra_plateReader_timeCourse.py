# max reed
# april 2, 2024
# this is a better version of my script for reading in spectra files. the only required user input necessary is a starting string to sort
# which files in the present directory you want to look at (if you don't do this, all .SP files get read in), and the identity of a wavelength
# to zero at. the former is on line 82, the latter on line 96. comment out line 99 if you don't want to zero at any wavelength.
# NOTE: in theory by adjusting the readSpectrumFile function alone, you can make this work with ANY output text file containing spectra.
# may 15, 2024: modified to work with text files output from the plate reader.
# SPECIFICALLY this is for when you have a single run and have exported multiple timepoint spectra as individual files.
# ... this is only a necessary script because trying to export multiple spectra simultaneously crashes the plate reader computer ...

import os
#import matplotlib.pyplot as plt

class Spectrum:
	def __init__(self, name, time, timeToAdd, date, wavelengths,absorbances):
		self.name = name
		self.time = time
		self.timeToAdd = timeToAdd
		self.date = date
		self.wavelengths = wavelengths
		self.absorbances = absorbances
		self.date_time = self.date + ", " + self.time
		# here's the time the measurement started
		hour = float(self.time[-13:-11])
		minute = float(self.time[-10:-8])
		second = float(self.time[-7:-5])
		day = float(self.date[-2:])
		# now we also process the time since the start of the experiment

		if len(self.timeToAdd)<2:
			timeSinceStart = 0 # only happens for the zero time point.
		else:
			hourSinceStart = float(self.timeToAdd[:2])
			minuteSinceStart = float(self.timeToAdd[3:5])
			secondSinceStart = float(self.timeToAdd[6:])
			timeSinceStart = hourSinceStart * 60 + minuteSinceStart + secondSinceStart / 60
		self.time_mins = day * 24 * 60 + hour * 60 + minute + second / 60 + timeSinceStart
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
	# this first bit is hard coded. i rely on the file having one lines, then a line with date and time, then four blank lines,
	# then a line with the wavelength, then a line with the absorbances.
	thisFile = open(fileName)
	for k in range(1):
		thisFile.readline()
	dateTimeInfo = thisFile.readline().split(",") # this is a CSV, so we split by comma.
	time_thisFile = dateTimeInfo[2]
	day_thisFile = dateTimeInfo[1]
	for k in range(4):
		thisFile.readline()
	# now we read the spectrum. we won't assume any particular spectrum length.
	readSpectrum = True
	wavelengths_thisFile = []
	absorbances_thisFile = []

	time_line = thisFile.readline().split(",") # only need this one for timeseries reads, otherwise this line doesn't exist.
	timeSoFar = time_line[3]
	wavelength_line = thisFile.readline().split(",")
	absorbances_line = thisFile.readline().split(",")

	# this excludes the first 2 entries and the last entry, which are info / placeholders.
	for entryNum in range(2,len(wavelength_line)-1):
		wavelengths_thisFile.append(float(wavelength_line[entryNum]))
		absorbances_thisFile.append(float(absorbances_line[entryNum]))
	# within this function, i generate a Spectrum object for the file being read in. not sure if this is good practice, but it avoids having to pass
	# the variables necessary for making the object back from this function.
	thisSpectrum = Spectrum(fileName,time_thisFile,timeSoFar,day_thisFile,wavelengths_thisFile,absorbances_thisFile)
	return thisSpectrum

# determine the spectrum (.SP) files in the directory with our desired prefix.
dir_list = os.listdir('.')
prunedList = []
required_name_start = ""
required_name_end = ".TXT"
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
wavelengthToZeroAt = 800.0
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
