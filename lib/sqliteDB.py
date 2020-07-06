import sqlite3
from contextlib import closing
from random import randrange


class SqliteDB:

    def __init__(self, path):
        self.path = path
        with closing(sqlite3.connect(self.path)) as dbc:
            cur = dbc.cursor()
            cur.execute("select * from sqlite_master where type= 'table'")
            f = False
            for table in cur.fetchall():
                f |= (table[2] == "problems")

            if not f:
                print("[DB] table \"problems\" not found!")
                print("[DB] create table...")
                cur.execute("create table problems("
                            "id text, title text, contest_id text, contest_title text, status text, point double, "
                            "difficulty double, primary key(id))")
                print("[DB] create table Done.")

    def appendDBFromJson(self, json):

        with closing(sqlite3.connect(self.path)) as dbc:
            cur = dbc.cursor()
            # 更新のため全削除
            cur.execute("delete from problems where True")
            for key in json.keys():
                data = json[key]
                diff = "NULL" if data["difficulty"] is None else data["difficulty"]
                point = "NULL" if data["point"] == -1 else data["point"]
                sql = "insert into problems(id, title, contest_id, contest_title, status, point, difficulty)" \
                      "values('{}','{}','{}','{}','{}',{},{})" \
                    .format(key, data["title"], data["contest_id"], data["contest_title"], data["status"], point, diff)
                # print("[DB] Execute SQL Statement: {}".format(sql))
                cur.execute(sql)
            dbc.commit()
            dbc.close()

    def getDataWithSelector(self, selector):
        plist = []
        plist_id = []
        with closing(sqlite3.connect(self.path)) as dbc:
            cur = dbc.cursor()
            for s in selector:
                dup_check = True
                candidate = []
                while dup_check:
                    sql = "select * from problems where {} >= {} and {} <= {}" \
                        .format(s["column"], s["range"]["lower"], s["column"], s["range"]["upper"])
                    cur.execute(sql)

                    select_list = cur.fetchall()
                    idx = randrange(select_list.__len__())
                    candidate = select_list[idx]
                    dup_check = (candidate[0] in plist_id)
                plist.append(candidate)
                plist_id.append(candidate[0])
            dbc.close()

        return plist


