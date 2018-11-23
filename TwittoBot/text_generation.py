#!/usr/bin/python3
# coding: utf-8
from random import choice, randint
from ngrams import get_lexgram, get_tweetgram

dico2 = dico3 = dico4 = dicontext = {}
end = ["</s>", "</?>", "</!>", "</...>"]

def next_word(sentence, nb_last_words):
    size = len(sentence[-1*nb_last_words:]) + 1
    if size == 2:
        return {ngram[1]: dico2.get(ngram) for ngram in dico2 if ngram[0] == sentence[-1]}
    elif size == 3:
        return {ngram[2]: dico3.get(ngram) for ngram in dico3 if ngram[0] == sentence[-2] and ngram[1] == sentence[-1]}
    elif size == 4:
        return {ngram[3]: dico4.get(ngram) for ngram in dico4 if ngram[0] == sentence[-3] and ngram[1] == sentence[-2] and ngram[2] == sentence[-1]}
    else:
        return {"</s>": 0}

def predict_sentence():
    sentence = ["<s>"]
    while sentence[-1] not in end:
        filter, nb_last_words = {}, 3
        while not filter:
            filter = next_word(sentence, nb_last_words)
            nb_last_words -= 1
        sort = list(sorted(filter, key=filter.get, reverse=True))
        if len(sort) > 10: sort = sort[:10]
        sentence.append(choice(sort))
    return sentence

def tokens_to_text(sentence):
    return ' '.join(sentence).replace("<s> ", '').replace("</s>", '').replace("</?>", '?').replace("</!>", '!').replace("</...>", '...').replace("' ", "'").replace("[num]", str(randint(0,100)))

def genere_sentence(min=10):
    sentence = []
    while len(sentence) <= min:
        sentence = predict_sentence()
    return tokens_to_text(sentence)


def genere_corpus_sentence(nb=1):
    global dico2, dico3, dico4, dicontext
    dico2, dico3, dico4, dicontext = get_lexgram()
    print("Dictionnaires chargés.")
    if nb == 1:
        return genere_sentence()
    sentences = []
    for i in range(nb):
        sentences.append(genere_sentence())
    return sentences

def genere_similar_tweet(tweets, nb=1):
    global dico2, dico3, dico4
    dico2, dico3, dico4 = get_tweetgram(tweets)
    print("Dictionnaires générés.")
    if nb == 1:
        return genere_sentence()
    sentences = []
    for i in range(nb):
        sentences.append(genere_sentence())
    return sentences

def genere_mix_tweet():
    pass

#print(genere_corpus_sentence())
