import os
import json
import time
import urllib3
import certifi as cert
from lib.sqliteDB import SqliteDB


class ProblemDB:

    def __init__(self, user):
        print("Initialize...")
        # 変数初期化
        self.db_json = {}
        self.path = {
            "dlList": "data/downloadList.json",
            "dbPath": "data/problem.db",
            "cacheLog": "cache/cacheLog.json",
            "alias": "data/selectorAlias.json"
        }
        self.request = urllib3.PoolManager(
            cert_reqs="CERT_REQUIRED",
            ca_certs=cert.where()
        )
        self.apiRequestHeader = {
            "accept-encoding": "gzip"
        }
        self.db = SqliteDB(self.path["dbPath"])
        self.isfileUpdated = False
        self.username = user
        self.problemURL = []
        self.problemURL_template = "https://atcoder.jp/contests/{}/tasks/{}"

        with open(self.path["dlList"], "r") as f:
            self.dlList = json.load(f)

        self.update_judge()
        if self.isfileUpdated:
            self.construct_db()

        print("Initialize Done.")

    # jsonの更新が必要かチェック
    def update_judge(self):
        if not os.path.exists(self.path["cacheLog"]):
            with open(self.path["cacheLog"], mode="w", encoding="utf-8") as f:
                f.write("{}")
            self.update()
            self.isfileUpdated = True
        else:
            with open(self.path["cacheLog"], mode="r", encoding="utf-8") as f:
                clog = json.load(f)
            for key in clog.keys():
                if clog[key]["next_update"] < time.time():
                    print("FileID: {} has expired.".format(key))
                    self.update_file(key)
                    self.isfileUpdated = True

    # ファイルをすべて更新
    def update(self):
        print("File All Update...")
        for fid in self.dlList.keys():
            self.update_file(fid)
        print("All Update Done.")

    # fileidのファイルを更新
    def update_file(self, fileid):
        print("File Update... -> {}".format(fileid))
        target = self.dlList[fileid]["url"]
        res = self.request.request("GET", target.format(self.username), headers=self.apiRequestHeader)
        epoch = int(time.time())

        # ファイルにAPIのデータを書き込み
        res_json = json.loads(res.data)

        with open("cache/{}".format(self.dlList[fileid]["fileName"]), mode="w", encoding="utf-8") as f:
            json.dump(res_json, f, indent=4, ensure_ascii=False)

        # cacheLog.jsonを更新
        with open(self.path["cacheLog"], "r") as f:
            clog = json.load(f)

        clog[fileid] = {}
        clog[fileid]["fileName"] = self.dlList[fileid]["fileName"]
        clog[fileid]["latest_update"] = epoch
        clog[fileid]["next_update"] = epoch + self.dlList[fileid]["update_span"]

        with open(self.path["cacheLog"], mode="w", encoding="utf-8") as f:
            json.dump(clog, f, indent=4, sort_keys=True)

        print("File Update Done.")

    # jsonからdbを構築
    def construct_db(self):
        print("DB update...")

        db_raw = {}
        status = {}
        contests = {}

        with open(self.path["dlList"], mode="r", encoding="utf-8") as f:
            f_list = json.load(f)
        for fileID in f_list.keys():
            with open("cache/{}".format(f_list[fileID]["fileName"]), mode="r", encoding="utf-8") as f:
                db_raw[fileID] = json.load(f)

        for submit in db_raw["userSubmission"]:
            if (submit["problem_id"] in status.keys()) and (status[submit["problem_id"]] != "AC"):
                status[submit["problem_id"]] = submit["result"]
            else:
                status[submit["problem_id"]] = "AC"

        for contest in db_raw["contestList"]:
            contests[contest["id"]] = contest["title"]

        for problem in db_raw["problemList"]:
            pid = problem["id"]
            self.db_json[pid] = {
                "title": problem["title"].replace("'", "''"),
                "contest_id": problem["contest_id"],
                "status": status[pid] if pid in status.keys() else "Trying",
                "contest_title": contests[problem["contest_id"]].replace("'","''"),
                "point_status": "Normal"
            }
            if (pid in db_raw["diffList"]) and ("difficulty" in db_raw["diffList"][pid]):
                self.db_json[pid]["difficulty"] = db_raw["diffList"][pid]["difficulty"]
            else:
                self.db_json[pid]["difficulty"] = None
            if not problem["point"] is None:
                self.db_json[pid]["point"] = problem["point"]
            elif not problem["predict"] is None:
                self.db_json[pid]["point"] = problem["predict"]
                self.db_json[pid]["point_status"] = "Predict"
            else:
                self.db_json[pid]["point"] = -1
                self.db_json[pid]["point_status"] = "None"

        with open("data/db.json", mode="w", encoding="utf-8") as f:
            json.dump(self.db_json, f, indent=4, ensure_ascii=False)

        self.db.appendDBFromJson(self.db_json)

        print("DB update Done.")

    # selectorに合致する問題をランダムに選ぶ
    def choose(self, selector):
        with open(self.path["alias"], mode="r") as f:
            a_list = json.load(f)
            for key in a_list.keys():
                if selector == a_list[key]["alias"]:
                    selector = a_list[key]["selector"]

        illegal = False
        s_list = selector.split("-")
        selector_list = []
        for s in s_list:
            if (s[0] == "p") or (s[0] == "d"):
                s_param = s[1:]
                param = s_param[1:-1].split(":") if ":" in s_param else [int(s_param)] * 2
                obj = {
                    "column": "point" if s[0] == "p" else "difficulty",
                    "range": {
                        "upper": param[1],
                        "lower": param[0]
                    }
                }
                selector_list.append(obj)

            else:
                illegal = True
                break

        """
        # CUIに出力する
        if illegal:
            print("Invalid Selector.")
        else:
            task = self.db.getDataWithSelector(selector_list)
            for i, t in enumerate(task):
                print("{}\n"
                      "problemName: {}\n"
                      "\tcontest: {}\n"
                      "\tpoint: {}\n"
                      "\tdifficulty: {}\n"
                      .format(i+1, t[1], t[2], t[4], t[5]))
        """
        self.problemURL = []
        if illegal:
            return ["Invalid Selector."]
        else:
            task = self.db.getDataWithSelector(selector_list)
            for t in task:
                self.problemURL.append(self.problemURL_template.format(t[2], t[0]))
            return task

        # return ["Invalid Selector."] if illegal else self.db.getDataWithSelector(selector_list)

    def getProblemURLFromIndex(self, index):
        return self.problemURL[index]

    def getAllProblemURL(self):
        return self.problemURL
