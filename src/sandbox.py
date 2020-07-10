from lib.Twitter import TwitterAPI
import config
from pprint import pprint

twitter = TwitterAPI(
    client_key=config.APP_KEY,
    client_secret=config.APP_SEC,
    access_key=config.ACC_KEY,
    access_secret=config.ACC_SEC
)

pprint(twitter.tweet(tweet="にゃーん"))
