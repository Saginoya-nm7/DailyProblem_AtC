from lib.problemDB import ProblemDB
import config
from lib.Twitter import TwitterAPI


problemDB = ProblemDB(config.USER_NAME)

problem = problemDB.choose(config.PROBLEM_SELECTOR)[0]

tweet = config.TWEET_TEMPLATE[problem[6] == "Normal"].format(
    title=problem[1],
    contest_title=problem[3],
    point=int(problem[5]),
    url=config.URL_TEMPLATE.format(problem[2], problem[0])
)

twitter = TwitterAPI(
    client_key=config.APP_KEY,
    client_secret=config.APP_SEC,
    access_key=config.ACC_KEY,
    access_secret=config.ACC_SEC
)

twitter.tweet(tweet=tweet)
