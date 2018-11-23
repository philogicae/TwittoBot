#!/usr/bin/python3
# coding: utf-8
import os, io
from collections import defaultdict
from lexique import get_files_from_path, read_normalize_tokenize, genere_lexique

def remove_stopwords(words, stopwords):
	return [w for w in words if w not in stopwords]

def lexique():
	try:
		path = "corpus/text_generation/n-grams/"
		dico = set()
		with io.open(path+"lexique.txt", "r", encoding="utf8") as f:
			dico.update([ngram.split("\t")[0] for ngram in f])
		return dico
	except Exception as e: print("Erreur au chargement du lexique : " + str(e))

def all_words_in_lexique(words, lexique):
	for word in words:
		if word not in lexique:
			return False
	return True


def save_dicogram(nb, dico, biblio, sort=False):
	path = "corpus/text_generation/n-grams/"
	os.makedirs(path, exist_ok=True)
	with io.open(path+str(nb)+"-grams.txt", "w", encoding="utf-8") as f:
		newdico = dico
		if sort: newdico = sorted(dico, key=dico.get, reverse=True)
		for ngram in newdico:
			f.write(ngram + "\t" + str(dico[ngram]) + "\n")
	with open(path+"biblio_"+str(nb)+"-grams.txt", "w") as f:
		for text in sorted(biblio):
			f.write(text+"\n")

def load_dicogram(nb, min=1):
	path = "corpus/text_generation/n-grams/"
	dico, biblio = defaultdict(int), []
	try:
		with io.open(path+str(nb)+"-grams.txt", "r", encoding="utf-8") as f:
			for ngram in f:
				text = ngram[:-1].split("\t")
				if min <= int(text[1]):
					dico[text[0]] = int(text[1])
		with open(path+"biblio_"+str(nb)+"-grams.txt", "r") as f:
			for text in f:
				biblio.append(text[:-1])
	except: pass
	return dico, biblio

def n_grams(n, text): # Le texte doit être une liste de lignes (qui sont des listes de mots)
	ngrams = []
	for line in text:
		line = [word for word in line if word != ''] # Exclusion des mots vides
		ngrams.extend(zip(*[line[i:] for i in range(n)]))
	return ngrams

def filter_sort(nb, min=1):
	dico, biblio = load_dicogram(nb, min)
	print("dicogram("+str(nb)+").filter("+str(min)+") : terminé")
	save_dicogram(nb, dico, biblio, sort=True)
	print("dicogram("+str(nb)+").sort : terminé")

def genere_dicogram(nb, min=1, save=10):
	dico, biblio = load_dicogram(nb)
	#stopwords = set([word.strip() for word in io.open("corpus/text_generation/stopwords.txt", "r", encoding="utf-8")])
	wordlist = lexique()
	files = get_files_from_path("corpus/text_generation/txt/", "txt")
	nb_files = len(files)
	for file in files:
		nb_files -= 1
		if file not in biblio:
			if nb == "context":
				#for l in [remove_stopwords(line, stopwords) for line in read_normalize_tokenize(file)]:
				for l in read_normalize_tokenize(file):
					for x in range(len(l)-1):
						for y in range(x+1, len(l)):
							if l[x] != l[y] and all_words_in_lexique([l[x], l[y]], wordlist):
								dico[' '.join(sorted([l[x], l[y]]))] += 1
			else:
				for n_gram in n_grams(nb, read_normalize_tokenize(file)):
					if all_words_in_lexique(n_gram, wordlist):
						dico[' '.join(n_gram)] += 1
			biblio.append(file)
			print(os.path.basename(file)+" : ok !\trestant : "+str(nb_files))
			if nb_files%save == 0 : save_dicogram(nb, dico, biblio)
	print("dicogram("+str(nb)+").genere : terminé")
	if min > 1: filter_sort(nb, min)


def get_dicogram(nb):
	dico = defaultdict(int)
	try:
		with io.open("corpus/text_generation/n-grams/"+str(nb)+"-grams.txt", "r", encoding="utf-8") as f:
			for ngram in f:
				text = ngram[:-1].split("\t")
				dico[tuple(text[0].split(' '))] = int(text[1])
	except: print("Erreur : Dicogram introuvable")
	return dico

def get_context(word, nb=20, show=False):
	context, filter = get_dicogram("context"), {}
	stopwords = set([word.strip() for word in io.open("corpus/text_generation/stopwords.txt", "r", encoding="utf-8")])
	for ngram in context:
		if ngram[0] == word and ngram[1] not in stopwords:
			filter[ngram[1]] = context.get(ngram)
		elif ngram[1] == word and ngram[0] not in stopwords:
			filter[ngram[0]] = context.get(ngram)
	sort = list(sorted(filter, key=filter.get, reverse=True))
	if len(sort) > nb:
		sort = sort[:nb]
	if show:
		for x in sort:
			print(x)
	return filter


def genere_lexgram(filter0=1, filter1=1, filter2=1, filter3=1, filter4=1, save=10):
	genere_lexique(filter1, save)
	genere_dicogram(2, filter2, save)
	genere_dicogram(3, filter3, save)
	genere_dicogram(4, filter4, save)
	genere_dicogram("context", filter0, save)

def get_lexgram():
	return (get_dicogram(2), get_dicogram(3), get_dicogram(4), get_dicogram("context"))


def fastdicogram(nb, text): # text doit être une liste de phrases
	dico = defaultdict(int)
	if nb == "context":
		for l in read_normalize_tokenize(text):
			for x in range(len(l)-1):
				for y in range(x+1, len(l)):
					if l[x] != l[y]:
						dico[tuple(sorted([l[x], l[y]]))] += 1
	else :
		for n_gram in n_grams(nb, read_normalize_tokenize(text)):
			dico[tuple(n_gram)] += 1
	return dico

def fastcontext(word, text, nb=20, show=False):
	context, filter = fastdicogram("context", text), {}
	stopwords = set([word.strip() for word in io.open("corpus/text_generation/stopwords.txt", "r", encoding="utf-8")])
	for ngram in context:
		if ngram[0] == word and ngram[1] not in stopwords:
			filter[ngram[1]] = context.get(ngram)
		elif ngram[1] == word and ngram[0] not in stopwords:
			filter[ngram[0]] = context.get(ngram)
	sort = list(sorted(filter, key=filter.get, reverse=True))
	if len(sort) > nb:
		sort = sort[:nb]
	if show:
		for x in sort:
			print(x)
	return filter

def get_tweetgram(text):
	return (fastdicogram(2, text), fastdicogram(3, text), fastdicogram(4, text))


#genere_lexgram(20, 20, 10, 5, 3)
#print(fastdicogram(3, ["hello, how are you today ?", "I'm fine, and you my friend ?", "I'm fine too, thank you !"]))
#get_context("hitler", nb=10, show=True)
