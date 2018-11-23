#!/usr/bin/env python3
# coding: utf-8
import re
from nltk.tokenize import TweetTokenizer
from nltk.tag import pos_tag
from nltk.corpus import wordnet, sentiwordnet
from nltk.sentiment.vader import SentimentIntensityAnalyzer

def load_list(file):
    try:
        with open(file, "r") as f:
            return set([word.strip() for word in f.readlines()])
    except Exception as e : print("Erreur : " + str(e))

tweetoken = TweetTokenizer()
sentivader = SentimentIntensityAnalyzer()
stopwords = load_list("corpus/sentiment_analysis/stopwords.txt")
negwords = load_list("corpus/sentiment_analysis/negative_words.txt")

def remove_stopwords(list):
    return [[word, tag] for word, tag in list if word not in stopwords and len(word) > 1]

def normalizer(text):
    text = text.lower()
    text = re.sub("[\n\t\r]", " ", str(text))
    text = re.sub("https+://[^ ]+", " ", str(text))
    return text

def retagger(tag):
    if tag.startswith("NN") : return wordnet.NOUN
    elif tag.startswith("JJ"): return wordnet.ADJ
    elif tag.startswith("RB"): return wordnet.ADV
    elif tag.startswith("VB"): return wordnet.VERB
    else: return None

def sentiment_analyzer(text, showResults=False, showAnalysis=False, returnTuple=False):
    norm_text = normalizer(text)
    tok_text = tweetoken.tokenize(norm_text)
    tag_text = pos_tag(tok_text)
    clean_text = remove_stopwords(tag_text)

    token_count = pos_score = neg_score = obj_score = negInvert = 0
    for word, tag in clean_text:
        if word in negwords:
            negInvert = 1 # Si token négatif => inversion polarité token suivant
            if showAnalysis:
                print(word + " = <inverter>")
        else:
            synsets = list(sentiwordnet.senti_synsets(word, retagger(tag)))
            mood = synsets[0] if synsets else sentivader.polarity_scores(word)
            if type(mood) is not dict: # On a trouvé un synset => SentiWordNet
                pos_score += mood.pos_score() if not negInvert else mood.neg_score()
                neg_score += mood.neg_score() if not negInvert else mood.pos_score()
                if mood.pos_score() > 0 or mood.neg_score() > 0:
                    obj_score += mood.obj_score()
                    token_count += 1
                if showAnalysis:
                    print(word + " = " + str(mood) + " <ObjScore=" + str(mood.obj_score()) + ">")
            else: # On a pas trouvé de synset => VaderSentiment
                if mood['compound'] > 0:
                    if not negInvert: pos_score += mood['compound']
                    else: neg_score += mood['compound']
                elif mood['compound'] < 0:
                    if not negInvert: neg_score -= mood['compound']
                    else: pos_score -= mood['compound']
                if mood['compound'] != 0:
                    obj_score += 0.5
                    token_count += 1
                if showAnalysis:
                    print(word + " = <sentivader: PosScore=" + str(mood['pos']) + " NegScore=" + str(mood['neg'])
                            + " NeuScore=" + str(mood['neu']) + " Compound=" + str(mood['compound']) + ">")
            if negInvert: negInvert = 0

    if token_count == 0: # Pour éviter la division par 0 dans le cas  d'un nombre nul de tokens polarisés trouvés
        final_pos_score = final_neg_score = final_obj_score = final_score = 0
    else: # Calcul des résultats
        final_pos_score = round(float(pos_score) / token_count, 5)
        final_neg_score = round(float(neg_score) / token_count, 5)
        final_obj_score = round(float(obj_score) / token_count, 5)
        final_score = round(final_pos_score - final_neg_score, 5)

    if showResults:
        print("\n" + str(norm_text) + " :\npos : " + str(final_pos_score) + " | neg : "
        + str(final_neg_score) + " | obj : " + str(final_obj_score) + " | polarity : " + str(final_score))
    return final_score if not returnTuple else (final_pos_score, final_neg_score, final_obj_score)


#text = "Even when i'm angry, i could never kill someone"
#sentiment_analyzer(text, showResults=True, showAnalysis=True)