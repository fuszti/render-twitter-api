from flask import Flask, request, jsonify
import tweepy
import time
import os

app = Flask(__name__)

# Load Twitter API credentials from environment variables
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

auth = tweepy.AppAuthHandler(CLIENT_ID, CLIENT_SECRET)
api = tweepy.API(auth)

@app.route('/post_thread', methods=['POST'])
def post_thread():
    data = request.get_json()
    duration_between_tweets = data.get("duration_between_tweets", 0)
    thread = data.get("thread", [])
    
    if not thread:
        return jsonify({"error": "Thread content is empty"}), 400
    
    last_tweet_id = None

    for tweet in thread:
        if "tweet" not in tweet:
            continue

        tweet_text = tweet["tweet"]

        if last_tweet_id is None:
            new_tweet = api.update_status(status=tweet_text)
        else:
            new_tweet = api.update_status(status=tweet_text, in_reply_to_status_id=last_tweet_id, auto_populate_reply_metadata=True)

        last_tweet_id = new_tweet.id

        time.sleep(duration_between_tweets)
    
    return jsonify({"message": "Thread posted successfully"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

