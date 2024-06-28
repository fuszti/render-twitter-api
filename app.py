from flask import Flask, request, jsonify
import tweepy
import time
import os

app = Flask(__name__)

# Load Twitter API credentials from environment variables
CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

PORT = os.getenv("PORT", 4000)
API_KEY = os.getenv("API_KEY")

client = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

@app.before_request
def before_request():
    if request.headers.get('API-Key') != API_KEY:
        print(f"Unauthorized request with API key: {request.headers.get('API-Key')}")
        print(f"Expected API key: {API_KEY}")
        return jsonify({"error": "Unauthorized"}), 403
    
@app.route('/tweet', methods=['POST'])
def post_single_tweet():
    data = request.get_json()
    tweet = data.get("tweet", "")

    if not tweet:
        return jsonify({"error": "Tweet content is empty"}), 400

    client.create_tweet(text=tweet)

    return jsonify({"message": "Tweet posted successfully"}), 200

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
            new_tweet = client.create_tweet(text=tweet_text)
        else:
            new_tweet = client.create_tweet(text=tweet_text, in_reply_to_tweet_id=last_tweet_id)

        last_tweet_id = new_tweet[0]['id']

        time.sleep(duration_between_tweets)
    
    return jsonify({"message": "Thread posted successfully"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
