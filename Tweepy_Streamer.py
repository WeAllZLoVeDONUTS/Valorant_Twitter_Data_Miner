from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from textblob import TextBlob

import Twitter_Credentials
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re

class TwitterClient():
    def __init__(self, twitter_user):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)
        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    def get_user_timeline_tweets(self, num_tweets):
        tweets=[]
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets

    def get_friend_list(self, num_friends):
        friends_list = []
        for friend in Cursor(self.twitter_client.friends).items(num_friends):
            friends_list.append(friend)
        return friends_list

    def get_home_timeline_tweets(self, num_tweets):
        home_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets


#TWITTER AUTHENTICATOR
class TwitterAuthenticator():
    def authenticate_twitter_app(self):
        auth = OAuthHandler(Twitter_Credentials.CONSUMER_KEY, Twitter_Credentials.CONSUMER_SECRET)
        auth.set_access_token(Twitter_Credentials.ACCESS_TOKEN, Twitter_Credentials.ACCESS_TOKEN_SECRET)
        return auth




class TwitterStreamer():
    #Class for streaming and processing live tweets
    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticator()

    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        #This handles Twitter authentication and the connection to the Twitter Streaming API
        listener = TwitterListener()
        auth = self.twitter_authenticator.authenticate_twitter_app()
        stream = Stream(auth, listener)
        stream.filter(track=["Valorant", "Valorant Update", "Valorant Patch"])



class TwitterListener(StreamListener):
    #Basic Listener Class that prints received tweets
    def __innit__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename


    def on_data(self,data):
        try:
            print(data)
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write(data)
            return True
        except BaseException as e:
            print("Error on data: %s" % str(e))
        return True


    def on_error(self, status):
        if status==420:
            #Returning False to not get booted from mining data in case we violate any rules
            return False
        print(status)

class TweetAnalyzer():
    #Class used to analyze and categorize tweets

    def clean_tweet(self,tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def analyze_sentiment(self,tweet):
        analysis=TextBlob(self.clean_tweet(tweet))

        if analysis.sentiment.polarity > 0:
            return 1 #Positivly interpreted tweet
        elif analysis.sentiment.polarity == 0:
            return 0 #We don't know if the tweet is negative or positive
        else:
            return -1 #Negatively interpreted tweet

    def tweets_to_data_frame(self, tweets):
        data_frame = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['Tweets by Valorant Twitter Page'])

        data_frame['Author'] = np.array([tweet.author for tweet in tweets])
        data_frame['Likes'] = np.array([tweet.favorite_count for tweet in tweets])
        data_frame['Retweets'] = np.array([tweet.retweet_count for tweet in tweets])
        data_frame['Date'] = np.array([tweet.created_at for tweet in tweets])
        data_frame['Source'] = np.array([tweet.source for tweet in tweets])
        data_frame['ID'] = np.array([tweet.id for tweet in tweets])

        return data_frame


if __name__ == "__main__":
    twitter_client = TwitterClient("playVALORANT")
    tweet_analyzer = TweetAnalyzer()
    api = twitter_client.get_twitter_client_api()

    tweets = api.user_timeline(screen_name="playVALORANT",count=900)

    data_frame = tweet_analyzer.tweets_to_data_frame(tweets)
    #print(dir(tweets[0]))
    #print(data_frame.head(100))
    #print(np.max(data_frame['Likes']))

    data_frame['sentiment'] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in data_frame['Tweets by Valorant Twitter Page']])
    print(data_frame.head(10))

# Displays a graph of the data

    time_likes = pd.Series(data=data_frame['Likes'].values, index=data_frame['Date'])
    time_likes.plot(figsize=(16,4), color='r', label="Likes", legend=True)
    time_likes = pd.Series(data=data_frame['Retweets'].values, index=data_frame['Date'])
    time_likes.plot(figsize=(16,4), color='b', label="Retweets", legend=True)
    plt.show()



#Displays the Twitter Data
"""
    hash_tag_list = ["Valorant", "Update", "Agent", "Patch"]
    fetched_tweets_filename = "tweets.json"

    twitter_client=TwitterClient('playVALORANT')
    print(twitter_client.get_user_timeline_tweets(1))
"""
#    twitter_streamer = TwitterStreamer()
#    twitter_streamer.stream_tweets(fetched_tweets_filename, hash_tag_list)
