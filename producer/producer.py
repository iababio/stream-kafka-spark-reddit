#!/usr/bin/python3

from kafka import KafkaProducer
from datetime import datetime
import praw
import secret_config as conf  # Configuration file for Reddit API keys
import sys
import time

SUBREDDIT_TOPICS = ['politics', 'worldnews', 'technology', 'sports', 'funny', 'gaming', 'aww', 'pics', 'videos', 'news']

KAFKA_BROKER = 'localhost:9092'
KAFKA_TOPIC = 'reddit_posts'

# Initialize Reddit API
reddit = praw.Reddit(
    client_id=conf.reddit_client_id,
    client_secret=conf.reddit_client_secret,
    user_agent=conf.reddit_user_agent
)

def send_to_kafka(post):
    try:
        producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER)
        producer.send(KAFKA_TOPIC, bytes(post.title + ' ' + post.selftext, encoding='utf-8'))
        producer.flush()  # Ensure all messages are sent before closing
        print(f"[{datetime.now().strftime('%H:%M.%S')}] Sent post to Kafka: {post.title}")
    except Exception as e:
        print(f'Error sending to Kafka --> {e}')
        sys.exit(1)

def stream_subreddits():
    for topic in SUBREDDIT_TOPICS:
        subreddit = reddit.subreddit(topic)
        for post in subreddit.stream.submissions():
            send_to_kafka(post)

try:
    stream_subreddits()
except KeyboardInterrupt:
    print("Stream stopped manually")
except Exception as e:
    print(f'Error in Reddit stream --> {e}')
    sys.exit(1)
