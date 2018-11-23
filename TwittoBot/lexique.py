#!/usr/bin/python3
# coding: utf-8
import os, io, re
from collections import defaultdict

def get_files_from_path(path, type):
		paths = []
		for subdir in os.listdir(path):
				joined_path = os.path.join(path, subdir)
				if subdir.endswith("."+type):
						paths.append(joined_path)
				elif os.path.isdir(joined_path):
						paths.extend(get_files_from_path(joined_path, type))
		return paths

def read_normalize_tokenize(file):
	text = ''
	if type(file) is list: # Si c'est une liste de tweets
		text = '\n'.join(file)
	else: # Sinon c'est un fichier
		try:
			with io.open(file, "r", encoding="utf-8") as f:
				text = f.read()
		except Exception as e: print("Erreur : " + str(e))

	text = text.lower() # Tout en minuscule
	# Suppression des URL
	text = re.sub(
		"(((https?:\/\/www\.)|(https?:\/\/)|(www\.))[A-Za-z0-9]+\.[A-Za-z]{2,3}(\/[^ \n\t\r\/]+)*)|([A-Za-z0-9]+\.[A-Za-z]{2,3}(\/[^ \n\t\r\/]+)+)", ' ', str(text))
	text = re.sub("&lt;", '<', text)  # Traitement code xml de <
	text = re.sub("&gt;", '>', text)  # Traitement code xml de >
	text = re.sub("&amp;", '&', text)  # Traitement code xml de &
	text = re.sub("[\[\]{}\"\`«»“„”¨¤§µ,_²]+", ' ', text) # Suppression des caractères inutiles
	text = re.sub("[^ ]{22}[^ ]+", ' ', text) # Suppression des mots trop longs
	text = re.sub("\?\n*", " </?>\n", text) # Traitement de ?
	text = re.sub("!\n*", " </!>\n", text) # Traitement de !
	text = re.sub("(\.( *\.)+\n*)|(…)", " </...>\n", text) # Traitement de ...
	#text = re.sub("[0-9]+([,.][0-9]+)?", " [num] ", text)  # Traitement des nombres
	text = re.sub("[\t\r ]+", ' ', text) # Traitement des blancs
	text = re.sub("\. ", '\n', text) # Retour après points
	newtext = []
	for line in text.split("\n"):
		newline = ["<s>"] # Début de ligne
		newline.extend([word for word in line.split(' ') if word != '']) # Exclusion des mots vides
		if newline[-1] == '.': # Traitement des points finaux
			del(newline[-1])
		elif newline[-1].endswith('.'): # Traitement des points en fin de mots
			newline[-1] = newline[-1][:-1]
		if newline[-1] not in ["</?>", "</!>", "</...>"]: # Exception de ? et ! et ...
			newline.append("</s>") # Fin de ligne
		if len(newline) > 2:
			newtext.append(newline)
	return newtext


def save_lexique(dico, biblio):
	path = "corpus/text_generation/n-grams/"
	os.makedirs(path, exist_ok=True)
	with io.open(path+"lexique.txt", "w", encoding="utf-8") as f:
		for ngram in sorted(dico, key=dico.get, reverse=True):
			f.write(ngram + "\t" + str(dico.get(ngram)) + "\n")
	with open(path+"biblio_lexique.txt", "w") as f:
		for text in sorted(biblio):
			f.write(text + "\n")

def load_lexique(min=1):
	path = "corpus/text_generation/n-grams/"
	dico, biblio = defaultdict(int), []
	try:
		with io.open(path+"lexique.txt", "r", encoding="utf-8") as f:
			for ngram in f:
				text = ngram[:-1].split("\t")
				if min <= int(text[1]):
					dico[text[0]] = int(text[1])
		with open(path+"biblio_lexique.txt", "r") as f:
			for text in f:
				biblio.append(text[:-1])
	except: pass
	return dico, biblio

def filter_lexique(min):
	dico, biblio = load_lexique(min)
	print("lexique.filter("+str(min)+") : terminé")
	save_lexique(dico, biblio)
	print("lexique.sort : terminé")

def genere_lexique(min=1, save=10):
	dico, biblio = load_lexique()
	files = get_files_from_path("corpus/text_generation/txt/", "txt")
	nb_files = len(files)
	for file in files:
		nb_files -= 1
		if file not in biblio:
			for line in read_normalize_tokenize(file):
				for word in line:
					dico[word] += 1
			biblio.append(file)
			print(os.path.basename(file)+" : ok !\trestant : "+str(nb_files))
		if nb_files%save == 0 and nb_files != 0 : save_lexique(dico, biblio)
	
	useless_words = ["<", "/", ">", "</", "*", ",", "|", "(", ")", "[", "]", "\"", ":"]
	for word in useless_words: # Suppression de caractères inutiles :
		if word in dico:
			del(dico[word])
	save_lexique(dico, biblio)
	print("lexique.genere : terminé")
	if min > 1: filter_lexique(min)

#genere_lexique()
