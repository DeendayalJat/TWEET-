from flask import Flask, request, jsonify
import tweepy
import pandas as pd
import re
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from textblob import TextBlob
import nltk

nltk.download('vader_lexicon')

app = Flask(__name__)

# Twitter API authentication (Replace with your own credentials)
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAPuh0AEAAAAATSXxPBUcNHfV%2B32ei9L0y5yyRMA%3D5dJK3U5uRwOibwfQJJOcIrN3ZdyrSDw8PbcDPUWmod9gbUJtdfN"
client = tweepy.Client(bearer_token=BEARER_TOKEN)

def preprocess_tweet(text):
    text = text.lower()
    text = re.sub('RT @\w+: ', " ", text)
    text = re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", text)
    text = re.sub(r"\s+[a-zA-Z]\s+", ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text

@app.route('/analyze', methods=['GET'])
def analyze_tweets():
    keyword = request.args.get('keyword', '')
    if not keyword:
        return jsonify({"error": "Please provide a keyword"}), 400
    
    query = f'#{keyword} -is:retweet lang:en'
    tweets = client.search_recent_tweets(query=query, max_results=10)
    
    tweet_data = []
    for tweet in tweets.data:
        clean_text = preprocess_tweet(tweet.text)
        analysis = TextBlob(clean_text)
        score = SentimentIntensityAnalyzer().polarity_scores(clean_text)
        sentiment = "positive" if score['compound'] > 0.05 else "negative" if score['compound'] < -0.05 else "neutral"
        
        tweet_data.append({
            "original": tweet.text,
            "cleaned": clean_text,
            "polarity": analysis.sentiment.polarity,
            "subjectivity": analysis.sentiment.subjectivity,
            "sentiment": sentiment
        })
    
    return jsonify(tweet_data)

if __name__ == '__main__':
    app.run(debug=True)
