import csv

filew = open('train.csv', 'w')
filer = open('try1.csv', 'r')

reader = csv.reader(filer)
writer = csv.writer(filew)

def process(array):
	temp = []
	a = 0
	for i in array:
		if a == 84:
			temp.append(i)
		else:
			if i.isdigit():
				temp.append(int(i) / 100)
			else:
				temp.append(i)
		a += 1
	return temp

for lines in reader:
	writer.writerow(process(lines))

filew.close()
filer.close()
