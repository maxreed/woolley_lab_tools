# max reed
# may 6, 2024
# a good copy of the script i wrote to help determine the identities of peaks seen on mass spectra corresponding to partially degraded proteins.

import numpy as np

# uncomment the relevant line depending on what protein cofactor is. add more lines if needed.
# 1. no cofactor
#cofactorNetMass = 0
# 2. biotinylated protein
#cofactorNetMass = 244.31 - 18.02
# 3. p-coumaric acid chromophore
#cofactorNetMass = 164.05 - 18.02
# 4. phycocyanobillin chromophore
cofactorNetMass = 586.69
# 5. custom cofactor (change this to whatever you want)
#cofactorNetMass = 0

massToFind = 18906.20 # enter the mass you're trying to find here.
N15_eff = 0.0 # N15 labelling efficiency (can be calculated from the mass of the intact protein by MS). set to 0 for non-isotopically enriched samples.
errorTolerance = 1.0 # i often start with a larger value like 3, but you can start with 1 if the spectrum is clean (ESI mass spectra often are clean).

N15_mass_diff = 15.0-14.0067 # average difference in mass from adding a single nitrogen 15.
forEndGroups = 18.02 # need this because all the masses are for residues and don't include the extra atoms at the N and C termini.

# read in the protein sequence. note that one must update proteinSequence.txt every time you analyze a new spectrum.
sequenceReader = open('proteinSequence.txt')
sequence = sequenceReader.readline()
lenSequence = len(sequence)
sequenceReader.close()

# read in the amino acid masses. residue_masses_numN.txt does not need to be updated (unless working with unnatural AA).
aminoAcidReader = open('residue_masses_numN.txt')
aminoAcidInfo = [] # this'll have name, typical mass, and number of nitrogens
numAA = 20 # if for some reason you modify residue_masses_numN.txt to add unnatural amino acids, update this.
for i in range(numAA):
	newLine = aminoAcidReader.readline()
	aminoAcidInfo.append(newLine.split())
	# cast the mass to a float and the number of nitrogens to an integer.
	aminoAcidInfo[i][1] = float(aminoAcidInfo[i][1])
	aminoAcidInfo[i][2] = int(aminoAcidInfo[i][2])

# make a dictionary, with the single-letter amino acid code as the key and the mass as the value.
residueMasses = {}
for i in range(numAA):
	# note that here we modify mass if we have an N15-labelled sample.
	residueMasses[aminoAcidInfo[i][0]] = aminoAcidInfo[i][1] + aminoAcidInfo[i][2] * N15_eff * N15_mass_diff

# add in a dummy residue with mass 0 at the end. this will help with referencing indices.
massPerResidue = np.zeros(lenSequence+1)
for i in range(lenSequence):
	thisResidue = sequence[i]
	massPerResidue[i] = residueMasses[thisResidue]

# some initial terminal output.
print("Untruncated mass:\t" + str(np.sum(massPerResidue)+cofactorNetMass+forEndGroups))
print("Mass Input:\t\t" + str(massToFind))

# these first two variables are indices for the start and end of the protein segment we are considering.
takeFromEnd = -1
takeFromStart = 0
# initialize the variable 
massFound = -1
repetitions = 0 # note that we search until we find a solution. the repetitions variable prevents the program from running forever by limiting it to 1000 attempts to find mass.

# start by hacking away at the N terminal.
while (np.abs(massFound-massToFind)>errorTolerance and repetitions<1000): # loop until we find a mass within our error tolerance.
	massFound = np.sum(massPerResidue[takeFromStart:takeFromEnd])+cofactorNetMass+forEndGroups # calculate the mass of the current protein fragment we're looking at.
	if massFound>(massToFind+errorTolerance): # do this if the mass we found is too large.
		takeFromStart = takeFromStart + 1 # remove 1 AA from the N terminus in the fragment we're considering.
	elif massFound<(massToFind-errorTolerance): # do this is the mass we found is too small.
		# if our mass is too small, add 1 AA to the N terminus and take 1 from the C terminus.
		takeFromStart = takeFromStart - 1
		takeFromEnd = takeFromEnd - 1
		# a safety check to make sure we aren't perpetually undershooting
		newMass = np.sum(massPerResidue[takeFromStart:takeFromEnd])+cofactorNetMass+forEndGroups
		if newMass<(massToFind-errorTolerance):
			takeFromStart = takeFromStart - 1
	# make sure takeFromEnd doesn't become positive and takeFromStart doesn't become negative.
	if takeFromEnd>-1:
		takeFromEnd=-1
	if takeFromStart<0:
		takeFromStart=0
	repetitions = repetitions + 1

print("N terminal start")
print("Mass Found:\t\t" + str(massFound))
print("Lost from N Term:\t" + str(takeFromStart))
print("Lost from C Term:\t" + str(takeFromEnd+1))

# reset the variables we use to perform the search.
takeFromEnd = -1
takeFromStart = 0
massFound = -1
repetitions = 0

# very similar to the above section of code but we begin by removing amino acids from the C terminus instead of the N terminus.
while (np.abs(massFound-massToFind)>errorTolerance and repetitions<1000):
	massFound = np.sum(massPerResidue[takeFromStart:takeFromEnd])+cofactorNetMass+forEndGroups
	if massFound>(massToFind+errorTolerance):
		takeFromEnd = takeFromEnd - 1 # remove 1 AA from the C terminus in the fragment we're considering.
	elif massFound<(massToFind-errorTolerance):
		# if our mass is too small, add 1 AA to the C terminus and take 1 from the N terminus.
		takeFromStart = takeFromStart + 1
		takeFromEnd = takeFromEnd + 1
		newMass = np.sum(massPerResidue[takeFromStart:takeFromEnd])+cofactorNetMass+forEndGroups
		if newMass<(massToFind-errorTolerance):
			takeFromEnd = takeFromEnd + 1
	if takeFromEnd>-1:
		takeFromEnd=-1
	if takeFromStart<0:
		takeFromStart=0
	repetitions = repetitions + 1

print("C terminal start")
print("Mass Found:\t\t" + str(massFound))
print("Lost from N Term:\t" + str(takeFromStart))
print("Lost from C Term:\t" + str(takeFromEnd+1))
