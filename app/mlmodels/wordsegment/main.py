import os
import sys
import wordsegment

wordsegment.load()

try:
	os.chdir(sys.argv[0].split("/main.py")[0])
except:
	print("failed to change dir")

print('Ready')
while True:
	res = str(input())
	inp = res.strip().upper()
	if (inp != 'Exit'):
		temp = wordsegment.segment(inp)
		if temp:
			print(", ".join(temp))
		else:
			print(inp)
	else:
		break
