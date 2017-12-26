"""
Этот модуль сожержит класс DataBase, реализующий работу с базой данных
"""
import os
from urllib import parse
import psycopg2



parse.uses_netloc.append("postgres")
url = parse.urlparse(os.environ["DATABASE_URL"])


class DataBase:
    """
    Реализует интерфейс работы с базой данных
    Note:
        У пользователя прямого доступа к классу нет
    Attributes:
        conn (:class:`connection`): Дескриптор подключения к базе данных
        cur (:class:`cursor`): Перо для выполнения PostgreSQL команд.
    Args:
        conn (:class: `connection`): Дескриптор подключения к базе данных.
            Создается подключение между программой и базой данных, созданная
            в приложении в сервисе Heroku.
        cur (:class: `cursor`): Перо для выполнения PostgreSQL команд.
            Создается и связывается с текущим соединением к базе данных.

    """

    def __init__(self):
        self.conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        self.cur = self.conn.cursor()

    def __del__(self):
        self.conn.close()
        self.cur.close()

    # add film to database
    def AddFilmToLibrary(self, user_id, imdb_id):
        """
        Добавление фильма в базу данных
        Args:
            user_id (int): номер чата
            imdb_id (int): id фильма на сайте *imdb.com*
        Returns:
            str: Возвращает строку статуса:
                {
                    "added user_id, imdb_id to database": успешное добавление фильма в базу данных
                    "this title already in user - %s database": фильм уже в базе данных

                }

        """
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
        """
        Проверка библиотеки пользователя на наличие в ней фильма
        Args:
            user_id (int): id пользователя
            imdb_id (int): id фильма на сайте *imdb.com*
        Returns:
            bool : True если нет, False в противном случае
        """
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
        """
        Проверка на вхождение субтитров в базу данных
        Args:
            imdb_id (int): id фильма на сайте *imdb.com*
        Returns:
            bool : True если нет, False в противном случае
        """
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
        """
        Добавление слов к фильму в базу данных
        Args:
            imdb_id (int): id фильма на сайте *imdb.com*
            word (str) : слово
        """
        word_id = self.GetWordID(word)
        self.cur.execute(
            """INSERT INTO subtitle_words (imdb_id, word_id) VALUES (%s,%s);""",
            (imdb_id, word_id)
        )
        self.conn.commit()

    def GetWordID(self, word):
        """
        Возвращает id слова
        Args:
            word (str) : слово
        Returns:
            :obj:`int`: id слова
        """
        self.cur.execute(
            """SELECT id FROM words WHERE word=\'{}\'
            """.format(word)
        )
        res = self.cur.fetchall()
        if len(res) != 0:
            return res[0][0]
        else:
            return (self.AddToIDList(word))

    def AddToIDList(self, word):
        """
        Добавляет слово в базу данных
        Args:
            word (str) : слово
        Returns:
            :obj:`int`: id слова
        """
        self.cur.execute(
            """SELECT max(id) FROM words"""
        )
        curr_id = (self.cur.fetchall())[0][0]
        if (curr_id):
            curr_id += 1
        else:
            curr_id = 1

        self.cur.execute(
            """INSERT INTO words (id, word) VALUES (%s,%s);""",
            (curr_id, word)
        )
        self.conn.commit()
        return curr_id

    def LearnWord(self, word_id, user_id):
        """
        Добавляет слово в таблицу изученных слов
        Args:
            word_id (int) : id слова
            user_id (int) : id  пользователя
        """
        self.cur.execute(
            """INSERT INTO user_words (chat_id, word_id) VALUES (%s,%s);""",
            (user_id, word_id)
        )
        self.conn.commit()

    def GetWordsForTitle(self, user_id, imdb_id):
        """
        Возвращает слов к фильму исключив изученные пользователем слова
        Args:
            user_id (int) : id  пользователя
            imdb_id (int) : id фильма на сайте *imdb.com*
        Returns:
            dic (dict): слова:
                + id слова из таблицы words
                + слово
        """
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
            ON nuw.word_id = w.id ORDER BY w.id;""", (imdb_id, user_id)
                         )
        dic = {}
        i = 0
        for label in self.cur.fetchall():
            dic[i] = label
            i += 1
        return dic

    def GetUserLibrary(self, user_id):
        """
        Возвращает библиотеку пользователя с фильмами
        Args:
            user_id (int) : id  пользователя
        Returns:
            dic (dict): фильмы:
                + index
                + imdb_id
        """
        self.cur.execute(
            """SELECT * FROM user_films WHERE chat_id={}""".format(user_id)
        )
        dic = {}
        i = 0
        for label in self.cur.fetchall():
            dic[i] = label
            i += 1
        return dic

    def AddSubtitleToLibrary(self, subtitle_id, imdb_id, episode, season):
        """
        Добавляет информацию о фильме в базу данных

        Args:
            subtitle_id (int): id субтитров с сайта *opensubtitles.org*
            imdb_id (int): id фильма с сайта *imdb.com*
            episode (int) : номер эпизода
            season (int) : номер сезона
        """
        f = self.GetSubtitleID(imdb_id)
        if not f:
            self.cur.execute(
                """INSERT INTO subtitle_imdb (subtitle_id, imdb_id, season, episode)
                    VALUES (%s, %s, %s, %s);""",
                (subtitle_id, imdb_id, season, episode)
            )
            self.conn.commit()

    def GetSubtitleID(self, imdb_id):
        """
        Возвращает id субтитров
        Args:
            imdb_id (int): id фильма с сайта *imdb.com*
        Returns:
            (int): id субтитров с сайта *opensubtitles.org*
        """
        self.cur.execute(
            """SELECT subtitle_id FROM subtitle_imdb WHERE imdb_id=\'{}\'
            """.format(imdb_id)
        )
        res = self.cur.fetchall()
        if len(res) != 0:
            return res[0][0]
        else:
            return None

    def GetSeriesInfo(self, imdb_id):
        """
        Возвращает дополнительную информацию о фильме
        Args:
            imdb_id (int): id фильма с сайта *imdb.com*
        Returns:
            dic (dict): информация о сериале :
                + season
                + episode
        """
        self.cur.execute(
            """SELECT season, episode FROM subtitle_imdb WHERE imdb_id=\'{}\'"""
                .format(imdb_id)
        )
        res = self.cur.fetchall()
        dic = {}
        if (res):
            if res[0][0] != None:
                dic["season"] = res[0][0]
                dic["episode"] = res[0][1]
                return dic
        else:
            return None

    def GetDefinition(self, word):
        """
        Возвращает определение для слова
        Args:
            word (str): слово
        Returns:
            str : определение
        """
        self.cur.execute(
            """SELECT definition FROM words WHERE word=\'{}\'
            """.format(word)
        )
        res = self.cur.fetchall()
        if len(res) != 0:
            return res[0][0]
        else:
            return None

    def AddDefinition(self, word, definition):
        """
        Добавить определение для слова в базу данных
        Args:
            word (str): слово
            definition (str): определение для слова

        """
        self.cur.execute(
            """UPDATE words SET definition = %s WHERE word = %s;""",
            (definition, word)
        )
        self.conn.commit()

    def DeleteFilmFromLibrary(self, user_id, imdb_id):
        """
        Удалить фильм из библиотеки пользователя
        Args:
            user_id (int): id пользователя
            imdb_id (int): id фильма на сайте *imdb.com*
        """
        self.cur.execute(
            """DELETE FROM user_films WHERE chat_id=%s AND imdb_id=%s;""",
            (user_id, imdb_id)
        )
        self.conn.commit()

    def AddSentence(self, word, imdb_id, sentence):
        """
        Занести предложение из субитров к слову в базу данных
        Args:
            word (str): слово
            imdb_id (int): id фильма на сайте *imdb.com*
            sentence (str): преложение
        """
        word_id = self.GetWordID(word)
        self.cur.execute(
            """UPDATE subtitle_words SET sentence = %s WHERE word_id = %s AND imdb_id=%s;""",
            (sentence, word_id, imdb_id)
        )
        self.conn.commit()

    def GetSentence(self, word, imdb_id):
        """
        Возвращает предложение к слову в определеном фильме
        Args:
            word (str): слово
            imdb_id (int): id фильма на сайте *imdb.com*
        Returns:
            str: предложение к слову
        """
        word_id = self.GetWordID(word)
        self.cur.execute(
            """SELECT sentence FROM subtitle_words WHERE word_id=%s AND imdb_id=%s;""",
            (word_id, imdb_id)
        )
        res = self.cur.fetchall()
        if len(res) != 0:
            return res[0][0]
        else:
            return None
