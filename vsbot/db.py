import sqlite3


class BotDB:
    def __init__(self, db_name: str = "bot.db"):
        self.db = sqlite3.connect(db_name)

        # https://stackoverflow.com/questions/3300464/how-can-i-get-dict-from-sqlite-query
        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d

        self.db.row_factory = dict_factory
        self.prepare_db()

    def prepare_db(self):
        cur = self.db.cursor()
        cur.execute("create table if not exists users(uid integer, fname text, username text)")
        cur.close()
        self.db.commit()

    def new_user(self, uid: int, fname: str, username: str):
        cur = self.db.cursor()
        if self.get_user(uid):
            return False

        cur.execute("insert into users values(:uid, :fname, :username)", (uid, fname, username))
        cur.close()
        self.db.commit()
        return True

    def get_user(self, uid: int):
        cur = self.db.cursor()
        rq = cur.execute("select * from users where uid=:uid", {"uid": uid}).fetchall()
        try:
            return rq[0]
        except IndexError:
            return None

    def get_users(self):
        cur = self.db.cursor()
        rq = cur.execute("select * from users").fetchall()
        return rq


    def get_users_ids(self):
        cur = self.db.cursor()
        rq = cur.execute("select * from users").fetchall()
        return [user["uid"] for user in rq]

