import streamlit as st
import pandas as pd
import tweepy
import networkx as nx
import time
import matplotlib
import matplotlib.pyplot as plt
import networkx.algorithms.community as nx_comm
from networkx.algorithms import community
from networkx.algorithms.community import greedy_modularity_communities

# access_token = "1338405329684418560-gbPj1S2B8ZooGYa5zTVP419kvOi6A4"
# access_token_secret = "qkUYBywzaRdfOemFoxaZpJXslPZuFgo5aUt6nb84AFAMn"

# api_key = "BYuSRARWMfkmpMMHbbgMbuDBA"
# api_key_secret = "zuZXF7ChNGE1As6ibLy0Lx5mnFCQEQb9XACoIICuIG1rKyvvmZ"


def scrape(hashtag,amount):
  
  consumer_key = "BYuSRARWMfkmpMMHbbgMbuDBA"
  consumer_secret = "zuZXF7ChNGE1As6ibLy0Lx5mnFCQEQb9XACoIICuIG1rKyvvmZ"

  access_key = "1338405329684418560-gbPj1S2B8ZooGYa5zTVP419kvOi6A4"
  access_secret = "qkUYBywzaRdfOemFoxaZpJXslPZuFgo5aUt6nb84AFAMn"

  auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
  auth.set_access_token(access_key, access_secret)

  
  api = tweepy.API(auth,wait_on_rate_limit=True)
  
  

  db = pd.DataFrame(columns=['username',
                             'following',
                             'followers',
                             'totaltweets',
                             'retweetcount',
                             'text',
                             'hashtags',
                             'createdat'])
  
  
  
  tweets = tweepy.Cursor(api.search,
                         hashtag, 
                         lang="en",
                         tweet_mode='extended',max_results=100,type="mixed").items(amount)
                        
  list_tweets = [tweet for tweet in tweets]
 
  for tweet in list_tweets:
          username = tweet.user.screen_name
          following = tweet.user.friends_count
          followers = tweet.user.followers_count
          totaltweets = tweet.user.statuses_count
          retweetcount = tweet.retweet_count
          hashtags = tweet.entities['hashtags']
          created=tweet.created_at

          try:
                  text = tweet.retweeted_status.full_text
          except AttributeError:
                  text = tweet.full_text
          hashtext = list()
          for j in range(0, len(hashtags)):
                  hashtext.append(hashtags[j]['text'])
          if(len(hashtext)>1):
            ith_tweet = [username, 
                        following,
                        followers, 
                        totaltweets,
                        retweetcount, 
                        text, 
                        hashtext,
                        created]
                    
            db.loc[len(db)] = ith_tweet
          name=hashtag+'.csv'
          #db.to_csv(name)
  #db["hashtags"] = db["hashtags"].apply(eval)

  return(db)

def to_1D(series):
 return pd.Series([x for _list in series for x in _list])

def frequency(df):

  hash_dict = {}
  hash_dict=to_1D(df["hashtags"]).value_counts()
  
  return(hash_dict)

st.title('Recent Hashtag posts visualization')

name=st.text_input("Hashtag","Type Here")

clicked = st.button('Process..')

if clicked:
  G=nx.MultiDiGraph()

  max_counter=3
  counter=0
  j=1
  s=0
  d={}
  f={}
  done=[]
  done.append(name)
  rem=[]
  colour=[]

  d[name]=scrape(name,100)
  f[name]=frequency(d[name])

  G.add_node(name,colour='red')
  colour.append('red')
  for i in range(len(f[name])):
    s=0
    if(counter==8):
      break
    cur="#"+list(f[name].items())[i+1][0]
    print(cur)
    for j in done:
      if(similar(cur,j)>0.8):
        s=1
    if(s==1):
      continue
    else:
      d[cur]=scrape(cur,100)
      done.append(cur)
      f[cur]=frequency(d[cur])
      counter=counter+1
      G.add_node(cur,colour='green')
      colour.append('green')
      G.add_edge(name,cur,weight=f[name][i])
      


  for i in range(7):
    counter=0
    cur=done[i+1]
    for j in range(len(f[cur])):
      sim=0
      if(counter==max_counter):
        break
      if(similar(cur,"#"+list(f[cur].items())[j][0])>=0.8):
        continue
      counter=counter+1
      for k in done:
        if(similar("#"+list(f[cur].items())[j][0],k)>=0.8):
          sim=1
          G.add_edge(cur,k,weight=f[cur][j])
      if(sim==1):
        continue 

      if("#"+list(f[cur].items())[j][0] in done):
        G.add_edge(cur,"#"+list(f[cur].items())[j][0],weight=f[cur][j])
      else:
        G.add_node("#"+list(f[cur].items())[j][0],colour='blue')
        colour.append('blue')
        done.append("#"+list(f[cur].items())[j][0])
        G.add_edge(cur,"#"+list(f[cur].items())[j][0],weight=f[cur][j])
  sample=[]
  sample.append(done[0])
  shells=[sample,done[1:9],done[9:]]
  pos = nx.shell_layout(G, shells)
  labels = nx.get_edge_attributes(G,'weight')

  weights = list(zip(*nx.get_edge_attributes(G, 'weight').items()))
  fig, ax = plt.subplots()
  nx.draw(G,pos,node_color=colour,edge_color=weights[1], width=2,with_labels = True)
  st.pyplot(fig)
  
