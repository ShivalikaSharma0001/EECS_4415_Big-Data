#!/usr/bin/python

# -- coding: utf-8 --
# =============================================================================
# 
# Name: Shivalika Sharma, Komal Arora
# 
# =============================================================================
import socket
import sys
import json
import re
# 5 related hastags  - #YorkU, #UofT, #RyersonU, #mcmasteru, #uOttawa 
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import API
from tweepy import Stream

# Replace the values below with yours
consumer_key="ZAPfZLcBhYEBCeRSAK5PqkTT7"
consumer_secret="M81KvgaicyJIaQegdgXcdKDeZrSsJz4AVrGv3yoFwuItQQPMay"
access_token="2591998746-Mx8ZHsXJHzIxAaD2IxYfmzYuL3pYNVnvWoHZgR5"
access_token_secret="LJDvEa0jL7QJXxql0NVrULTAniLobe2TAAlnBdXRfm1xF"


class TweetListener(StreamListener):
    """ A listener that handles tweets received from the Twitter stream.

        This listener prints tweets and then forwards them to a local port
        for processing in the spark app.
    """

    def on_data(self, data):
        """When a tweet is received, forward it"""
        try:

            global conn

            # load the tweet JSON, get pure text
            full_tweet = json.loads(data)
            tweet_text = full_tweet['text']
           
            #clean the text
            clean_tweet_text = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)", " ", tweet_text).split())

            # print the tweet plus a separator
            print ("------------------------------------------")
            print(clean_tweet_text)
            # send it to spark
            conn.send(str.encode(clean_tweet_text + '\n'))         
        except:
            # handle errors
            e = sys.exc_info()[0]
            print("Error: %s" % e)
        return True

    def on_error(self, status):
        print(status)


# ==== setup local connection ====

# IP and port of local machine or Docker
TCP_IP = socket.gethostbyname(socket.gethostname()) # returns local IP
TCP_PORT = 9009

# setup local connection, expose socket, listen for spark app
conn = None
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
print("Waiting for TCP connection...")

# if the connection is accepted, proceed
conn, addr = s.accept()
print("Connected... Starting getting tweets.")


# ==== setup twitter connection ====
listener = TweetListener()
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
stream = Stream(auth, listener)

# setup search terms
track = ["#googlemaps","#googledoodle","#chrome", "#googleplay","#android","#chromecast","#youtube","#pixel3","#google","#googlearts",
        "#iOS","#iPhone","#applewatch","#macbook","#ipod","#airpods","#ipad","#itunes","#icloud","#applepay",
        "#azure","#office365","#windows","#xbox","#skype","#microsoftedge","#msn","#onedrive","#cortana","#minecraft",
        "#ibmcloud","#ibmwatson","#ibmsystems","#db2","#bluemix","#watsonsupplychain","#websphere","#ibminternhack","#ibmconsulting",
        "#acrobatpro","#dreamweaver","#adobemuse","#photoshop","#adobedimension","#adoberemix","#framemaker","#robohelp","captivateprime"]
#track = ['#']
language = ['en']
locations = [-130,-20,100,50]

# get filtered tweets, forward them to spark until interrupted
try:
    stream.filter(track=track, languages=language, locations=locations)
except KeyboardInterrupt:
    s.shutdown(socket.SHUT_RD)