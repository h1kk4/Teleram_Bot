from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove, File
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler
from telegram.ext import MessageHandler, Filters, Dispatcher, Job
from telegram.ext import CallbackQueryHandler, RegexHandler, ChosenInlineResultHandler
import logging
from flags import Flags
from opensubtitles import OpenSubtitles
from SearchByOMDB import OMDB
from settings import Settings
from cards import *
import base64
import zlib
import ast
from subtitles_download import *
from db import DataBase

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
        self.Show_keyboard(bot, update)
        return logger.info("done start")

    def menu(self, bot, update):
        logger.info("Menu")
        reply_markup = main_menu(update)
        # reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard= True ,one_time_keyboard=True)
        update.message.reply_text('Please choose what you want to do:',
                                  reply_markup=reply_markup)

    def Show_keyboard(self, bot, update):
        logger.info("Show KEYBOARD")
        custom_keyboard = [['/menu'], ['/help']]
        reply_markup = ReplyKeyboardMarkup(custom_keyboard)
        bot.send_message(text="Hi!",
                         chat_id=update.message.chat_id,
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
            logger.info("%s" % postgre.AddFilmToLibrary(update.callback_query.message.chat_id, id))
            self.download_subtitle_for_film(bot, update, id)
        else:
            logger.info("Series Method")
            self.ask_for_season_episode(bot, id, update)


    def download_subtitle_for_film(self, bot, update, id):
        logger.info("Download method OpenSubtitles token %s" % OPExample.login())
        postgre = DataBase()
        if postgre.CheckSubtitlesLibrary(id):
            IDSubtitleFile = self.search_subs_on_opensubtitles(id)
            if IDSubtitleFile == '':
                print(update)
                bot.send_message(text="Sorry, I can't find any subtitles",
                                 chat_id=update.message.chat_id)

            FileData = (OPExample.download_subtitles([IDSubtitleFile]))
            data = get_clear_string(FileData['data'][0]['data'])
        else:
            logger.info("subtitles for this title -%s already in library" % id)

            bot.send_message(text="this title is already in your library",
                             chat_id=update.message.chat_id)
        OPExample.logout()

    def download_subtitle_for_series(self, bot, update, id):
        logger.info("Download method OpenSubtitles token %s" % OPExample.login())
        postgre = DataBase()
        if postgre.CheckSubtitlesLibrary(id):
            IDSubtitleFile = self.search_subs_on_opensubtitles(id)
            if IDSubtitleFile == '':
                print(update)
                bot.send_message(text="Sorry, I can't find any subtitles",
                                 chat_id=update.callback_query.message.chat_id)

            FileData = (OPExample.download_subtitles([IDSubtitleFile]))
            data = get_clear_string(FileData['data'][0]['data'])
        else:
            logger.info("subtitles for this title -%s already in library" % id)

            bot.send_message(text="this title is already in your library",
                             chat_id=update.callback_query.message.chat_id)
        OPExample.logout()
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

    def search_title_or_episode(self, bot, update):



        if not flags:
            bot.send_message(chat_id=update.message.chat_id, text="Send /help to get instructions")
            return

        logger.info("Search for %s" % update.message.text)
        #
        # Search for episode of the series
        #
        if (flags[update.message.chat_id].get_flag_series() == True):
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
            if id_of_series == '':
                title = OMDBExample.get_title(flags[update.message.chat_id].get_id_series()) + " "
                id_of_series = OMDBExample.search_series(title + update.message.text)

            logger.info("Id of episode of %s%s" % (title, id_of_series))

            bot.send_message(chat_id=update.message.chat_id, text="http://imdb.com/title/%s" % id_of_series)
            postgre = DataBase()
            logger.info("%s" % postgre.AddFilmToLibrary(update.message.chat_id, id_of_series[2:]))
            self.download_subtitle_for_series(bot, update, id_of_series[2:])

        #
        # Searching for name of the title
        #

        if (flags[update.message.chat_id].get_flag_search() == True):
            labels = OPExample.search_movies_on_imdb(update.message.text)
            logger.info('Fill out the cards on request "%s"' % update.message.text)
            dic = {}
            i = 0
            if (labels['data'] != [[]]):
                for label in labels['data']:
                    dic[i] = [self.what_run(label['title']), label['id']]
                    i += 1
                    if (i == 3):
                        logger.info("Dic to send %s" % dic)

                        reply_markup = get_navigate_markup(dic)
                        render_navigate_markup(reply_markup, dic, update)
                        break

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

    def button(self, bot, update):
        logger.info("Method button")
        query = update.callback_query
        chat_id = query.message.chat_id
        #
        if (query.data == 'search'):
            bot.edit_message_text(text="Please send me the name of the title: ",
                                  chat_id=chat_id,
                                  message_id=query.message.message_id)

            flags[chat_id] = Flags()
            flags[chat_id].set_flag_search(True)
        #
        #
        if (query.data == 'learn'):
            bot.edit_message_text(text="Chose from list",
                                  chat_id=chat_id,
                                  message_id=query.message.message_id)

            postgre = DataBase()

            dic = postgre.GetUserLibrary(chat_id)
            if dic == {}:
                bot.send_message(text="You have not added any movies yet",
                                 chat_id=chat_id)
                return
            reply_markup = library_navigate_markup(len(dic))
            bot.send_message(text="http://imdb.com/title/tt%s" % dic[0][1],
                                  chat_id=chat_id,
                                  message_id=query.message.message_id,
                                  reply_markup=reply_markup)
            logger.info("rendered library list for %s " % chat_id)
        #
        #
        if ((query.data.split('_')[0]) == 's'):  # TODO LEARN METHOD
            data = dict(ast.literal_eval(query.data.split('_')[1]))
            index = int(query.data.split('_')[2])
            logger.info("select button index %s, flag %s, title %s" % (index, data[index][0], data[index][1]))

            self.SearchSubsMethod(bot, update, data[index][0], data[index][1])
                # bot.edit_message_text(text="OK",
                #                       chat_id=chat_id,
                #                       message_id=query.message.message_id,
                #                       )


            logger.info("selected")
        #
        #
        if ((query.data.split('_')[0]) == 'n'):
            data = dict(ast.literal_eval(query.data.split('_')[1]))
            index = int(query.data.split('_')[2])
            logger.info("index %s, flag %s, title %s" % (index, data[index][0], data[index][1]))
            reply_markup = get_navigate_markup(data, index)
            # render_navigate_markup(reply_markup, data, index, update)
            bot.edit_message_text(text="http://imdb.com/title/tt%s" % data[index][1],
                                  reply_markup=reply_markup,
                                  chat_id=chat_id,
                                  message_id=query.message.message_id)
            logger.info("navigate")

        if ((query.data.split('_')[0]) == 'ls'):  # TODO LEARN METHOD
            index = query.data.split("_")[1]
            postgre = DataBase()
            dic = postgre.GetUserLibrary(chat_id)

            logger.info("index %s title %s" % (index, dic[index][1]))

                # bot.edit_message_text(text="OK",
                #                       chat_id=chat_id,
                #                       message_id=query.message.message_id,
                #                       )


            logger.info("User  selected title to learn")

        if ((query.data.split('_')[0]) == 'ln'):
            index = int(query.data.split("_")[1])
            logger.info("index - %s"%index)
            postgre = DataBase()
            dic = postgre.GetUserLibrary(chat_id)

            logger.info("index %s title %s" % (index, dic[index][1]))

            reply_markup = library_navigate_markup(len(dic), index)
            bot.edit_message_text(text="http://imdb.com/title/tt%s" % dic[index][1],
                                  reply_markup=reply_markup,
                                  chat_id=chat_id,
                                  message_id=query.message.message_id)
            logger.info("navigate")

        return logger.info("done button method")


    def unknown(self, bot, update):
        bot.send_message(chat_id=update.message.chat_id,
                         text="Sorry, I don't understand that command.")

    def error(self, bot, update, error):
        logger.warn('Update "%s" caused error "%s"' % (update, error))

    def AddHandler(self):

        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(CommandHandler("help", self.help))
        self.dispatcher.add_handler(CommandHandler("menu", self.menu))

        self.dispatcher.add_handler(MessageHandler(Filters.text, self.search_title_or_episode))
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
