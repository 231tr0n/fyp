import os
import sys
import spellchecker

spell_checker = spellchecker.SpellChecker()

try:
	os.chdir(sys.argv[0].split("/main.py")[0])
except:
	print("failed to change dir")

print('Ready')
while True:
	res = str(input())
	inp = res.strip().upper()
	if (inp != 'Exit'):
		temp = spell_checker.correction(inp)
		if temp:
			print(temp.upper())
		else:
			print(inp)
	else:
		break
