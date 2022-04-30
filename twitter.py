import tweepy
import pandas as pd
from decouple import config
import streamlit as st


@st.cache(suppress_st_warning=True)
def scrape(hashtag, amount):
    consumer_key = config("consumer_key")
    consumer_secret = config("consumer_secret")

    access_key = config("access_key")
    access_secret = config("access_secret")

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)

    api = tweepy.API(auth, wait_on_rate_limit=True)

    db = pd.DataFrame(columns=['username',
                               'following',
                               'followers',
                               'total_tweets',
                               'retweet_count',
                               'text',
                               'hashtags',
                               'createdat'])

    tweets = tweepy.Cursor(api.search_tweets,
                           hashtag,
                           lang="en",
                           tweet_mode='extended', count=100, result_type="mixed").items(amount)

    list_tweets = [tweet for tweet in tweets]

    for tweet in list_tweets:
        username = tweet.user.screen_name
        following = tweet.user.friends_count
        followers = tweet.user.followers_count
        total_tweets = tweet.user.statuses_count
        retweet_count = tweet.retweet_count
        hashtags = tweet.entities['hashtags']
        created = tweet.created_at

        try:
            text = tweet.retweeted_status.full_text
        except AttributeError:
            text = tweet.full_text
        hash_text = list()
        for j in range(0, len(hashtags)):
            hash_text.append(hashtags[j]['text'])
        if len(hash_text) > 1:
            ith_tweet = [username,
                         following,
                         followers,
                         total_tweets,
                         retweet_count,
                         text,
                         hash_text,
                         created]

            db.loc[len(db)] = ith_tweet
    return db
