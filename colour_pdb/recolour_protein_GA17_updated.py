# i updated this on nov. 1, 2024 to make the analysis more systematic.
# this version of the script classifies NpF2164g3 residues as affected or not affected by GA17 binding.
# old version of the script however does a colour ramp.
# note that i don't have a class of residues that decrease in intensity because only one does and it also shifts. so.

import numpy as np

pdbName = "NpF2164g3.B99990001"
cmd.load(pdbName + ".pdb")
cmd.alter(pdbName,"b=0.0")
cmd.hide("sticks")

found = []

scoreReader = open("Pv_ga17_updated.txt")
shift = (scoreReader.readline()).split()
while len(shift)<2:
	shift = (scoreReader.readline()).split()

# i've marked the end of the file "Pv_ga16" with an x on the final line to stop the file reader.
while not shift[0] == "x":
	if len(shift)==2:
		# parse the chemical shift value.
		this_shift = float(shift[1])
		resNum = int(shift[0])
		if this_shift==-1:
			# residues that vanish are magenta.
			found.append(resNum)
			cmd.color("magenta","resi " + str(resNum))
			cmd.show("spheres","resi " + str(resNum) + " and n. CA")
		elif this_shift==-2:
			# residues that have large decreases in intensity are blue.
			found.append(resNum)
			cmd.color("blue","resi " + str(resNum))
			cmd.show("spheres","resi " + str(resNum) + " and n. CA")
		elif this_shift==-3:
			# residue with large chemical shifts are coloured green.
			cmd.color("green","resi " + str(resNum))
			cmd.show("spheres","resi " + str(resNum) + " and n. CA")
			found.append(resNum)
		else:
			# these are things that have data but aren't affected.
			cmd.color("yellow","resi " + str(resNum))
			found.append(resNum)
	shift = (scoreReader.readline()).split()
scoreReader.close()

# colour unassigned residue white.
absentColour = "white"
for i in np.arange(1,197):
	if np.sum(i==found)==0:
		cmd.color(absentColour,"resi " + str(i))

