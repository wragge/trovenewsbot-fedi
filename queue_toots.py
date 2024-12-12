from mastodon import Mastodon
import redis
from rq import Queue
import re
import json
from trovenewsbot_fedi import process_toot
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()

#   Set up Mastodon
mastodon = Mastodon(
    access_token = os.getenv("TOKEN_SECRET"),
    api_base_url = 'https://wraggebots.net/',
    version_check_mode = "none"
)

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
toot_queue = Queue('trovenewsbot', connection=redis.Redis())

"""
# since_id = redis_client.get('newsbot_last_tweet_id')
# since_id = None
if since_id:
    mentions = api.mentions_timeline(since_id=since_id, include_rts=False)
else:
    mentions = api.mentions_timeline(include_rts=False)
# [::-1] reverses the list
for tweet in mentions[::-1]:
    print(tweet.text)
    if tweet.in_reply_to_screen_name == 'TroveNewsBot':
        #tweet_author = '@' + tweet.author.screen_name
        #tweet_details = '{} | {} | {}'.format(tweet_id, tweet_author, tweet.text)
        tweet_json = json.dumps(tweet._json)
        #print(tweet_json)
        result = tweet_queue.enqueue(process_tweet, tweet_json)
    redis_client.set('newsbot_last_tweet_id', tweet.id_str)
"""
since_id = redis_client.get('newsbot_last_toot_id')

if since_id:
    mentions = mastodon.notifications(types=["mention"], since_id=since_id.decode("utf-8"))
else:
    mentions = mastodon.notifications(types=["mention"])
for mention in mentions[::-1]:
    soup = BeautifulSoup(mention["status"]["content"], features="lxml")
    toot_text = soup.get_text()
    print(toot_text)
    # Only process direct mentions
    if toot_text.lower().startswith("@trovenewsbot"):
        toot_json = json.dumps(mention["status"], sort_keys=True, default=str)
        #result = toot_queue.enqueue(process_toot, toot_json)
        process_toot(toot_json)
        print(toot_json)
        #mastodon.notifications_dismiss(mention["id"])
    redis_client.set('newsbot_last_toot_id', mention["id"])
