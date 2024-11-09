# max reed
# april 18, 2024
# this script takes a protein sequence and adds numbering in an aesthetically pleasing way. i originally wrote this
# to help me with the supplemental of the phi_switching paper, for which we included about 20 different protein sequences
# and manually annotating them with markers of position would have been a pain.

# note that i coded this so that the "0" in "10" overlaps with the 10th residue (and the "0" in "20" with the 20th residue, etc.).

# i advise taking this and then pasting it into your document of interest in a monospaced font like Courier New.

# don't worry about the stuff in the loops below, just paste your sequence in here and run the code.
sequence =  'MRGSHHHHHHGSGEFLATTLERIEKNFVITDPRLPDNPIIFASDSFLQLTEYSREEILGRNCRFLQGPETDRATVRKIRDAIDNQTEVTVQLINYTKSGKKFWNVFHLQPMRDYKGDVQYFIGVQLDGTERLHGAAEREAVMLIKKTAFQIAEAANDENYF'
annotation = ''

# you can adjust this based on how many characters you want on a line. this is the only other part of this program except the
# sequence you may want to adjust. 66 gives 60 amino acids per line (it adds 10 AA plus one space character at a time). 
lineLength = 66

# the variable thisLabel is essentially a counter that keeps track of where in the sequence we're printing.
thisLabel = 10

seq_len = len(sequence)

# this part of the code constructs the "label line", which contains only spaces and a count of which amino acid we've printed up to.
while thisLabel<seq_len:
	# looking for the length of the label in characters.
	thisLabel_len = len(str(thisLabel))
	# add in an appropriate number of space characters.
	for i in range(10-thisLabel_len):
		annotation = annotation + ' '
	# add the number. the last digit of the number is over the position the number corresponds to.
	annotation = annotation + str(thisLabel)
	# need to add another space every 10 AA
	annotation = annotation + ' '
	thisLabel = thisLabel + 10


# this bit of the code makes the amino acid sequence we print. all it does is add a spaces after every 10 amino acids.
sequence_with_spaces = ''
lengthCovered = 0
while lengthCovered < seq_len:
	if (lengthCovered+10)<seq_len:
		sequence_with_spaces = sequence_with_spaces + sequence[lengthCovered:lengthCovered+10] + ' '
	else:
		sequence_with_spaces = sequence_with_spaces + sequence[lengthCovered:]
	lengthCovered = lengthCovered + 10

# this prints the actual output. it increments its way through the two strings we made above.
lengthPrinted = 0
while lengthPrinted < len(sequence_with_spaces):
	if (lengthPrinted+lineLength)<len(sequence_with_spaces):
		print(annotation[lengthPrinted:lengthPrinted+lineLength])
		print(sequence_with_spaces[lengthPrinted:lengthPrinted+lineLength])
		print("")
	else:
		print(annotation[lengthPrinted:])
		print(sequence_with_spaces[lengthPrinted:])
	lengthPrinted = lengthPrinted + lineLength

