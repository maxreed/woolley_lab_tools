# max reed
# december 28 2024
# a custom script for adding the extra chemical shifts known for GAF6 Pg to the star file.
# when using CARA, not all shifts are exported (specifically, the i-1 position shifts are
# not used). i wrote a script to export all shifts in CARA, but not being very comfortable
# in lua, i decided to do the final processing in python.

# this writes the first three positions in a star file line, following spacing conventions.
def writeStartOfLine(thisShiftNum,thisResNum):
	line = ""
	thisShiftNumLen = len(str(thisShiftNum))
	thisResNumLen = len(str(thisResNum))
	for j in range(10-thisShiftNumLen):
		line = line + " "
	line = line + str(thisShiftNum)
	for k in range(2): # for some reason we write residue number twice.
		for k2 in range(5-thisResNumLen):
			line = line + " "
		line = line + str(thisResNum)
	return line

# helps fill in residue identities at the -1 positions.
def getMinus1Residue(residueDictionary,queryRes):
	if queryRes in residueDictionary:
		return residueDictionary[queryRes]
	else:
		return "xxx"

str_initial = open("gaf6_Pg_v6")
shiftFile = open("GAF6_Pg_allShifts.txt")
str_final = open("gaf6_Pg_v6_mod",'r+')

for i in range(11):
	thisLine = str_initial.readline()
	str_final.write(thisLine)

# i'm only really interested in the -1 positions, since those weren't used by CARA.
CA_minus1_shifts = {}
C_minus1_shifts = {}
# i'm hard coding in the number of systems.
for i in range(177):
	systemLine = shiftFile.readline()
	systemNum = systemLine.split("\t")[1]
	residueLine = shiftFile.readline()
	residueNum = int(residueLine.split("\t")[1])

	nextLine = shiftFile.readline()
	while(len(nextLine)>2):
		entries = nextLine.split("\t")
		atomID = entries[0]
		thisShift = entries[1]
		# in each case taking a number of characters that will give 3 decimal places.
		if atomID == 'C-1':
			C_minus1_shifts[residueNum] = thisShift[:7]
		elif atomID == 'CA-1':
			CA_minus1_shifts[residueNum] = thisShift[:6]
		nextLine = shiftFile.readline()

# now that we extracted the C and CA -1 shifts, we have to put them into the star file.
# this will need some manual editing, since i have no residue identity info. if i find a
# C-1 or CA-1 shift for a residue that has no name, i'll need to put in some new lines
# with a placeholder residue identity i fill in later.

# i'm doing the first line manually so i can get a value for currentResidue.
shiftNum = 1 # this is what goes in printed column 1. i'll be counting myself as i'm adding
	# lots of shifts, so the original numbers won't work.
thisLine = str_initial.readline()
entries = thisLine.split()
currentResidue = int(entries[1]) # technically, could also be entries[2].
str_final.write(thisLine)

has_CA = [currentResidue] # this will be a list of all residues with a CA shift reported.
	# note that since i'm doing the first entry manually, i have to add it here manually.

residueTypes = {} # also keeping track of each residue's identity for convenience.

thisLine = str_initial.readline()
while len(thisLine)>8:
	entries = thisLine.split()
	shiftNum = shiftNum + 1
	thisResidue = int(entries[1])

	# this is the core of the program. beyond this, we're basically copying the initial file.
	if thisResidue>currentResidue:
		# search for shifts at the -1 position.
		if (thisResidue in CA_minus1_shifts):
			# write out the CA-1 value IF we don't already have one.
			if not (thisResidue-1) in has_CA:
				lineToWrite = writeStartOfLine(shiftNum,thisResidue-1)
				lineToWrite = lineToWrite + "   " + getMinus1Residue(residueTypes,thisResidue-1)
				lineToWrite = lineToWrite + "  CA    C  "
				lineToWrite = lineToWrite + CA_minus1_shifts[thisResidue] + " 0.3     1    \n"
				str_final.write(lineToWrite)
				shiftNum = shiftNum + 1 # because we added another shift.
		if (thisResidue in C_minus1_shifts):
			# write out the C-1 value.
			lineToWrite = writeStartOfLine(shiftNum,thisResidue-1)
			lineToWrite = lineToWrite + "   " + getMinus1Residue(residueTypes,thisResidue-1)
			lineToWrite = lineToWrite + "  C     C "
			lineToWrite = lineToWrite + C_minus1_shifts[thisResidue] + " 0.3     1    \n"
			str_final.write(lineToWrite)
			shiftNum = shiftNum + 1 # because we added another shift.
	
	# this ensures that C and CA are only written for the -1 position once.
	currentResidue = thisResidue

	# keep track of which residues we have CA values for and what residue identities we have.
	if not thisResidue in residueTypes:
		residueTypes[thisResidue] = entries[3]
	shiftType = entries[4]
	if shiftType == "CA":
		has_CA.append(thisResidue)

	# now that we checked the line we just read in for residue and atom type, write it (with updated shift number).
	lineToWrite = writeStartOfLine(shiftNum,thisResidue)
	# just hard coded the index of 20 in so i don't have to reconstruct the whole line.
	lineToWrite = lineToWrite + thisLine[20:]
	str_final.write(lineToWrite)

	# go to the next line.
	thisLine = str_initial.readline()
str_final.write(thisLine)

str_initial.close()
shiftFile.close()
str_final.close()
