from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
import logging
logging.basicConfig(format="""%(asctime)s - %(name)s -
                        %(levelname)s - %(message)s""",
                    level=logging.INFO)

logger = logging.getLogger(__name__)
def get_navigate_markup(dic , index=0):

    # if len(dic) > 1:
    #     buttons.append(dict('←',
    #                         callback_data='navigate_%s_%d' % (str_json, (index - 1) % len(dic))))

    button_list = [
        InlineKeyboardButton("⬅️", callback_data="n_%s_%d"%(str(dic),(index - 1)%len(dic))),
        InlineKeyboardButton("ok", callback_data="s_%s_%d"%(str(dic),index)),
        InlineKeyboardButton("➡️", callback_data="n_%s_%d"%(str(dic),(index + 1)%len(dic)))
    ]
    return  InlineKeyboardMarkup(build_menu(button_list, n_cols=3))

    # buttons.append('ok',
        #                     callback_data='select_%s_%d' % (dic, index % len(dic)))
    # if len(dic) > 1:
    #     buttons.append(dict('→',
    #                         callback_data='navigate_%s_%d' % (str_json, (index + 1) % len(dic))))

def library_navigate_markup(len, index=0):
    button_list = [
        InlineKeyboardButton("⬅️", callback_data="ln_%s" % str((index - 1) % len)),
        InlineKeyboardButton("ok", callback_data="ls_%s" % str((index))),
        InlineKeyboardButton("➡️", callback_data="ln_%s" % str((index + 1) % len))
    ]
    return InlineKeyboardMarkup(build_menu(button_list, n_cols=3))

def main_menu(update):
    keyboard = [[InlineKeyboardButton("Add new subs",
                                          callback_data='search')],
                    [InlineKeyboardButton("My Library",
                                          callback_data='learn')],
                    ]
    return InlineKeyboardMarkup(keyboard)

def render_navigate_markup(reply_markup, dic, update , index):
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


# def learning_navigate_markup(dic, index = 0):
#     #TODO back here
#     logger.info("Navigating")
#     button_list = []
#     if  index - 5>=0:
#         button_list.append(InlineKeyboardButton("⬅️", callback_data="ln_%s_%d" % (str(dic), (index - 5))))
#     if  index + 5 <=len(dic):
#         button_list.append(InlineKeyboardButton("➡️", callback_data="ln_%s_%d" % (str(dic), (index + 5))))
#     count = 0
#     for x in dic:
#         if count == 5:
#             break
#         count+=1
#         button_list.append(InlineKeyboardButton("%s"%x[1], callback_data="ln_%s" % (str(dic))))
#
#
#
#
#     return InlineKeyboardMarkup(build_menu(button_list, n_cols=3))