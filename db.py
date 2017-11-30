import os
from urllib import parse
import psycopg2

#parse.uses_netloc.append("postgres")
#url = parse.urlparse(os.environ["DATABASE_URL"])


class DataBase:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname='db_for_bot',
            user='alex'
            # database=url.path[1:],
            # user=url.username,
            # password=url.password,
            # host=url.hostname,
            # port=url.port
        )
        self.cur = self.conn.cursor()

    def __del__(self):
        self.conn.close()
        self.cur.close()

    def AddFilmToLibrary(self, user_id, imdb_id):
        f = self.CheckUserLibrary(user_id, imdb_id)
        if f:
            self.cur.execute(
                """INSERT INTO user_films (chat_id, imdb_id)
                    VALUES (%s, %s);""",
                (user_id, imdb_id)
            )
            self.conn.commit()
            return "added %s, %s to database" % (user_id, imdb_id)
        else:
            return "this title already in user - %s database" % user_id

    def CheckUserLibrary(self, user_id, imdb_id):
        self.cur.execute(
            """SELECT * FROM user_films WHERE chat_id=\'{}\'
                AND imdb_id=\'{}\'
            """.format(user_id, imdb_id)
        )
        res = self.cur.fetchall()
        if len(res) == 0:
            return True
        else:
            return False

    def CheckSubtitlesLibrary(self, imdb_id):
        self.cur.execute(
            """SELECT * FROM subtitle_words WHERE imdb_id=\'{}\'
            """.format(imdb_id)
        )
        res = self.cur.fetchall()
        if len(res) == 0:
            return True
        else:
            return False

    def AddWordsToLibrary(self, imdb_id, word):

        word_id = self.GetWordID(word)
        self.cur.execute(
            """INSERT INTO subtitle_words (imdb_id, word_id) VALUES (%s,%s);""",
            (imdb_id, word_id)
        )
        self.conn.commit()

        return "Create"

    def GetWordID(self, word):
        self.cur.execute(
            """SELECT * FROM words WHERE word=\'{}\'
            """.format(word)
        )
        res = self.cur.fetchall()
        if len(res) == 0:
            return res[0][0]
        else:
            return (self.AddToIDList(word))

    def AddToIDList(self, word):
        self.cur.execute(
            """SELECT * FROM words where id in (SELECT max(id) FROM words GROUP BY word ) order by id desc"""
        )
        curr_id = self.cur.fetchall()[0][0] + 1

        self.cur.execute(
            """INSERT INTO words (id, word) VALUES (%s,%s);""",
            (curr_id, word)
        )
        self.conn.commit()
        return curr_id

    def LearnWord(self, word, user_id):
        self.cur.execute(
            """INSERT INTO user_words (chat_id, word) VALUES (%s,%s);""",
            (user_id, word)
        )
        self.conn.commit()

    def GetWordsForTitle(self, user_id, imdb_id):
        self.cur.execute("""
            SELECT w.id, w.word
            FROM (
                SELECT sw.word_id
                FROM (
                    SELECT word_id
                    FROM subtitle_words
                    WHERE imdb_id = %s
                ) AS sw
                LEFT JOIN (
                    SELECT word_id
                    FROM user_words
                    WHERE chat_id = %s
                ) AS uw
                ON sw.word_id = uw.word_id
                WHERE uw.word_id IS NULL
            ) AS nuw
            LEFT JOIN words AS w
            ON nuw.word_id = w.id;""", (imdb_id, user_id)
                         )
        return ((self.cur.fetchall()))

    def GetUserLibrary(self, user_id):

        self.cur.execute(
            """SELECT * FROM user_films WHERE chat_id={}""".format(user_id)
        )
        dic = {}
        i = 0
        for label in self.cur.fetchall():
            dic[i]=label
            i+=1
        print("it's dic", dic)
        return dic