"""Этот модуль сожержит строки
Args:

    Настойки для OpenSubtitles Api:
        OPENSUBTITLES_SERVER :obj:`str`: - адрес сервера
        USER_AGENT :obj:`str`: - User Agent
        LANGUAGE :obj:`str`: - язык
        USER_NAME :obj:`str`: -  username
        USER_PASSWORD :obj:`str`: - пароль


    EmptyLibraryTxt :obj:`str`: - строка сообщения при пустой библиотеке
    HelpTxt :obj:`str`: - строка при вызове /help
    NotInMenuTxt :obj:`str`: - строка сообщения, если пользователь не в меню
    telegram_token :obj:`str`: - стока с токеном для Telegram
    OMDBapikey :obj:`str`: - стока с токеном для OMDB Api
    YADICT_KEY :obj:`str`: - стока с токеном для Yandex Dictionary
    YATRANSLATE_KEY :obj:`str`: - стока с токеном для Yandex Translater
    MASHAPE_KEY :obj:`str`: - стока с токеном для mashape

"""
from os import environ

class Settings(object):

    OPENSUBTITLES_SERVER = ["OPENSUBTITLES_SERVER"]
    USER_AGENT = ["USER_AGENT"]
    LANGUAGE = ["LANGUAGE"]
    USER_NAME = ["USER_NAME"]
    USER_PASSWORD = environ["USER_PASSWORD"]

    EmptyLibraryTxt = "You have not added any movies yet.\n " \
                      "Open /menu to add new titles."

    HelpTxt = "Hi!\n" \
              "This Bot help's you to learn new english words.\n" \
              "Send me /menu to start.\n" \
              'Tap on "Add new subs" to add new title to you library.\n' \
              'Tap on "My Library" to chose title and start learn words.'

    NotInMenuTxt = "Ooops.\n" \
                   "You are not in menu. To search for titles just open /menu."

    telegram_token = environ["telegram_token"]

    OMDBapikey = environ["OMDBapikey"]
    YADICT_KEY = environ["YADICT_KEY"]
    YATRANSLATE_KEY = ["YATRANSLATE_KEY"]
    MASHAPE_KEY = ["MASHAPE_KEY"]
