import streamlit as st
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import pandas as pd
import tweepy
import json
from tweepy import OAuthHandler
import re
import textblob
from textblob import TextBlob
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import openpyxl
import time
import tqdm


st.set_option('deprecation.showfileUploaderEncoding', False)
st.set_option('deprecation.showPyplotGlobalUse', False)

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import seaborn as sns



STYLE = """
<style>
img {
    max-width: 100%;
}
</style> """

def main():
    """ Common ML Dataset Explorer """
    

    html_temp = """
	<div style="background-color:tomato;"><p style="color:white;font-size:40px;padding:9px">Live twitter Sentiment analysis</p></div>
	"""
    st.markdown(html_temp, unsafe_allow_html=True)
    st.subheader("Select a topic which you'd like to get the sentiment analysis on :")

    
    consumer_key = "your api key"
    consumer_secret = "your secret api key"
    access_token = ""
    access_token_secret = ""



    

    auth = tweepy.OAuthHandler( consumer_key , consumer_secret )
    auth.set_access_token( access_token , access_token_secret )
    api = tweepy.API(auth)
    
    
    df = pd.DataFrame(columns=["Date","User","IsVerified","Tweet","Likes","RT",'User_location'])
    
    
    def get_tweets(Topic,Count):
        i=0
      
        for tweet in tweepy.Cursor(api.search, q=Topic,count=100, lang="en",exclude='retweets').items():
            
            df.loc[i,"Date"] = tweet.created_at
            df.loc[i,"User"] = tweet.user.name
            df.loc[i,"IsVerified"] = tweet.user.verified
            df.loc[i,"Tweet"] = tweet.text
            df.loc[i,"Likes"] = tweet.favorite_count
            df.loc[i,"RT"] = tweet.retweet_count
            df.loc[i,"User_location"] = tweet.user.location
            
            i=i+1
            if i>Count:
                break
            else:
                pass
    
    def clean_tweet(tweet):
        return ' '.join(re.sub('(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|([RT])', ' ', tweet.lower()).split())
    
        
    
    def analyze_sentiment(tweet):
        analysis = TextBlob(tweet)
        if analysis.sentiment.polarity > 0:
            return 'Positive'
        elif analysis.sentiment.polarity == 0:
            return 'Neutral'
        else:
            return 'Negative'
    
    #Function to Pre-process data for Worlcloud
    def prepCloud(Topic_text,Topic):
        Topic = str(Topic).lower()
        Topic=' '.join(re.sub('([^0-9A-Za-z \t])', ' ', Topic).split())
        Topic = re.split("\s+",str(Topic))
        stopwords = set(STOPWORDS)
        stopwords.update(Topic) ### Add our topic in Stopwords, so it doesnt appear in wordClous
        ###
        text_new = " ".join([txt for txt in Topic_text.split() if txt not in stopwords])
        return text_new

    
    #
    from PIL import Image
    image = Image.open('Logo1.jpg')
    st.image(image, caption='Twitter for Analytics',use_column_width=True)
    
    
    # Collect Input from user :
    Topic = str()
    Topic = str(st.text_input("Enter the topic you are interested in (Press Enter once done)"))     
    
    if len(Topic) > 0 :
        
        # Call the function to extract the data. pass the topic and filename you want the data to be stored in.
        with st.spinner("Please wait, Tweets are being extracted"):
            get_tweets(Topic , Count=200)
        st.success('Tweets have been Extracted !!!!')    
           
    
        # Call function to get Clean tweets
        df['clean_tweet'] = df['Tweet'].apply(lambda x : clean_tweet(x))
    
        # Call function to get the Sentiments
        df["Sentiment"] = df["Tweet"].apply(lambda x : analyze_sentiment(x))
        
        
        # Write Summary of the Tweets
        st.write("Total Tweets Extracted for Topic '{}' are : {}".format(Topic,len(df.Tweet)))
        st.write("Total Positive Tweets are : {}".format(len(df[df["Sentiment"]=="Positive"])))
        st.write("Total Negative Tweets are : {}".format(len(df[df["Sentiment"]=="Negative"])))
        st.write("Total Neutral Tweets are : {}".format(len(df[df["Sentiment"]=="Neutral"])))
        
        # See the Extracted Data : 
        if st.button("See the Extracted Data"):
            #st.markdown(html_temp, unsafe_allow_html=True)
            st.success("Below is the Extracted Data :")
            st.write(df.head(50))
        
        
        # get the countPlot
        if st.button("Get Count Plot for Different Sentiments"):
            st.success("Generating A Count Plot")
            st.subheader(" Count Plot for Different Sentiments")
            st.write(sns.countplot(df["Sentiment"]))
            st.pyplot()
        
        # Piechart 
        if st.button("Get Pie Chart for Different Sentiments"):
            st.success("Generating A Pie Chart")
            a=len(df[df["Sentiment"]=="Positive"])
            b=len(df[df["Sentiment"]=="Negative"])
            c=len(df[df["Sentiment"]=="Neutral"])
            d=np.array([a,b,c])
            explode = (0.1, 0.0, 0.1)
            st.write(plt.pie(d,shadow=True,explode=explode,labels=["Positive","Negative","Neutral"],autopct='%1.2f%%'))
            st.pyplot()
            
            
        
        if st.button("Get Count Plot Based on Verified and unverified Users"):
            st.success("Generating A Count Plot (Verified and unverified Users)")
            st.subheader(" Count Plot for Different Sentiments for Verified and unverified Users")
            st.write(sns.countplot(df["Sentiment"],hue=df.IsVerified))
            st.pyplot()
        
        
       
        
        
        # Create a Worlcloud
        if st.button("Get WordCloud for all things said about {}".format(Topic)):
            st.success("Generating A WordCloud for all things said about {}".format(Topic))
            text = " ".join(review for review in df.clean_tweet)
            stopwords = set(STOPWORDS)
            text_newALL = prepCloud(text,Topic)
            wordcloud = WordCloud(stopwords=stopwords,max_words=800,max_font_size=70).generate(text_newALL)
            st.write(plt.imshow(wordcloud, interpolation='bilinear'))
            st.pyplot()
    st.sidebar.header("About App")
    st.sidebar.info("A Twitter Sentiment analysis Project which will scrap twitter for the topic selected by the user. The extracted tweets will then be used to determine the Sentiments of those tweets. \
                The different Visualizations will help us get a feel of the overall mood of the people on Twitter regarding the topic we select.")
    st.sidebar.text("Built with Streamlit")
    
    st.sidebar.header("For Any Queries/Suggestions Please reach out at :")
    st.sidebar.info("ramkaurav90@gmail.com")
    



    if st.button("Exit"):
        st.balloons()



if __name__ == '__main__':
    main()
