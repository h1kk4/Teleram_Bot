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
from utils import Utils
from cards import *
from subtitles_download import *
import ast

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
        self.menu(update)
        return logger.info("done start")

    def menu(self, update):
        logger.info("Menu")
        reply_markup = main_menu(update)
        # reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard= True ,one_time_keyboard=True)
        update.message.reply_text('Please choose what you want to do:',
                                  reply_markup=reply_markup)

    def help(self, update):
        logger.info("help")
        update.message.reply_text(Settings.HelpTxt)

    def SearchSubsMethod(self, bot, update, flag, id):
        logger.info("Method Search")

        if (flag == 0):
            logger.info("Film Method")
            self.Download_Subtitles(id)
            flags[update.callback_query.message.chat_id].set_flag_search(False)
        else:
            logger.info("Series Method")
            title = self.Ask_For_Season_Episode(bot, id, update)

    def Download_Subtitles(self, title):

        return

    def Ask_For_Season_Episode(self, bot, id, update):

        flags[update.callback_query.message.chat_id].set_flag_series(True)
        flags[update.callback_query.message.chat_id].set_id_series(id)
        flags[update.callback_query.message.chat_id].set_flag_search(False)
        logger.info("asked")
        bot.edit_message_text(text="Send me season and number of series \n"
                                   "in that format S1 E1",
                              chat_id=update.callback_query.message.chat_id,
                              message_id=update.callback_query.message.message_id)

    def search_title_or_episode(self, bot, update):

        logger.info("Search for %s" % update.message.text)
        logger.info("OpenSubtitles token %s" % OPExample.login())
        if (flags[update.message.chat_id].get_flag_series() == True):
            flags[update.message.chat_id].set_flag_series(False)
            title = OMDBExample.search_title(flags[update.message.chat_id].get_id_series()) + " "
            id_of_series = OMDBExample.search_series(title + update.message.text)
            logger.info("Id of episode of %s%s" % (title, id_of_series))
            bot.send_message(chat_id=update.message.chat_id, text="http://imdb.com/title/%s" % id_of_series)
        # добавить поиск по сериалам в следуещем формате
        # title уже известен, нужно вызвать OMDBsearch  добавиви к строки тайтла Title S2 E9
        if (flags[update.message.chat_id].get_flag_search() == True):
            labels = OPExample.search_movies_on_imdb(update.message.text)
            logger.info('Fill out the cards on request "%s"' % update.message.text)
            dic = {}
            i = 0
            print("labels", labels)
            if (labels['data'] != [[]]):
                for label in labels['data']:
                    dic[i] = [self.what_run(label['title'], update), label['id']]
                    i += 1
                    if (i == 3):
                        logger.info("Dic to send %s" % dic)

                        index = 0

                        reply_markup = get_navigate_markup(dic, index)
                        render_navigate_markup(reply_markup, dic, index, update)
                        # reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard= True ,one_time_keyboard=True)
                        # update.message.reply_text("http://imdb.com/title/tt%s" % dic[index][1], reply_markup=reply_markup)
                        break

            else:
                bot.send_message(chat_id=update.message.chat_id, text="I can't find this title")
                logger.exception("Nothing found")

        OPExample.logout()

    def what_run(self, str, update):
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

        if (query.data == 'search_for_subtitles'):
            bot.edit_message_text(text="Please send me the name of the title: ",
                                  chat_id=chat_id,
                                  message_id=query.message.message_id)

            flags[chat_id] = Flags()
            flags[chat_id].set_flag_search(True)

        if ((query.data.split('_')[0]) == 's'):
            data = dict(ast.literal_eval(query.data.split('_')[1]))
            index = int(query.data.split('_')[2])

            logger.info("index %s, flag %s, title %s" % (index, data[index][0], data[index][1]))

            self.SearchSubsMethod(bot, update, data[index][0], data[index][1])

            logger.info("selected")
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
        return logger.info("done button method")

    def unknown(self, bot, update):
        bot.send_message(chat_id=update.message.chat_id,
                         text="Sorry, I don't understand that command.")

    def Error(self, bot, update, error):
        logger.warn('Update "%s" caused error "%s"' % (update, error))

    def AddHandler(self):
        self.dispatcher.add_handler(CommandHandler("start", self.start))

        self.dispatcher.add_handler(CommandHandler("help", self.help))

        self.dispatcher.add_handler(MessageHandler(Filters.text, self.search_title_or_episode))

        self.dispatcher.add_handler(CallbackQueryHandler(self.button))

        self.dispatcher.add_error_handler(self.Error)

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
