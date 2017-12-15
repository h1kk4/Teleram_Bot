from telegram import ParseMode
from telegram.ext import Updater, CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram.ext import CallbackQueryHandler
from flags import Flags
from SearchByOMDB import OMDB
from settings import Settings
from cards import *
from subtitles_download import *
from db import DataBase
from imdb import IMDb
# Enable logging
logging.basicConfig(format="""%(asctime)s - %(name)s -
                        %(levelname)s - %(message)s""",
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class SubsBot:
    def __init__(self, Token):
        self.__token = Token
        self.updater = Updater(self.__token)
        self.dispatcher = self.updater.dispatcher

    def start(self, bot, update):
        logger.info("Method start")
        reply_markup = Show_keyboard()
        bot.send_message(text=Settings.HelpTxt,
                         chat_id=update.message.chat_id,
                         reply_markup=reply_markup)

    def menu(self, bot, update):
        reply_markup = main_menu()
        update.message.reply_text('Here is menu\n'
                                  'Chose what you want to do:',
                                  reply_markup=reply_markup)

    def help(self, bot, update):
        logger.info("help")
        update.message.reply_text(Settings.HelpTxt)

    def SearchSubsMethod(self, bot, update, flag, id):
        logger.info("Search for Subtitles")
        if (flag == 0):
            logger.info("Film Method")
            flags[update.callback_query.message.chat_id].set_flag_search(False)
            postgre = DataBase()
            if (self.download_subtitles(bot, update, id, flag="film")):
                logger.info("%s" % postgre.AddFilmToLibrary(update.callback_query.message.chat_id, id))
        else:
            logger.info("Series Method")
            self.ask_for_season_episode(bot, id, update)

    def download_subtitles(self, bot, update, id, flag, episode=None, season=None):
        logger.info("Download method OpenSubtitles token %s" % OPExample.login())
        if flag == "series":
            chat_id = update.message.chat_id
        else:
            chat_id = update.callback_query.message.chat_id
        postgre = DataBase()
        if postgre.CheckSubtitlesLibrary(id):
            IDSubtitleFile = self.search_subs_on_opensubtitles(id)
            if IDSubtitleFile == '':
                bot.send_message(text="Sorry, I can't find any subtitles",
                                 chat_id=chat_id)
                return False

            FileData = (OPExample.download_subtitles([IDSubtitleFile]))
            data = get_words_set(FileData['data'][0]['data'])
            self.add_words_to_db(id, data)
            self.add_subtitle_to_db(imdb_id=id, subtitle_id=IDSubtitleFile, episode=episode, season=season)
        else:
            logger.info("subtitles for title -%s already in library" % id)
        bot.send_message(text="To start learn, open /menu and go to your library",
                         chat_id=chat_id)

        OPExample.logout()
        return True

    def add_words_to_db(self, imdb_id, data):
        logger.info("adding words to database")
        postgre = DataBase()
        for label in data:
            postgre.AddWordsToLibrary(imdb_id=imdb_id, word=label)

    def add_subtitle_to_db(self, imdb_id, subtitle_id, episode=None, season=None):
        logger.info("adding imdb_id - %s subtitle_id - %s to database" % (imdb_id, subtitle_id))
        postgre = DataBase()
        postgre.AddSubtitleToLibrary(subtitle_id=subtitle_id, imdb_id=imdb_id, episode=episode, season=season)

    def search_subs_on_opensubtitles(self, id):
        request_data = [{"sublanguageid": 'eng', 'imdbid': id}]
        idSubtitleFile = OPExample.search_subtitles(request_data)
        found_id = ''
        for label in idSubtitleFile['data']:
            if label['SubFormat'] == 'srt':
                found_id = (label['IDSubtitleFile'])
                logger.info("found id %s" % found_id)
                break

        return found_id

    def ask_for_season_episode(self, bot, id, update):

        flags[update.callback_query.message.chat_id].set_flag_series(True)
        flags[update.callback_query.message.chat_id].set_id_series(id)
        flags[update.callback_query.message.chat_id].set_flag_search(False)

        logger.info("asked")

        bot.edit_message_text(text="Send me season and number of series \n"
                                   "in that format S1 E1",
                              chat_id=update.callback_query.message.chat_id,
                              message_id=update.callback_query.message.message_id)

    def text_handler(self, bot, update):

        if update.message.chat_id not in flags:
            self.help(bot, update)
            return



        # Search for episode of the series

        if (flags[update.message.chat_id].get_flag_series() == True):
            logger.info("Search for episode %s" % update.message.text)
            self.search_subtitles_for_episode(bot, update)

        # Searching for name of the titles (filling thw menu of titles)

        elif(flags[update.message.chat_id].get_flag_search() == True):
            logger.info("Search for title %s" % update.message.text)
            self.titles_search(bot, update)

        else:
            update.message.reply_text(Settings.NotInMenuTxt)


    def search_subtitles_for_episode(self, bot, update):
        flags[update.message.chat_id].set_flag_series(False)
        logger.info("OpenSubtitles token %s" % OPExample.login())

        data = update.message.text.split()
        episode = data.pop()[1:]
        season = data.pop()[1:]

        request_data = [{"sublanguageid": 'eng', 'imdbid': flags[update.message.chat_id].get_id_series()}]
        id_of_series = ''
        title = ''
        for label in ((OPExample.search_subtitles(request_data))['data']):
            if label["SeriesSeason"] == season and label["SeriesEpisode"] == episode:
                title = label["MovieName"]
                id_of_series = label["IDMovieImdb"]
                id_of_series = "tt" + id_of_series
                OPExample.logout()
                break

        # if nothing been found on opensubtitles
        if id_of_series == '':
            title = OMDBExample.get_title(flags[update.message.chat_id].get_id_series()) + " "
            if title:
                data = OMDBExample.search_series(title + update.message.text)
            else:
                bot.send_message(text="Sorry, I can't find any subtitles",
                                 chat_id=update.message.chat_id)
                return

            if data != {}:
                id_of_series = data.imdb_id
            else:
                bot.send_message(text="Sorry, I can't find any subtitles",
                                 chat_id=update.message.chat_id)
                return
        OPExample.logout()
        logger.info("Id of episode of %s%s" % (title, id_of_series))

        bot.send_message(chat_id=update.message.chat_id, text="http://imdb.com/title/%s" % id_of_series)
        postgre = DataBase()
        if (self.download_subtitles(bot=bot,
                                    update=update,
                                    id=id_of_series[2:],
                                    episode=episode,
                                    season=season,
                                    flag="series")):
            logger.info("%s" % postgre.AddFilmToLibrary(update.message.chat_id, id_of_series[2:]))

        OPExample.logout()

    def titles_search(self, bot, update):

        logger.info('Fill out the cards on request "%s"' % update.message.text)
        dic = {}
        i = 0

        """"""
        ia = IMDb()
        movies = ia.search_movie(update.message.text)
        if movies != []:
            for item in movies:
                dic[i] = [self.what_run(item['kind']),item.movieID ]
                i+=1

            reply_markup = get_navigate_markup(len(dic))
            render_navigate_markup(reply_markup, dic, update)
            flags[update.message.chat_id].set_titles(dic)
            return

        logger.info("OpenSubtitles token %s" % OPExample.login())
        labels = OPExample.search_movies_on_imdb(update.message.text)

        if (labels['data'] != [[]]):
            for label in labels['data']:
                if 'id' not in label:
                    continue
                logger.info("Opensubtitles")

                dic[i] = [self.what_run(label['title']), label['id']]
                i += 1
            reply_markup = get_navigate_markup(len(dic))
            render_navigate_markup(reply_markup, dic, update)
            flags[update.message.chat_id].set_titles(dic)

        elif (OMDBExample.search_film(update.message.text)):
            logger.info("OMDB")
            label = OMDBExample.search_film(update.message.text)
            dic[0] = [label['type'], label['imdb_id']]

            reply_markup = get_navigate_markup(len(dic))
            render_navigate_markup(reply_markup, dic, update)
            flags[update.message.chat_id].set_titles(dic)

        else:
            bot.send_message(chat_id=update.message.chat_id, text="I can't find this title")
            logger.exception("Nothing found")

        OPExample.logout()

    def what_run(self, str):
        data = str.lower()
        if (data.find("tv series") != -1):
            logger.info("set flag series")
            return 1
        else:
            logger.info("set flag film")
            return 0

    def user_data(self, chat_id):
        words = flags[chat_id].get_words()
        library = flags[chat_id].get_library()
        dic = {'words': words, 'library': library}
        return dic

    def button(self, bot, update):

        logger.info("Method button")

        query = update.callback_query
        chat_id = query.message.chat_id
        #
        if (query.data == 'search'):
            # Search for new title

            bot.edit_message_text(text="Please send me the name of the title: ",
                                  chat_id=chat_id,
                                  message_id=query.message.message_id)
            flags[chat_id] = Flags()
            flags[chat_id].set_flag_search(True)

        if (query.data == 'learn'):
            # Render user library
            self.render_library(bot, query, chat_id)

        if ((query.data.split('_')[0]) == 's'):
            # User select title to learn

            data = flags[chat_id].get_titles()
            index = int(query.data.split('_')[1])
            logger.info("select button index %s, flag %s, title %s" % (index, data[index][0], data[index][1]))
            self.SearchSubsMethod(bot, update, data[index][0], data[index][1])

            logger.info("selected")

        if ((query.data.split('_')[0]) == 'n'):
            # Chosen navigation button in searching

            data = flags[chat_id].get_titles()
            index = int(query.data.split('_')[1])
            logger.info("index %s, flag %s, title %s" % (index, data[index][0], data[index][1]))
            reply_markup = get_navigate_markup(len(data), index)
            bot.edit_message_text(text="http://imdb.com/title/tt%s" % data[index][1],
                                  reply_markup=reply_markup,
                                  chat_id=chat_id,
                                  message_id=query.message.message_id)

            logger.info("navigate in searching")

        if ((query.data.split('_')[0]) == 'ls'):
            # Chosen title to learn from user library

            index = int(query.data.split("_")[1])  # index in dic of users library
            dic = flags[chat_id].get_library()
            title = dic[index][1]  # title - imdb_id of film/series
            logger.info("index %s title %s" % (index, dic[index][1]))

            reply_markup = library_menu(index)

            bot.edit_message_text(text="Chose how you want to learn words",
                                  reply_markup=reply_markup,
                                  chat_id=chat_id,
                                  message_id=query.message.message_id)

            logger.info(("User selected title - %s to learn") % title)

        if ((query.data.split('_')[0]) == "lm1"):
            # First version of learning card

            index = int(query.data.split("_")[1])  # index in dic of users library
            dic = flags[chat_id].get_library()
            title = dic[index][1]  # title - imdb_id of film/series
            logger.info("index %s title %s" % (index, dic[index][1]))

            postgre = DataBase()
            flags[chat_id].set_words(postgre.GetWordsForTitle(chat_id, title))

            words = flags[chat_id].get_words()
            reply_markup = learn_navigate_markup(words, 0, len(words), index)

            bot.edit_message_text(
                text="*%s* words left to learn for this title\n%s" % (len(words), get_learn_list(words)),
                reply_markup=reply_markup,
                chat_id=chat_id,
                message_id=query.message.message_id,
                parse_mode=ParseMode.MARKDOWN)

        if ((query.data.split('_')[0]) == "lm2"):
            # Second version of learning card

            index = int(query.data.split("_")[1])  # index in dic of users library
            dic = flags[chat_id].get_library()
            title = dic[index][1]  # title - imdb_id of film/series
            logger.info("index %s title %s" % (index, dic[index][1]))

            postgre = DataBase()
            flags[chat_id].set_words(postgre.GetWordsForTitle(chat_id, title))

            words = flags[chat_id].get_words()
            reply_markup = learn_navigate_markup_simple_version(0, len(words), index)
            bot.edit_message_text(
                text="*%s* words left to learn for this title\n word - *%s*" % (len(words), words[0][1]),
                reply_markup=reply_markup,
                chat_id=chat_id,
                message_id=query.message.message_id,
                parse_mode=ParseMode.MARKDOWN)

        if ((query.data.split('_')[0]) == 'ln'):
            # Chosen navigation button in library

            index = int(query.data.split("_")[1])
            dic = flags[chat_id].get_library()
            logger.info("index %s title " % (index))
            # , dic[index][1]))
            reply_markup = library_navigate_markup(len(dic), index)

            text_out = "http://imdb.com/title/tt%s" % dic[index][1]
            postgre = DataBase()

            series_info = postgre.GetSeriesInfo(dic[index][1])
            if (series_info):
                text_out += "\n *Season* - %s *Episode* - %s" % (series_info['season'], series_info['episode'])
            bot.edit_message_text(text=text_out,
                                  reply_markup=reply_markup,
                                  chat_id=chat_id,
                                  message_id=query.message.message_id,
                                  parse_mode=ParseMode.MARKDOWN)
            logger.info("navigate in library")

        if ((query.data.split('_')[0]) == 'len'):
            # Chosen navigation button in learning menu
            self.navigation_in_learning_card(bot, query, chat_id)

        if ((query.data.split('_')[0]) == 'les'):
            # Chose word to get more information

            index = int(query.data.split("_")[1])
            title = int(query.data.split("_")[2])
            flag = query.data.split("_")[3]
            dic = flags[chat_id].get_words()
            logger.info("Word to learn - %s" % dic[index][1])
            card = get_card(dic[index][1], flags[chat_id].get_library()[title][1])

            if flag == "1":
                reply_markup = learn_card(index, title, '1')
            else:
                reply_markup = learn_card(index, title, '0')

            if card:
                text_out = get_study_card(card)
            else:
                text_out = "Nothing been found"

            bot.edit_message_text(text=text_out,
                                  reply_markup=reply_markup,
                                  chat_id=chat_id,
                                  message_id=query.message.message_id,
                                  parse_mode=ParseMode.MARKDOWN)

        if (query.data.split('_')[0] == 'learned'):
            # User said that he know this word
            self.learn_func(bot, query, chat_id)

        if (query.data == "finish"):
            # Finish studying

            flags[chat_id].reset_words()
            flags[chat_id].reset_library()
            reply_markup = main_menu()
            bot.edit_message_text(text="Please choose what you want to do:",
                                  reply_markup=reply_markup,
                                  chat_id=chat_id,
                                  message_id=query.message.message_id)

        if (query.data.split("_")[0] == "delete"):
            # Delete title from user library
            self.delete_title_from_library(bot, query, chat_id)

        return logger.info("done button method")

    def delete_title_from_library(self, bot, query, chat_id):

        index = int(query.data.split("_")[1])
        data = flags[chat_id].get_library()
        logger.info("deleting %s" % data[index][1])
        postgre = DataBase()
        postgre.DeleteFilmFromLibrary(chat_id, data[index][1])

        flags[chat_id] = Flags()
        flags[chat_id].set_library(postgre.GetUserLibrary(chat_id))
        dic = flags[chat_id].get_library()
        print(dic)
        if dic == {}:
            bot.edit_message_text(text=Settings.EmptyLibraryTxt,
                                  chat_id=chat_id,
                                  message_id=query.message.message_id)
            return

        index = index % len(dic)
        text_out = "http://imdb.com/title/tt%s" % dic[index][1]
        series_info = postgre.GetSeriesInfo(dic[index][1])
        if (series_info):
            text_out += "\n *Season* - %s *Episode* - %s" % (series_info['season'], series_info['episode'])

        reply_markup = library_navigate_markup(len(dic), index)
        bot.edit_message_text(text=text_out,
                              chat_id=chat_id,
                              message_id=query.message.message_id,
                              reply_markup=reply_markup,
                              parse_mode=ParseMode.MARKDOWN)

    def render_library(self, bot, query, chat_id):
        postgre = DataBase()
        flags[chat_id] = Flags()
        flags[chat_id].set_library(postgre.GetUserLibrary(chat_id))
        library = flags[chat_id].get_library()
        if library == {}:
            bot.edit_message_text(text=Settings.EmptyLibraryTxt,
                                  chat_id=chat_id,
                                  message_id=query.message.message_id, )
            return
        text_out = "http://imdb.com/title/tt%s" % library[0][1]
        series_info = postgre.GetSeriesInfo(library[0][1])
        if (series_info):
            text_out += "\n *Season* - %s *Episode* - %s" % (series_info['season'], series_info['episode'])
        reply_markup = library_navigate_markup(len(library))
        bot.edit_message_text(text=text_out,
                              chat_id=chat_id,
                              message_id=query.message.message_id,
                              reply_markup=reply_markup,
                              parse_mode=ParseMode.MARKDOWN)

        logger.info("rendered library list for %s " % chat_id)

    def navigation_in_learning_card(self, bot, query, chat_id):
        index = int(query.data.split("_")[1])
        title = int(query.data.split("_")[2])
        words = flags[chat_id].get_words()
        logger.info("index %s word %s" % (index, words[index][1]))

        if (query.data.split("_")[3] == "0"):
            reply_markup = learn_navigate_markup(words, index, len(words), title)
            text_out = get_learn_list(words, index)
            logger.info("navigate in learning")
        else:
            reply_markup = learn_navigate_markup_simple_version(index, len(words), title)
            text_out = "*%s*" % words[index][1]
            logger.info("navigate in learning (simple)")

        if (query.data.split("_")[4] == "0"):
            bot.edit_message_text(text=text_out,
                                  reply_markup=reply_markup,
                                  chat_id=chat_id,
                                  message_id=query.message.message_id,
                                  parse_mode=ParseMode.MARKDOWN)
        else:
            bot.edit_message_reply_markup(reply_markup=None,
                                          chat_id=chat_id,
                                          message_id=query.message.message_id)
            bot.send_message(text=text_out,
                             reply_markup=reply_markup,
                             chat_id=chat_id,
                             parse_mode=ParseMode.MARKDOWN)

    def learn_func(self, bot, query, chat_id):
        index = int(query.data.split("_")[1])
        title_id = int(query.data.split("_")[2])
        word = flags[chat_id].get_words()
        dic = flags[chat_id].get_library()
        title = dic[title_id][1]  # title - imdb_id of film/series
        logger.info("Learned word is - %s" % word[index][1])
        postgre = DataBase()
        postgre.LearnWord(word[index][0], chat_id)

        flags[chat_id].set_words(postgre.GetWordsForTitle(chat_id, title))  # Update words for title
        words = flags[chat_id].get_words()
        if (query.data.split("_")[3] == '1'):  # if user in simple learn card
            logger.info("learned word and get another")

            index += 1
            index = index % len(words)
            text_out = "*%s*" % words[index][1]
            reply_markup = learn_navigate_markup_simple_version(index, len(words), title_id)
            if (query.data.split("_")[4] == '1'):
                logger.info("Got it! Card will stay in history")

                bot.edit_message_reply_markup(reply_markup=None,
                                              chat_id=chat_id,
                                              message_id=query.message.message_id)
                bot.send_message(text=text_out,
                                 reply_markup=reply_markup,
                                 chat_id=chat_id,
                                 message_id=query.message.message_id,
                                 parse_mode=ParseMode.MARKDOWN)
            else:
                logger.info("User know word! Card would not stay in history")

                bot.edit_message_text(text=text_out,
                                      reply_markup=reply_markup,
                                      chat_id=chat_id,
                                      message_id=query.message.message_id,
                                      parse_mode=ParseMode.MARKDOWN)
        else:
            logger.info("index %s title %s" % (index, dic[title_id][1]))

            reply_markup = learn_navigate_markup(words, index, len(words), title_id)
            text_out = get_learn_list(words, index)
            bot.edit_message_reply_markup(reply_markup=None,
                                          chat_id=chat_id,
                                          message_id=query.message.message_id)

            bot.send_message(text=text_out,
                             reply_markup=reply_markup,
                             chat_id=chat_id,
                             message_id=query.message.message_id,
                             parse_mode=ParseMode.MARKDOWN
                             )

            logger.info("navigate in learning")

    def error(self, update, error):
        logger.warn('Update "%s" caused error "%s"' % (update, error))

    def AddHandler(self):

        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(CommandHandler("help", self.help))
        self.dispatcher.add_handler(CommandHandler("menu", self.menu))

        self.dispatcher.add_handler(MessageHandler(Filters.text, self.text_handler))
        self.dispatcher.add_handler(CallbackQueryHandler(self.button))
        self.dispatcher.add_error_handler(self.error)

    def startBot(self):

        self.AddHandler()
        self.updater.start_polling()
        self.updater.idle()


if __name__ == '__main__':
    OPExample = OpenSubtitles()
    OMDBExample = OMDB()
    flags = {}
    bot = SubsBot(Settings.telegram_token)
    bot.startBot()
