from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
import logging
import yadict
import wordsapi
import urbandict

logging.basicConfig(format="""%(asctime)s - %(name)s -
                        %(levelname)s - %(message)s""",
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def get_navigate_markup(len, index=0):
    # if len(dic) > 1:
    #     buttons.append(dict('←',
    #                         callback_data='navigate_%s_%d' % (str_json, (index - 1) % len(dic))))

    button_list = []
    k = 1
    if len > 1:
        button_list.append(InlineKeyboardButton("⬅️", callback_data="n_%s" % str((index - 1) % len)))
        k += 1

    button_list.append(InlineKeyboardButton("ok", callback_data="s_%s" % (str(index))), )

    if len > 1:
        button_list.append(InlineKeyboardButton("➡️", callback_data="n_%s" % str((index + 1) % len)))
        k += 1

    return InlineKeyboardMarkup(build_menu(button_list, n_cols=k))

    # buttons.append('ok',
    #                     callback_data='select_%s_%d' % (dic, index % len(dic)))
    # if len(dic) > 1:
    #     buttons.append(dict('→',
    #                         callback_data='navigate_%s_%d' % (str_json, (index + 1) % len(dic))))


def library_navigate_markup(len, index=0):
    button_list = [ ]
    if len > 1:
        button_list.append(InlineKeyboardButton("⬅️", callback_data="ln_%s" % str((index - 1) % len)))

    button_list.append(InlineKeyboardButton("ok", callback_data="ls_%s" % str((index))))

    if len > 1:
        button_list.append(InlineKeyboardButton("➡️", callback_data="ln_%s" % str((index + 1) % len)))

    return InlineKeyboardMarkup(build_menu(button_list, n_cols=3))


def main_menu():
    keyboard = [[InlineKeyboardButton("Add new subs",
                                      callback_data='search')],
                [InlineKeyboardButton("My Library",
                                      callback_data='learn')],

                ]
    return InlineKeyboardMarkup(keyboard)


def library_menu(index):
    keyboard = [[InlineKeyboardButton("Get list of words",
                                      callback_data='lm1_%s' % index)],
                [InlineKeyboardButton("Get words one by one",
                                      callback_data='lm2_%s' % index)],

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
        out = out + "%s) *%s* \n" % (str(index), str(dic[index][1]))
        k += 1
        index += 1
    return out


def learn_navigate_markup(dic ,index, len, title):
    logger.info("Learn navigate")
    button_list = []
    head = []
    if (index - 4) < 0:
        k = 0
    else:
        k = index - 5
    head.append(InlineKeyboardButton(" 📋⬅️ ", callback_data="len_%s_%s_" % (str(k), str(title))))
    if index + 5 <= len - 1:
        head.append(InlineKeyboardButton("➡️📋", callback_data="len_%s_%s_" % (str(index + 5), str(title))))
    k = 0
    while (k <= 4 and index <= len - 1):
        button_list.append(InlineKeyboardButton("%s" % dic[index][1], callback_data="les_%s_%s_" % (index, str(title))))
        k += 1
        index += 1

    finish = [(InlineKeyboardButton("Finish ✅", callback_data="ln_%s" % str(title)))]
    return InlineKeyboardMarkup(build_menu(button_list, n_cols=5, header_buttons=head, footer_buttons=finish))


def learn_card(index, title, flag=""):
    # TODO вывод предложения
    button_list = [ ]
    k = 2
    button_list.append( InlineKeyboardButton("Get sentence with this word",
                                             callback_data="sentence_%s_%s_%s" % (str(index), str(title), str(flag))))

    if flag=="":
        button_list.append(InlineKeyboardButton("Got it 👌", callback_data="learned_%s_" % (str(index))))
        k+=1
    logger.info("flag in learn card - %s" % flag)
    go_back = [InlineKeyboardButton("⬅️ Go back",
                                    callback_data="les_%s_%s_%s" % (str(index), str(title), str(flag)))]
    return InlineKeyboardMarkup(build_menu(button_list, n_cols=k, footer_buttons=go_back))

def go_back(index, title, flag=""):
    go_back = [[InlineKeyboardButton("⬅️ Go back",
                                    callback_data="len_%s_%s_%s" % (str(index), str(title), str(flag)))]]
    return InlineKeyboardMarkup(go_back)

def learn_navigate_markup_simple_version(index, len, title):
    logger.info("Learn navigate (simple)")
    button_list = [
        InlineKeyboardButton("don't know", callback_data="les_%s_%s_1" % (str(index), str(title))),
        InlineKeyboardButton("already know", callback_data="learned_%s_%s" % (str(index), str(title)))
    ]
    logger.info("index - %s, title - %s"%(index, title))
    finish = [(InlineKeyboardButton("Finish ✅", callback_data="ln_%s" % str(title)))]
    if (index + 1) == len:
        return InlineKeyboardMarkup(finish)
    return InlineKeyboardMarkup(build_menu(button_list, n_cols=2, footer_buttons=finish))


def get_card(word):
    logger.info("creating word card")
    card = wordsapi.get_cards(word)
    print("card wordsapi", card)
    if not card:
        card = yadict.get_card(word)
    if not card:
        card = urbandict.get_card(word)

    if card:
        ts = yadict.get_transcription(word)
        if ts:
            card['ts'] = ts

        card["translation"] = yadict.get_translations(word)
        print(yadict.get_translations(word))
        return card
    return None


def get_study_card(card):
    # TODO in urbandict add 'scr' column
    logger.info("get word card ")
    out = ""
    print(card)
    if (card['src'] == 'wordsapi'):
        logger.info("yadict search")
        out += "Word - *%s*\n" % str(card['word'])
        out += "Transcription - %s\n" % str(card['pron'])
        out += "Definitions :\n"
        for label in card['def']:
            out += " - _%s_\n" % str(label)

    elif (card['src'] == "yadict"):
        logger.info("yadict search")
        out += "Word - *%s*\n" % str(card['word'])
        if 'ts' in card:
            out += "Transcription - %s\n" % str(card['ts'])
        out += "Synonyms :\n"
        for label in card['syn']:
            out += " - _%s_\n" % str(label)
    else:
        out += "Word - *%s*\n" % str(card['word'])
        for x in card['def']:
            for y in x:
                out += " - _%s - %s_ \n" % (str(y['text']), str(y['type']))
    if 'translation' in card:
        out += "Translation - %s" % card['translation']
    return out
