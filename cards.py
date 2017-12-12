from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
import logging
import yadict
import wordsapi
import urbandict
from db import DataBase
from opensubtitles import OpenSubtitles
from subtitles_download import *

logging.basicConfig(format="""%(asctime)s - %(name)s -
                        %(levelname)s - %(message)s""",
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def get_navigate_markup(len, index=0):
    k = 1
    button_list = []
    if len > 1:
        button_list.append(InlineKeyboardButton("⬅️", callback_data="n_%s" % str((index - 1) % len)))  # navigate
        k += 1

    button_list.append(InlineKeyboardButton("ok", callback_data="s_%s" % (str(index))), )  # select

    if len > 1:
        button_list.append(InlineKeyboardButton("➡️", callback_data="n_%s" % str((index + 1) % len)))
        k += 1

    return InlineKeyboardMarkup(build_menu(button_list, n_cols=k))


def library_navigate_markup(len, index=0):
    button_list = []

    if len > 1:
        button_list.append(
            InlineKeyboardButton("⬅️", callback_data="ln_%s" % str((index - 1) % len)))  # library_navigate

    button_list.append(InlineKeyboardButton("ok", callback_data="ls_%s" % str((index))))  # library_select

    if len > 1:
        button_list.append(InlineKeyboardButton("➡️", callback_data="ln_%s" % str((index + 1) % len)))

    delete = [(InlineKeyboardButton("delete from library", callback_data="delete_%s" % str(index)))]

    return InlineKeyboardMarkup(build_menu(button_list, n_cols=3, footer_buttons=delete))


def main_menu():
    keyboard = [[InlineKeyboardButton("Add new subs",
                                      callback_data='search')],
                [InlineKeyboardButton("My Library",
                                      callback_data='learn')],

                ]
    return InlineKeyboardMarkup(keyboard)


def Show_keyboard():
    logger.info("Show KEYBOARD")
    custom_keyboard = [['/menu'], ['/help']]
    return ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True)


def library_menu(index):
    keyboard = [[InlineKeyboardButton("Get list of words",
                                      callback_data='lm1_%s' % index)],  # library menu 1
                [InlineKeyboardButton("Get words one by one",
                                      callback_data='lm2_%s' % index)],  # library menu 2

                ]
    return InlineKeyboardMarkup(keyboard)


def render_navigate_markup(reply_markup, dic, update, index=0):
    update.message.reply_text("http://imdb.com/title/tt%s" % dic[index][1], reply_markup=reply_markup)
    logger.info("render_navigate_markup")


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


def get_learn_list(dic, index=0):
    k = 0
    out = ''
    while (k <= 4 and index <= len(dic) - 1):
        out = out + "%s) *%s* \n" % (str(index + 1), str(dic[index][1]))
        k += 1
        index += 1
    return out


def learn_navigate_markup(dic, index, len, title):
    logger.info("Learn navigate")
    button_list = []
    head = []

    if (index - 5) < 0:
        k = 0
    else:
        k = index - 5

    if (index != 0):
        head.append(InlineKeyboardButton(" 📋⬅️ ", callback_data="len_%s_%s_0_0" % (str(k), str(title))))

    if index + 5 <= len - 1:
        head.append(InlineKeyboardButton("➡️📋", callback_data="len_%s_%s_0_0" % (str(index + 5), str(title))))
    k = 0
    while (k <= 4 and index <= len - 1):
        button_list.append(
            InlineKeyboardButton("%s" % dic[index][1], callback_data="les_%s_%s_" % (str(index), str(title))))
        k += 1
        index += 1

    finish = [(InlineKeyboardButton("Finish ✅", callback_data="finish"))]
    return InlineKeyboardMarkup(build_menu(button_list, n_cols=5, header_buttons=head, footer_buttons=finish))


