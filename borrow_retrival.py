import csv
import io
import re

borrowers = []
with open('borrowers.csv', 'rb') as csvfile:
	reader = csv.reader(csvfile, delimiter=',')
	first_line = True
	for row in reader:
		if(first_line):
			first_line = False
			continue
		borrowers.append([row[0], re.sub("[^0-9]", "", row[1]), row[2], row[3], row[4], row[5], row[6], row[7], re.sub("[^0-9]", "", row[8])])
with io.open('normalized_data/borrower.csv', 'wb') as csvfile:
	wr = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
	for borrower in borrowers:
		wr.writerow(borrower)