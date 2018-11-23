#!/usr/bin/env python3
# coding: utf-8
from sentiment_analysis import sentiment_analyzer
from nltk.corpus import twitter_samples, movie_reviews
from csv import reader

def F_mesure(vp, fp, fn):
    precision, rappel = float(vp)/(vp+fp), float(vp)/(vp+fn)
    return float(2*precision*rappel) / (precision+rappel)

def evaluation(correctPos, incorrectPos, correctNeg, incorrectNeg):
    total = correctPos+incorrectPos+correctNeg+incorrectNeg
    print("F-mesure Pos : " + str(F_mesure(correctPos, incorrectNeg, incorrectPos)))
    print("F-mesure Neg : " + str(F_mesure(correctNeg, incorrectPos, incorrectNeg)))
    print("Correct/Total : " + str(float(correctPos+correctNeg) / total))
    print("Incorrect/Total : " + str(float(incorrectPos+incorrectNeg) / total), end="\n\n")

def eval_sorted_tweets(dataname, positive_tweets, negative_tweets):
    correctPos = incorrectPos = correctNeg = incorrectNeg = count = 0
    total = len(positive_tweets) + len(negative_tweets)
    for tweet in positive_tweets:
        score = sentiment_analyzer(tweet)
        if score >= 0: correctPos += 1
        else: incorrectPos += 1
        count += 1
        if count % 15000 == 0:
            print("Progression : " + str(round(float(100*count)/total, 4)) + "%")
    for tweet in negative_tweets:
        score = sentiment_analyzer(tweet)
        if score >= 0: incorrectNeg += 1
        else: correctNeg += 1
        count += 1
        if count % 15000 == 0:
            print("Progression : " + str(round(float(100*count)/total, 4)) + "%")
    print(dataname + " :")
    evaluation(correctPos, incorrectPos, correctNeg, incorrectNeg)


def eval_with_twitter_samples(): # 10000 tweets
    positive_tweets = twitter_samples.strings('positive_tweets.json')
    negative_tweets = twitter_samples.strings('negative_tweets.json')
    eval_sorted_tweets("Twitter Samples", positive_tweets, negative_tweets)

def eval_with_movie_reviews(): # 2000 critiques
    positive_tweets, negative_tweets = [], []
    for fileid in movie_reviews.fileids('pos'):
        positive_tweets.append(' '.join(movie_reviews.words(fileid)))
    for fileid in movie_reviews.fileids('neg'):
        negative_tweets.append(' '.join(movie_reviews.words(fileid)))
    eval_sorted_tweets("Movie Reviews", positive_tweets, negative_tweets)

def eval_with_sentiment140_testcorpus(): # 500 tweets
    positive_tweets, negative_tweets = [], []
    try:
        with open('corpus/sentiment_analysis/Sentiment140/testdata.manual.2009.06.14.csv', 'r') as csvfile:
            for row in  reader(csvfile, delimiter=','):
                polarity, text = int(row[0]), row[5]
                if polarity == 4: positive_tweets.append(text)
                elif polarity == 0: negative_tweets.append(text)
        eval_sorted_tweets("Sentiment140 (testcorpus)", positive_tweets, negative_tweets)
    except Exception as e: print("Erreur csv : " + str(e))

def eval_with_sentiment140_traincorpus(): # 1600000 tweets
    positive_tweets, negative_tweets = [], []
    try:
        with open('corpus/sentiment_analysis/Sentiment140/training.1600000.processed.noemoticon.csv', 'r') as csvfile:
            for row in  reader(csvfile, delimiter=','):
                polarity, text = int(row[0]), row[5]
                if polarity == 4: positive_tweets.append(text)
                elif polarity == 0: negative_tweets.append(text)
        eval_sorted_tweets("Sentiment140 (traincorpus)", positive_tweets, negative_tweets)
    except Exception as e: print("Erreur csv : " + str(e))


#eval_with_twitter_samples()
#eval_with_movie_reviews()
#eval_with_sentiment140_testcorpus()
#eval_with_sentiment140_traincorpus()

""" RESULTATS :

Twitter Samples :
F-mesure Pos : 0.8970753655793026
F-mesure Neg : 0.8823403343334761
Correct/Total : 0.8902
Incorrect/Total : 0.1098

Movie Reviews :
F-mesure Pos : 0.6938610662358643
F-mesure Neg : 0.5026246719160105
Correct/Total : 0.621
Incorrect/Total : 0.379

Sentiment140 (testcorpus) :
F-mesure Pos : 0.7817745803357316
F-mesure Neg : 0.6976744186046511
Correct/Total : 0.7465181058495822
Incorrect/Total : 0.25348189415041783

Sentiment140 (traincorpus) :
F-mesure Pos : 0.6936528504043472
F-mesure Neg : 0.5205079080058037
Correct/Total : 0.626155
Incorrect/Total : 0.373845

"""