def learn_card(index, title, flag):
    button_list = []
    # button_list.append(InlineKeyboardButton("Get sentence with this word",
    #                                         callback_data="sentence_%s_%s_%s" % (str(index), str(title), str(flag))))

    button_list.append(InlineKeyboardButton("Got it 👌",
                                            callback_data="learned_%s_%s_%s_1" % (str(index), str(title), str(flag))))
    logger.info("flag in learn card - %s" % flag)
    go_back = [InlineKeyboardButton("⬅️ Go back",
                                    callback_data="len_%s_%s_%s_1" % (str(index), str(title), str(flag)))]
    return InlineKeyboardMarkup(build_menu(button_list, n_cols=2, footer_buttons=go_back))


def learn_navigate_markup_simple_version(index, len, title):
    logger.info("Learn navigate (simple)")
    k = 2
    button_list = [
        InlineKeyboardButton("don't know", callback_data="les_%s_%s_1" % (str(index), str(title))),
        InlineKeyboardButton("already know", callback_data="learned_%s_%s_1_0" % (str(index), str(title)))

    ]
    if len > 1:
        button_list.append(InlineKeyboardButton("next word",
                                                callback_data="len_%s_%s_1_0" % (str((index + 1) % len), str(title))))
        k += 1
    logger.info("index - %s, title - %s" % (index, title))
    finish = [(InlineKeyboardButton("Finish ✅", callback_data="finish"))]
    if (index + 1) == len:
        return InlineKeyboardMarkup(finish)
    return InlineKeyboardMarkup(build_menu(button_list, n_cols=k, footer_buttons=finish))


def get_card(word, imdb_id):
    logger.info("creating word card")
    postgre = DataBase()
    if (postgre.GetDefinition(word) != None):
        logger.info("%s - already in database" % word)
        card = eval(postgre.GetDefinition(word))
        sentence = get_sentence(word, imdb_id)
        if sentence:
            card['sentence'] = sentence
        return card
    logger.info("adding information about '%s' to database" % word)
    card = wordsapi.get_cards(word)
    if not card:
        card = yadict.get_card(word)
    if not card:
        card = urbandict.get_card(word)

    if card:
        ts = yadict.get_transcription(word)
        sentence = get_sentence(word, imdb_id)

        if ts:
            card['ts'] = ts
        card["translation"] = yadict.get_translations(word)
        postgre.AddDefinition(word, str(card))
        if sentence:
            card['sentence'] = sentence

        return card
    return None


def get_sentence(word, imdb_id):
    OP = OpenSubtitles()
    logger.info("Getting sentence, OpenSubtitles token %s" % OP.login())
    postgre = DataBase()
    sentence = postgre.GetSentence(word, imdb_id)
    if sentence:
        return sentence
    subtitle_id = postgre.GetSubtitleID(imdb_id)
    logger.info("subtitle id - %s" % subtitle_id)
    FileData = (OP.download_subtitles([subtitle_id]))
    sentence = search_sentence(FileData['data'][0]['data'], word)
    OP.logout()
    if sentence:
        postgre.AddSentence(word, imdb_id, sentence)
        return sentence
    else:
        return None


def get_study_card(card):
    logger.info("get word card ")
    out = ""
    if (card['src'] == 'wordsapi'):
        logger.info("yadict search")
        out += "*Word* - %s\n" % str(card['word'])
        out += "*Transcription* - \[%s] \n" % str(card['pron'])
        out += "*Definitions* :\n"
        for label in card['def']:
            out += " - _%s_\n" % str(label)

    elif (card['src'] == "yadict"):
        logger.info("yadict search")
        out += "*Word* - \[%s]\n" % str(card['word'])
        if 'ts' in card:
            out += "*Transcription* \[%s]   \n" % str(card['ts'])
        out += "*Synonyms* :\n"
        for label in card['syn']:
            out += " - _%s_\n" % str(label)
    else:
        out += "*Word* - \[%s]\n" % str(card['word'])
        for x in card['def']:
            for y in x:
                out += " - _%s - %s_ \n" % (str(y['text']), str(y['type']))
    if 'translation' in card:
        out += "*Translation* - %s\n" % card['translation']
    if 'sentence' in card:
        out += "*Sentence with this word*\n - %s" % card['sentence']
    return out
