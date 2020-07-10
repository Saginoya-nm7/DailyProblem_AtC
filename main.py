from lib.problemDB import ProblemDB
import config
from lib.Twitter import TwitterAPI

problemDB = ProblemDB(config.USER_NAME)

problem = problemDB.choose(config.PROBLEM_SELECTOR)

twitter = TwitterAPI(
    client_key=config.APP_KEY,
    client_secret=config.APP_SEC,
    access_key=config.ACC_KEY,
    access_secret=config.ACC_SEC
)
rep = None
for i, p in enumerate(problem):
    tweet = config.TWEET_HEADER[i != 0] + \
            config.TWEET_TEMPLATE[p[6] == "Normal"].format(
                color=config.TWEET_PROBLEM_COLOR[i],
                title=p[1],
                contest_title=p[3],
                point=int(p[5]),
                url=config.URL_TEMPLATE.format(p[2], p[0])
            )
    res = twitter.tweet(tweet=tweet, reply_id=rep)
    rep = res["id"]
