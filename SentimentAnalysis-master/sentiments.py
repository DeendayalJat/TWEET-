from flask import Blueprint, render_template, request
import matplotlib.pyplot as plt
import os
import tweepy
import csv
import re
from textblob import TextBlob
import matplotlib
import numpy as np

# Use non-GUI backend for Matplotlib
matplotlib.use('agg')

# Flask Blueprint
second = Blueprint("second", __name__, static_folder="static", template_folder="template")

# Render page
@second.route("/sentiment_analyzer")
def sentiment_analyzer():
    return render_template("sentiment_analyzer.html")

# Sentiment Analysis Class
class SentimentAnalysis:
    def __init__(self):
        self.tweets = []
        self.tweetText = []

    def DownloadData(self, keyword, tweets):
        client = tweepy.Client(bearer_token='msufT1GSPD3KcnNQKGhTE%3DwIbehdIby3FC0A3DSInkus0ThoezzdHltq6NaVuSX3bgkgly95')
        tweets = int(tweets)
        
        # Fetch tweets
        response = client.search_recent_tweets(query=keyword, max_results=tweets, tweet_fields=["text"])
        self.tweets = response.data if response.data else []
        
        if not self.tweets:
            print("Error: No tweets retrieved. Please check the keyword and API limits.")
            return 0, "No Data", 0, 0, 0, 0, 0, 0, 0, keyword, tweets
        
        csvFile = open('result.csv', 'a')
        csvWriter = csv.writer(csvFile)

        polarity, positive, wpositive, spositive, negative, wnegative, snegative, neutral = 0, 0, 0, 0, 0, 0, 0, 0
        
        for tweet in self.tweets:
            tweet_text = tweet.text if hasattr(tweet, 'text') else ""
            clean_text = self.cleanTweet(tweet_text)
            self.tweetText.append(clean_text.encode('utf-8'))

            analysis = TextBlob(clean_text)
            polarity += analysis.sentiment.polarity

            if analysis.sentiment.polarity == 0:
                neutral += 1
            elif 0 < analysis.sentiment.polarity <= 0.3:
                wpositive += 1
            elif 0.3 < analysis.sentiment.polarity <= 0.6:
                positive += 1
            elif 0.6 < analysis.sentiment.polarity <= 1:
                spositive += 1
            elif -0.3 < analysis.sentiment.polarity < 0:
                wnegative += 1
            elif -0.6 < analysis.sentiment.polarity <= -0.3:
                negative += 1
            elif -1 < analysis.sentiment.polarity <= -0.6:
                snegative += 1
        
        csvWriter.writerow(self.tweetText)
        csvFile.close()

        # Compute percentages
        positive, wpositive, spositive, negative, wnegative, snegative, neutral = [self.percentage(x, tweets) for x in [positive, wpositive, spositive, negative, wnegative, snegative, neutral]]
        polarity = polarity / tweets if tweets > 0 else 0
        
        htmlpolarity = "Neutral" if polarity == 0 else "Weakly Positive" if 0 < polarity <= 0.3 else "Positive" if 0.3 < polarity <= 0.6 else "Strongly Positive" if 0.6 < polarity <= 1 else "Weakly Negative" if -0.3 < polarity <= 0 else "Negative" if -0.6 < polarity <= -0.3 else "Strongly Negative"
        
        # Debug Print
        print(f"Sentiment Scores: Positive={positive}, Weak Positive={wpositive}, Strong Positive={spositive}, Negative={negative}, Weak Negative={wnegative}, Strong Negative={snegative}, Neutral={neutral}")
        
        if sum(map(float, [positive, wpositive, spositive, negative, wnegative, snegative, neutral])) == 0:
            print("Error: No sentiment data available.")
            return 0, "No Data", 0, 0, 0, 0, 0, 0, 0, keyword, tweets
        
        self.plotPieChart(positive, wpositive, spositive, negative, wnegative, snegative, neutral, keyword, tweets)
        
        return polarity, htmlpolarity, positive, wpositive, spositive, negative, wnegative, snegative, neutral, keyword, tweets
    
    def cleanTweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\\w+:\/\/\\S+)", " ", tweet).split())
    
    def percentage(self, part, whole):
        return format(100 * float(part) / float(whole) if whole > 0 else 0, '.2f')
    
    def plotPieChart(self, positive, wpositive, spositive, negative, wnegative, snegative, neutral, keyword, tweets):
        fig = plt.figure()
        labels = [f'Positive [{positive}%]', f'Weakly Positive [{wpositive}%]', f'Strongly Positive [{spositive}%]', f'Neutral [{neutral}%]', f'Negative [{negative}%]', f'Weakly Negative [{wnegative}%]', f'Strongly Negative [{snegative}%]']
        sizes = list(map(float, [positive, wpositive, spositive, neutral, negative, wnegative, snegative]))
        
        if sum(sizes) == 0:
            print("Error: Pie chart cannot be generated because all sentiment values are zero.")
            return
        
        colors = ['yellowgreen', 'lightgreen', 'darkgreen', 'gold', 'red', 'lightsalmon', 'darkred']
        patches, texts, autotexts = plt.pie(sizes, colors=colors, startangle=90, autopct='%1.1f%%')
        plt.legend(patches, labels, loc="best")
        plt.axis('equal')
        plt.tight_layout()
        strFile = "static/images/plot1.png"
        if os.path.isfile(strFile):
            os.remove(strFile)
        plt.savefig(strFile)
        plt.close()

@second.route('/sentiment_logic', methods=['POST', 'GET'])
def sentiment_logic():
    keyword = request.form.get('keyword')
    tweets = request.form.get('tweets')
    sa = SentimentAnalysis()
    polarity, htmlpolarity, positive, wpositive, spositive, negative, wnegative, snegative, neutral, keyword1, tweet1 = sa.DownloadData(keyword, tweets)
    return render_template('sentiment_analyzer.html', polarity=polarity, htmlpolarity=htmlpolarity, positive=positive, wpositive=wpositive, spositive=spositive, negative=negative, wnegative=wnegative, snegative=snegative, neutral=neutral, keyword=keyword1, tweets=tweet1)

@second.route('/visualize')
def visualize():
    return render_template('PieChart.html')
