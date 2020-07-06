from lib.problemDB import ProblemDB
import config

urlTemplate = "https://atcoder.jp/contests/{}/tasks/{}"
problemDB = ProblemDB(config.USER_NAME)

problem = problemDB.choose("d[400:800]")[0]
print(problem)
print(config.TWEET_TEMPLATE[problem[6] == "Normal"].format(
    title=problem[1], contest_title=problem[3], point=int(problem[5]), url=urlTemplate.format(problem[2], problem[0]))
)
