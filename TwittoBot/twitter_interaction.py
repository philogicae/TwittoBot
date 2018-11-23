#!/usr/bin/env python3
# coding: utf-8
import tweepy

Consumer_Key = "VjuVDmv4jLbgMFkkI99F5iML0"
Consumer_Secret = "QHEU0akSnjRHCNBziAn0AqEjJLJpiYrUpd7MOun7sgO02z1KaR"
Access_Token = "972545524074254336-XfEVEkkF64l7kW2qwUC4ZigUUylNymb"
Access_Token_Secret = "78k5RQuentP49mN1psm7eCXbnUg2Op2rqN9ynLS3ssqY6"
api, login, log_state = None, None, None

def logging(status):
    global api, login, log_state
    if status == "as_App": # Nb de requêtes tweet autorisées plus élevées
        login = tweepy.AppAuthHandler(Consumer_Key, Consumer_Secret)
    elif status == "as_User": # Permet l'accès aux outils de publication
        login = tweepy.OAuthHandler(Consumer_Key, Consumer_Secret)
        login.set_access_token(Access_Token, Access_Token_Secret)
    api = tweepy.API(login, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    log_state = status


def getTweets(key, nb=5):
    if log_state != "as_App":
        logging("as_App")
    tweets = tweepy.Cursor(api.search, q=key+" -filter:retweets", result_type='recent', tweet_mode="extended", lang="en", count=100).items(nb)
    return [tweet.full_text for tweet in tweets]

def getTrends(woeid):
    if log_state != "as_App":
        logging("as_App")
    place = api.trends_place(woeid)
    return set([trend["name"] for trend in place[0]["trends"]])


def sendTweet(text):
    if log_state != "as_User":
        logging("as_User")
    api.update_status(text)
    print("\"" + text + "\" : Publié !")

def seeLastTweet():
    try:
        if log_state != "as_User":
            logging("as_User")
        last_tweet = api.user_timeline()[0]
        print(api.get_status(last_tweet.id).text)
    except Exception as e:
        print("Erreur : aucun tweet disponible\n" + str(e))

def deleteLastTweet():
    try:
        if log_state != "as_User":
            logging("as_User")
        last_tweet = api.user_timeline()[0]
        api.destroy_status(last_tweet.id)
        print("\"" + last_tweet.text + "\" : Supprimé !")
    except Exception as e:
        print("Erreur : aucun tweet disponible\n" + str(e))

#for tweet in getTweets("trump"): print(tweet+"\n")
#for trend in getTrends(23424977): print(trend)

#sendTweet("xezcaedada :)")
#seeLastTweet()
#deleteLastTweet()
