#!/usr/bin/env python
import pymysql
import pymysql.cursors

connection = pymysql.connect(host='127.0.0.1', 
                             user='root', 
                             password='', 
                             db='dbass_music_db',
                             charset='utf8mb4', 
                             cursorclass=pymysql.cursors.DictCursor)

cur = None

def connect(fn):
    def fnrepl(*args):

        cur = connection.cursor()
        return fn(*args, cur)
        connection.commit()
        cur.close()
        connection.close()

    return fnrepl

#####################_______USERS_____________/////

@connect
def chek_user(chatId, cur):
    cur.execute("SELECT * FROM `USERS` WHERE CHATID = {0} ".format(chatId))
    rows = cur.fetchall()
    cur.close()

    if(len(rows) == 0):
        return False
    else:
        for row in rows:
            if row['CHATID'] == chatId:
               return True
            else:
               return False

@connect
def get_param(chatId, param, cur):
    cur.execute("SELECT * FROM `USERS` WHERE CHATID = {0} ".format(chatId))
    rows = cur.fetchall()
    cur.close()
    if rows == ():
        return None
    else:
        return rows[0][param]

@connect
def get_all_users(cur):

    cur.execute("SELECT `CHATID` FROM `USERS` ")
    rows = cur.fetchall()
    lst_users = []
    for el in rows:
        lst_users.append(el['CHATID'])
    cur.close()
    return lst_users

@connect
def add_new_user(chatId, lang, cur ):
    cur.execute("INSERT INTO `USERS` (`CHATID`, `LANGUAGE`, `SHOW_BITRATE`, `SHOW_HEARTS`, `SHOW_AUDIO_FORMAT`, `RESULTS_COUNT`, `LAST_LIST`, `LAST_PAGE`, `LAST_URLS_PAGE`, `URLS`, `WITHOUT_FORMATING`, `HEARTS_BUTTONS`, `PLAYLIST_PAGE`, `LAST_URLS_LIST`)  VALUES ({0},'{1}', {2}, {3}, {4}, {5}, '{6}', {7}, {8}, '{9}', '{10}', {11}, {12}, '{13}')".format(chatId, lang.upper(), 1, 1, 1, 10, '', 0, 0, '', '', 1, 0, ''))
    connection.commit()
    cur.close()
    return

@connect
def set_language(chatId, lang, cur):
    cur.execute("UPDATE `USERS` SET `LANGUAGE` = '{0}' WHERE CHATID = {1} ". format(lang.upper(), chatId))
    connection.commit()
    cur.close()
    return

@connect
def set_pl_page(chatId, page, cur):
    cur.execute("UPDATE `USERS` SET `PLAYLIST_PAGE` = {0} WHERE CHATID = {1} ". format(page, chatId))
    connection.commit()
    cur.close()
    return

@connect
def set_results_count(chatId, count, cur):
    cur.execute("UPDATE `USERS` SET `RESULTS_COUNT` = {0} WHERE CHATID = {1} ". format(count, chatId))
    connection.commit()
    cur.close()
    return

@connect
def set_last_list(chatId, param, cur):
    cur.execute("UPDATE `USERS` SET `LAST_LIST` = '{0}' WHERE CHATID = {1} ". format(param, chatId))
    connection.commit()
    cur.close()
    return

@connect
def set_last_urls_list(chatId, param, cur):
    cur.execute("UPDATE `USERS` SET `LAST_URLS_LIST` = '{0}' WHERE CHATID = {1} ". format(param, chatId))
    connection.commit()
    cur.close()
    return

@connect
def set_urls(chatId, param, cur):
    cur.execute("UPDATE `USERS` SET `URLS` = '{0}' WHERE CHATID = {1} ". format(param, chatId))
    connection.commit()
    cur.close()
    return

@connect
def set_without_formating(chatId, param, cur):
    cur.execute("UPDATE `USERS` SET `WITHOUT_FORMATING` = '{0}' WHERE CHATID = {1} ". format(param, chatId))
    connection.commit()
    cur.close()
    return

@connect
def set_hearts_buttons(chatId, param, cur):
    cur.execute("UPDATE `USERS` SET `HEARTS_BUTTONS` = {0} WHERE CHATID = {1} ". format(param, chatId))
    connection.commit()
    cur.close()
    return

@connect
def set_last_page(chatId, param, cur):
    cur.execute("UPDATE `USERS` SET `LAST_PAGE` = {0} WHERE CHATID = {1} ". format(param, chatId))
    connection.commit()
    cur.close()
    return

@connect
def set_last_urls_page(chatId, param, cur):
    cur.execute("UPDATE `USERS` SET `LAST_URLS_PAGE` = {0} WHERE CHATID = {1} ". format(param, chatId))
    connection.commit()
    cur.close()
    return

@connect
def plus_page_playlist(chatId, cur):
    cur.execute("SELECT * FROM `USERS` WHERE CHATID = {0} ".format(chatId))
    rows = cur.fetchall()
    page = rows[0]['PLAYLIST_PAGE']
    set_pl_page(chatId, page + 1)
    return

@connect
def minus_last_page(chatId, cur):
    cur.execute("SELECT * FROM `USERS` WHERE CHATID = {0} ".format(chatId))
    rows = cur.fetchall()
    page = rows[0]['LAST_PAGE']
    set_last_page(chatId, page - 1)
    return

@connect
def plus_last_page(chatId, cur):
    cur.execute("SELECT * FROM `USERS` WHERE CHATID = {0} ".format(chatId))
    rows = cur.fetchall()
    page = rows[0]['LAST_PAGE']
    set_last_page(chatId, page + 1)
    return
#####################_______FAVOURITES_____________/////

@connect
def get_favorites(chatId, cur):
    cur.execute("SELECT * FROM `FAVOURITES` WHERE CHATID = {0} ".format(chatId))
    rows = cur.fetchall()
    cur.close()
    favorites_lst = []
    favorites = {}
    for row in rows:
        favorites = { row['NAME']: row['FILE_ID'] }
        favorites_lst.append(dict(favorites))

    if rows == ():
        return None
    else:
        return favorites_lst

@connect
def get_favorites_ident(chatId, cur):
    cur.execute("SELECT * FROM `FAVOURITES` WHERE CHATID = {0} ".format(chatId))
    rows = cur.fetchall()
    cur.close()
    favorites = {}
    for row in rows:
        favorites.setdefault(row['NAME'], row['FILE_ID'])
    if rows == ():
        return None
    else:
        return favorites

@connect
def add_new_favorites(chatId, name, fileId, cur):
    cur.execute("INSERT INTO `FAVOURITES` (`CHATID`, `NAME`, `FILE_ID`)  VALUES ({0},'{1}', '{2}')".format(chatId, name, fileId))
    connection.commit()
    cur.close()
    return

@connect
def rm_from_vaforites(key, cur):
    cur.execute("DELETE FROM `FAVOURITES` WHERE `KEY_ID` = {0}".format(key))
    connection.commit()
    cur.close()
    return