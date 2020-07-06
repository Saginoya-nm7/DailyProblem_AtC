from requests_oauthlib import OAuth1Session
import requests.status_codes as http_status
import json


class TwitterAPI:

    def __init__(self, client_key, client_secret, access_key, access_secret):
        self.client = OAuth1Session(client_key, client_secret, access_key, access_secret)

    def getTimeline(self, count):
        endpoint = "https://api.twitter.com/1.1/statuses/user_timeline.json"
        param = {"count": count}
        res = self.client.get(url=endpoint, params=param)

        return responseParser(res)

    def tweet(self, tweet: str):
        endpoint = "https://api.twitter.com/1.1/statuses/update.json"
        param = {"status": tweet}
        res = self.client.post(url=endpoint, params=param)

        return responseParser(res)


def responseParser(resObj) -> dict:
    if resObj.status_code != http_status.codes.ok:
        return {"error": resObj.status_code}
    return json.loads(resObj.text)
