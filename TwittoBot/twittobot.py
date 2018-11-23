#!/usr/bin/env python3
# coding: utf-8
import matplotlib.pyplot as plt
from twitter_interaction import getTrends, getTweets, sendTweet, seeLastTweet, deleteLastTweet
from sentiment_analysis import sentiment_analyzer
from text_generation import genere_similar_tweet
from ngrams import fastcontext

def show_graphics(listNeg, listPos, listObj, listPol):
    plt.subplot(1, 2, 1)
    plt.ylabel("Positivité")
    plt.xlabel("Négativité")
    plt.plot([0,1], [0,1], "r--", listNeg, listPos, "b.")
    plt.subplot(1, 2, 2)
    plt.ylabel("Polarité")
    plt.xlabel("Objectivité")
    plt.plot([0,1], [0,0], "r--", listObj, listPol, "b.")
    plt.show()


def sentiment_Trend(trend, nb=500, showScore=False, showTweets=False, showGraphics=False):
    listNeg, listPos, listObj, listPol = [], [], [], []
    trendScore = 0
    for tweet in getTweets(trend, nb):
        pos, neg, obj = sentiment_analyzer(tweet, showResults=showTweets, returnTuple=True)
        score = pos - neg
        trendScore += 1 if  score > 0 else -1 if score < 0 else 0
        if showGraphics:
            listNeg.append(neg)
            listPos.append(pos)
            listObj.append(obj)
            listPol.append(score)
    trendScore = round(float(trendScore) / nb, 5)
    if showScore: print(trend + " : " + str(trendScore))
    if showGraphics: show_graphics(listNeg, listPos, listObj, listPol)
    return trendScore

def analyse_Trends_USA(nb_trends=10, nb_tweets_by_trend=500, showTop=False):
    if nb_trends > 50: nb_trends = 50
    print("Analyse des tendances... ["+str(nb_trends)+"]x["+str(nb_tweets_by_trend)+"]")
    hashtagTrends, top = [], {}
    for trend in getTrends(23424977):
        if trend.startswith('#') and len(hashtagTrends) < nb_trends:
            hashtagTrends.append(trend)
    for trend in hashtagTrends:
        top[trend] = sentiment_Trend(trend, nb_tweets_by_trend)
    sorted_top = sorted(top, key=top.get, reverse=True)

    if showTop:
        print("\n* TOP "+str(nb_trends)+" POSITIVE TRENDS USA *")
        for trend in sorted_top:
            print(trend+" : "+str(top[trend]))
        print()

    best_trend = next(iter(sorted_top))
    return (best_trend.lower(), top[best_trend])


def context_trend(trend, nb=20, nb_tweets=5000):
    print("Trend : " + trend)
    print("Récupération de tweets de la tendance... ["+str(nb_tweets)+"]")
    trend_tweets = getTweets(trend, nb_tweets)
    fastcontext(trend, trend_tweets, nb, show=True)

def genere_best_tweet(nb_trends=5, nb_tweets=500, showTopTrends=False, showGeneredTweets=False):
    best_trend, best_trend_score = analyse_Trends_USA(nb_trends, nb_tweets, showTop=showTopTrends)
    print("Meilleure Tendance : "+best_trend+" : "+str(best_trend_score))

    print("Récupération de tweets de la tendance... ["+str(nb_tweets*10)+"]")
    best_trend_tweets = getTweets(best_trend, nb_tweets*10)
    
    print("Génération de tweets... ["+str(nb_tweets)+"]")
    new_tweets = genere_similar_tweet(best_trend_tweets, nb=nb_tweets)

    print("Analyse des tweets générés...")
    if showGeneredTweets: print()
    best_tweet, best_tweet_score = None, -1
    for tweet in new_tweets:
        tweet_score = sentiment_analyzer(tweet, showResults=showGeneredTweets)
        if best_trend not in tweet:
            tweet += ' '+best_trend
        if tweet_score > best_tweet_score and len(tweet) < 280:
            best_tweet, best_tweet_score = tweet, tweet_score
    if showGeneredTweets: print()

    print("Meilleur Tweet Généré : "+best_tweet+" : "+str(best_tweet_score))
    return best_tweet.capitalize()


def push_tweet(nb=1):
    if nb > 0:
        generated_tweet = genere_best_tweet()
        if generated_tweet is not None:
            sendTweet(generated_tweet)
        push_tweet(nb-1)

#sentiment_Trend("trump", nb=1000, showScore=True, showTweets=False, showGraphics=True)
#analyse_Trends_USA(nb_trends=10, nb_tweets_by_trend=100, showTop=True)

push_tweet()
#seeLastTweet()
#deleteLastTweet()

#context_trend("trump")
