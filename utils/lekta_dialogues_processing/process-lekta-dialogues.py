# from os import listdir
# from os.path import isfile, join
import os
import re

datasets_path = 'datasets/lekta_dialogues/new/'
lekta_input_path = 'datasets/lekta_dialogues/input'

pattern = '\$> .*Input.*\[\s?\d{1,3}\]: '
lang_pattern = '\$> .*Language\s*:\s*\[(\d*)\].*'

# Create/Open and rewrite files with Lekta input sentences

f_english = open(lekta_input_path + '/english.txt', 'w')
f_polish = open(lekta_input_path + '/polish.txt', 'w')
f_spanish = open(lekta_input_path + '/spanish.txt', 'w')

#dataset = "/JLPro"
#particular_folder = ''
particular_folder = '/2017/05'

for dataset in os.listdir(datasets_path):
    if dataset != 'Fluency-170301':
        continue
    else:
        print dataset
        
	root = datasets_path + dataset + "/Conversation/2017/05"
	for path, subdirs, files in os.walk(root):
		for name in files:
			full_path = os.path.join(path, name)
			if (os.path.isfile(full_path) and not name == '.DS_Store'):
				file = open(full_path)
				lang = '1'
				for line in file:
					lang_regex = re.findall(lang_pattern, line)
					if lang_regex:
						lang = lang_regex[0]
					if not re.match(pattern, line) is None:
						line = re.split(pattern, line)[1]
						line = line[:-1]
						if not line == '$exit$' and not line == '':
							line = line + '\n'
							if lang == '1':
								f_english.write(line)
							elif lang == '2':
								f_polish.write(line)
							elif lang == '3':
								f_spanish.write(line)
							else:
								print 'LANGUAGE UNKNOWN'
				file.close()

f_english.close()
f_polish.close()
f_spanish.close()
