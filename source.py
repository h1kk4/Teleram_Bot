from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
import logging
from subs import OpenSubtitles
from settings import Settings
import telegram.replykeyboardmarkup

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

global Token
Token = OpenSubtitles()

def start(bot, update):
    update.message.reply_text('Этот бот предоставляет следующий функционал:\n'
                              '/add "title" - Добавить субтитры к изучению\n'
                              '/learn "title" - начать изучать слова\n'
                              '/stop "title" - закончить изучать слова\n')


    print("Hi")

def help(bot, update):
    update.message.reply_text('/add "title" - Добавить субтитры к изучению\n'
                              '/learn "title" - начать изучать слова\n'
                              '/stop "title" - закончить изучать слова\n')

def echo(bot, update):
    update.message.reply_text(update.message.text)

def search(bot,update):
    print(update.message.text.split(" ", 1)[1])
    labels = Token.search_movies_on_imdb(update.message.text.split(" ", 1)[1])
    str = ''
    i = 0
    keyboard = []
    for label in labels['data']:
        str += label["title"] + '\n'
        keyboard += [[InlineKeyboardButton(label["title"],'',callback_data=label["id"])]]
        i+=1
        if (i==6):
            break

    reply_markup=InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)

def unknown(bot, update):
     bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")

def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

def button(bot, update):
    query = update.callback_query
    print(query.data)
    print(Token.download_subtitles(query.data))
    bot.edit_message_text(text="Yor are selected: %s" % query.data,
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)



def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():

    updater = Updater("My_Token")

    dp = updater.dispatcher

    Token.login(Settings.USER_NAME, Settings.USER_PASSWORD)
    print("this ---> ",Token.token)

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("search", search))

    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.text, echo))

    dp.add_error_handler(error)
    dp.add_handler(MessageHandler(Filters.command, unknown))
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()