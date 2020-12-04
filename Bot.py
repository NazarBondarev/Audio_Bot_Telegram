import config
import dbWorker
import messages
import keyboards
from downloader import SongsDownloader

import os
import aiogram
import asyncio
import json
import requests
import urllib

bot = aiogram.Bot(token =  config.API_TOKEN,
                  parse_mode = aiogram.types.ParseMode.HTML)
loop = asyncio.get_event_loop()
dp = aiogram.Dispatcher(bot, loop = loop)

users = {}

#####_______отредактировано
@dp.message_handler(commands = ['start'])
async def start_message(message: aiogram.types.Message):
    if dbWorker.chek_user(message.chat.id) == True:
        await bot.send_message(message.chat.id, messages.start_messages[dbWorker.get_param(message.chat.id, 'LANGUAGE')])
    else:
        await bot.send_message(message.chat.id, messages.gretings, reply_markup = keyboards.Keyboards().select_lang())

            #####################
        ##############################
    ########################################
#   if message.from_user.id in users.keys():
#       await bot.send_message(message.chat.id, messages.start_messages[users[message.from_user.id]['language']])
#
#   elif message.from_user.id not in users.keys():
#       keyb =  keyboards.Keyboards().select_lang()
#       await bot.send_message(message.chat.id, "Выбери язык\nChoose a language\nElige un idioma", reply_markup = keyb)
#       users[message.from_user.id] = {
#           "language": "",
#           "show_bitrate": "On",
#           "show_hearts": "On",
#           "show_audio_format": "On",
#           "results_count": "10",
#           "favourites_list": [],
#           "last_list": "",
#           "last_page": "",
#           "last_urls_page": "",
#           "urls": "",
#           "without_formating": "",
#           "hearts_buttons": "On",
#
#       }
#       update_users_write()

####################___________отредактировано_____________________
@dp.message_handler(commands = ['song'])
async def search_by_song_title(message: aiogram.types.Message):
    await message.reply( messages.song_messages[dbWorker.get_param(message.chat.id, 'LANGUAGE')])

def replacer(_lst, pat1, pat2):
    lst_buffer = []
    lst = []
    for page in _lst:
        lst_buffer.clear()
        for el in page:
            lst_buffer.append(el.replace(pat1, pat2))
        lst.append(list(lst_buffer))

    return lst

def lst_to_str(_lst):
    return_string = ""
    for page in _lst:
        return_string = return_string + "!".join(page)
        return_string = return_string + "~"

    return return_string

def dict_to_str(_lst):
    return_string = ""
    for page in _lst:
        for dict in page:
            
            return_string = return_string + str(dict["url"]) + ";" + str(dict["title"]) + ";" + str(dict["artist"]) + ";" + str(dict["duration"]) + ";" + str(dict["image"]) + ";"
            return_string = return_string + "|"
    return return_string


#################_____________Отредактировано
@dp.message_handler(lambda message: message.text not in  config.commands and 
                    not message.text.startswith("/newpost"))
async def search_song(message: aiogram.types.Message):
    global number_page_message, you_in_first_page
    lng = dbWorker.get_param(message.chat.id, 'LANGUAGE')
    results_count = dbWorker.get_param(message.chat.id, 'RESULTS_COUNT')

    song_list, urls_list, without_formating = SongsDownloader( f"{message.text}").get_songs_list(results_count)
   
    song_list = replacer(song_list, "0:", "")
    

    you_in_first_page =  messages.you_in_first_page_message[lng]
    number_page_message =  messages.number_page_message[lng]


    if song_list == "NoSongs" and urls_list == "NoSongs":
        await bot.send_message(message.chat.id,  messages.nothing_messages[lng])
    elif not song_list and not urls_list:
        pass
    else:
        

        list_len = len(dbWorker.get_param(message.chat.id, 'LAST_LIST'))  # Длинна списка

        keyb =  keyboards.Keyboards().for_songs_list(urls_list[0],
                                                     message.chat.id,
                                                     dbWorker.get_param(message.chat.id, 'RESULTS_COUNT'))

        await bot.send_message(message.chat.id, number_page_message.format("1", str(len(song_list))) + '\n'.join(song_list[0]), reply_markup = keyb)

        dbWorker.set_last_list(message.chat.id, lst_to_str(song_list).replace("'", "`"))  # Списки песен
        dbWorker.set_urls(message.chat.id, lst_to_str(urls_list).replace("'", "`")) # Списки ссылок на песни

        dbWorker.set_without_formating(message.chat.id, dict_to_str(without_formating).replace("'", "`"))
       
        
        
        dbWorker.set_last_page(message.chat.id, 0) # Последняя страница
        # Последний список ссылок на песни
        dbWorker.set_last_urls_page(message.chat.id, 0)

def string_to_list(mystr):
    return_lst = []
    buffer = []
    res = [element for element in mystr.split("~")]
    for r in res:
        buffer = [element for element in r.split("!")]
        return_lst.append(list(buffer))
        buffer.clear()
    return return_lst

#################_____________Отредактировано
@dp.callback_query_handler(lambda call: call.data in ("to_left", "close", "to_right"))
async def change_page(call: aiogram.types.CallbackQuery):
    user_lang = dbWorker.get_param(call.message.chat.id, 'LANGUAGE')  # Язык пользователя
    # Последний список песен для пользователя
    user_list_now = string_to_list(dbWorker.get_param(call.message.chat.id, 'LAST_LIST'))
    # Последний список ссылок на песни
    user_link_list_now = string_to_list(dbWorker.get_param(call.message.chat.id, 'URLS'))
    # Последняя просмотренная страница
    last_page = dbWorker.get_param(call.message.chat.id, 'LAST_PAGE')
    if call.data == "to_left":  # Листать влево
        if last_page == 0:
            await bot.answer_callback_query(call.id, messages.you_in_first_page_message[user_lang])  # Вы уже на первой странице
        else:
            keyb =  keyboards.Keyboards().for_songs_list(user_link_list_now[last_page - 1],
                                                         call.message.chat.id, dbWorker.get_param(call.message.chat.id, 'RESULTS_COUNT'))

            dbWorker.minus_last_page(call.message.chat.id)
            lPage = dbWorker.get_param(call.message.chat.id, 'LAST_PAGE')
            await bot.edit_message_text(chat_id = call.message.chat.id,
                                        text = messages.number_page_message[user_lang].format( lPage + 1, len(user_list_now)) + "\n".join( user_list_now[lPage]),
                                        message_id = call.message.message_id,
                                        reply_markup = keyb)

    elif call.data == "to_right":  # Листать вправо
        if last_page == len(user_list_now) - 1:
            await bot.answer_callback_query(call.id,
                                             messages.nothing_messages[user_lang])  # Ничего не нашлось
        else:
            keyb =  keyboards.Keyboards().for_songs_list(user_link_list_now[last_page + 1],
                                                         call.message.chat.id, dbWorker.get_param(call.message.chat.id, 'LAST_PAGE'))

            dbWorker.plus_last_page(call.message.chat.id)
            lPage = dbWorker.get_param(call.message.chat.id, 'LAST_PAGE')
            await bot.edit_message_text(chat_id = call.message.chat.id,
                                        text =  messages.number_page_message[user_lang].format( lPage + 1, len(user_list_now)) +"\n".join(user_list_now[lPage]),
                                        message_id = call.message.message_id,
                                        reply_markup = keyb)
    elif call.data == "close":
        await bot.delete_message(call.message.chat.id, call.message.message_id)


def string_to_listDict(mystr):
    list_dic = []
    buffer_dic = {}
    buffer_lst = []
    buffer_pages = []
    res = [element for element in mystr.split("|")]

    for el in res:
        buffer_lst = [element for element in el.split(";")]
        if len(buffer_pages) == 10:
            list_dic.append(list(buffer_pages))
            buffer_pages.clear()
        try:
            buffer_dic = {"url": buffer_lst[0], "title": buffer_lst[1], "artist": buffer_lst[2], "duration": buffer_lst[3], "image": buffer_lst[4]}
            buffer_pages.append(dict(buffer_dic))
        except:
            continue
    if len(list_dic) == 0 or list_dic[len(list_dic) - 1] != buffer_pages:
         list_dic.append(list(buffer_pages))
    return list_dic


#################_____________Отредактировано___
@dp.callback_query_handler(lambda call: call.data.startswith("select") and 
                           call.data.split("_")[1] not in ("RU", "EN", "ES"))
async def select_sound(call: aiogram.types.CallbackQuery):
    get_song_num = call.data.split('_')
    song_num = int(get_song_num[1]) - 1
    page = dbWorker.get_param(call.message.chat.id, 'LAST_PAGE')

    with_form = string_to_listDict(dbWorker.get_param(call.message.chat.id, 'WITHOUT_FORMATING'))
    name = with_form[page][song_num]["artist"]
    song_name = with_form[page][song_num]["title"]

   

    urls = string_to_list(dbWorker.get_param(call.message.chat.id, 'URLS'))

    song = SongsDownloader().download_song(  urls[page][song_num])
    _duration = with_form[page][song_num]["duration"]


 
    _title = ''.join(with_form[page][song_num]["artist"]) + ' - ' + ''.join(with_form[page][song_num]["title"])

    keyb =  keyboards.Keyboards().like_unlike_keyboard(  dbWorker.get_param(call.message.chat.id, 'HEARTS_BUTTONS'))
    msg = await bot.send_audio(call.message.chat.id, audio = song, title = _title,
                               performer = '',
                               caption = '<a href="https://t.me/dbas_music_bot">🎧DBAS Music</a>', reply_markup = keyb)


def get_duration(_duration):
    lst = _duration.split(":")
    hours = int(lst[0]) * 3600
    min = int(lst[1]) * 60
    sec = int(lst[2])
    duration = (hours + min + sec)
    return duration

#################_____________Отредактировано////////
@dp.callback_query_handler(lambda call: call.data in ["like", "unlike"])
async def like_or_unlike(call: aiogram.types.CallbackQuery):
    user_lang = dbWorker.get_param(call.message.chat.id, 'LANGUAGE')

    if call.data == "like":
        await bot.answer_callback_query(call.id,  messages.add_to_favourite[user_lang])
        dbWorker.add_new_favorites(call.message.chat.id, call.message.audio.title, call.message.audio.file_id)
        clear_lsts(call.message.chat.id)        
        return

    elif call.data == "unlike":
        favorites = dbWorker.get_favorites_ident(call.message.chat.id)
        for item in favorites:
            for key in item.keys():
                if key == call.message.audio.title:
                    await bot.answer_callback_query(call.id,  messages.del_from_favourite[user_lang])
                    dbWorker.rm_from_favorites(item[key])                    
                    clear_lsts(call.message.chat.id )
                    return

def clear_lsts(chatId):
    dbWorker.set_last_list(chatId, "")
    dbWorker.set_last_urls_list(chatId, "")
    dbWorker.set_urls(chatId, "")
    dbWorker.set_without_formating(chatId, "")
    return
##########________Отредактировано
@dp.callback_query_handler(lambda call: call.data in ["RU", "EN", "ES"])
async def select_lang(call: aiogram.types.CallbackQuery):
    if dbWorker.chek_user(call.message.chat.id) == True:
        dbWorker.set_language(call.message.chat.id, call.data)
    else:
        await bot.send_message(call.message.chat.id, messages.start_messages[call.data.upper()])
        dbWorker.add_new_user(call.message.chat.id, call.data)
    
    
    
    #if call.data == "select_ru":
    #    users[call.from_user.id]['language'] = "RU"
    #if call.data == "select_en":
    #    users[call.from_user.id]['language'] = "EN"
    #if call.data == "select_es":
    #    users[call.from_user.id]['language'] = "ES"
    #users[call.from_user.id]["last_list"] = ""
    #users[call.from_user.id]["last_urls_list"] = ""
    #users[call.from_user.id]["urls"] = ""
    #users[call.from_user.id]["without_formating"] = ""
    #update_users_write()
    #start_message_lang =  messages.start_messages[users[call.from_user.id]['language']]
    #await bot.send_message(call.message.chat.id, start_message_lang)

#################_____________Отредактировано
@dp.message_handler(commands = ['artist'])
async def search_for_artist_name(message: aiogram.types.Message):
    
    await message.reply( messages.artist_messages[dbWorker.get_param(message.chat.id, 'LANGUAGE')])

#################_____________Отредактировано
@dp.message_handler(commands = ['setlang'])
async def change_language(message: aiogram.types.Message):

    await bot.send_message(message.chat.id, messages.gretings, reply_markup = keyboards.Keyboards().select_lang())


#################_____________Отредактировано
@dp.message_handler(commands = ['settings'])
async def change_settings(message: aiogram.types.Message):
    lng = dbWorker.get_param(message.chat.id, 'LANGUAGE')
    setting_keyb =  keyboards.Keyboards().settings(lng, dbWorker.get_param(message.chat.id, 'RESULTS_COUNT'),
                                                        dbWorker.get_param(message.chat.id, 'HEARTS_BUTTONS'))

    await bot.send_message(message.chat.id, messages.settings_menu[lng], reply_markup = setting_keyb)

#################_____________Отредактировано
@dp.message_handler(commands = ['my'])
async def user_playlist(message: aiogram.types.Message):
    myFavorites = dbWorker.get_favorites(message.chat.id)
    lng = dbWorker.get_param(message.chat.id, 'LANGUAGE')
    dbWorker.set_pl_page(message.chat.id, 0)

    if myFavorites == None:
        await bot.send_message(message.chat.id,  messages.no_playlist[lng])
    else:
        f = lambda A, n=dbWorker.get_param(message.chat.id, 'RESULTS_COUNT'): [A[i:i + n] for i in range(0, len(A), n)]
        cut_playlist = f(myFavorites)

        keyb =  keyboards.Keyboards().for_user_playlist( cut_playlist[dbWorker.get_param(message.chat.id, 'PLAYLIST_PAGE')],
                                                         message.chat.id, dbWorker.get_param(message.chat.id, 'RESULTS_COUNT'))
        user_playlist = []
        i = 1
        for item in cut_playlist[0]:
            for key, val in item.items():
                user_playlist.append(f"{i}. {key}")
                i += 1

        await bot.send_message(message.chat.id, '\n'.join(user_playlist), reply_markup = keyb)
###
    #user_lang = users[message.from_user.id]['language']
    #playlist = users[message.from_user.id]['favourites_list']
    #users[message.from_user.id]["playlist_page"] = 0
    #
    #if not playlist:
    #    await bot.send_message(message.chat.id,  messages.no_playlist[user_lang])
    #
    #else:
    #    users[message.from_user.id]["playlist_page"] = 0
    #    f = lambda A, n=int(users[message.from_user.id]['results_count']): [A[i:i + n] for i in range(0, len(A), n)]
    #    cut_playlist = f(playlist)
    #
    #    keyb =  keyboards.Keyboards().for_user_playlist(
    #        cut_playlist[users[message.from_user.id]["playlist_page"]],
    #        message.chat.id, int(users[message.from_user.id]["results_count"]))
    #    user_playlist = []
    #    i = 1
    #    for item in cut_playlist[0]:
    #        for key, val in item.items():
    #            user_playlist.append(f"{i}. {key}")
    #            i += 1
    #
    #    await bot.send_message(message.chat.id, '\n'.join(user_playlist), reply_markup = keyb)

#################_____________Отредактировано
@dp.callback_query_handler(lambda call: call.data == "to_right_playlist")
async def to_right_user_playlisy(call: aiogram.types.CallbackQuery):

    playlist = dbWorker.get_favorites(message.chat.id)
    playlist_page = dbWorker.get_param(message.chat.id, 'PLAYLIST_PAGE')
    user_lang = dbWorker.get_param(message.chat.id, 'LANGUAGE')
    try:

        if playlist != None and len(playlist) > 1 and playlist_page != len(playlist) - 1:
            dbWorker.plus_page_playlist(message.chat.id)
            f = lambda A, n=dbWorker.get_param(message.chat.id, 'RESULTS_COUNT'): [ A[i:i + n] for i in range(0, len(A), n)]
            cut_playlist = f(playlist)
            keyb =  keyboards.Keyboards().for_user_playlist( playlist[dbWorker.get_param(message.chat.id, 'PLAYLIST_PAGE')],
                                                             call.message.chat.id, dbWorker.get_param(message.chat.id, 'RESULTS_COUNT'))
            user_playlist = []
            i = 1

            for item in cut_playlist[dbWorker.get_param(message.chat.id, 'PLAYLIST_PAGE')]:
                for key, val in item.items():
                    user_playlist.append(f"{i}. {key}")
                    i += 1

            await bot.edit_message_text(chat_id = call.message.chat.id,
                                        text = '\n'.join(user_playlist),
                                        message_id = call.message.message_id,
                                        reply_markup = keyb)

        else:
            await bot.answer_callback_query(call.id,  messages.nothing_messages[user_lang])

    except IndexError:
        await bot.answer_callback_query(call.id,  messages.nothing_messages[user_lang])

#################_____________Отредактировано
@dp.callback_query_handler(lambda call: call.data in ["change_lang", "count_result", "heart_buttons"])
async def settings_menu_changer(call: aiogram.types.CallbackQuery):
    if call.data == "change_lang":
        keyb =  keyboards.Keyboards().select_lang()
        await bot.send_message(call.message.chat.id, messages.gretings, reply_markup = keyb)
    elif call.data == "count_result":
        resCount = dbWorker.get_param(call.message.chat.id, 'RESULTS_COUNT')
        if resCount == 10:
            dbWorker.set_results_count(call.message.chat.id, 6)
        elif resCount == 6:
            dbWorker.set_results_count(call.message.chat.id, 8)
        elif resCount == 8:
            dbWorker.set_results_count(call.message.chat.id, 10)

        setting_keyb =  keyboards.Keyboards().settings(dbWorker.get_param(call.message.chat.id, 'LANGUAGE'),
                                                       dbWorker.get_param(call.message.chat.id, 'RESULTS_COUNT'),
                                                       dbWorker.get_param(call.message.chat.id, 'HEARTS_BUTTONS'))
        dbWorker.set_last_list(call.message.chat.id, "")
        dbWorker.set_last_urls_list(call.message.chat.id, "")
        dbWorker.set_urls(call.message.chat.id, "")
        dbWorker.set_without_formating(call.message.chat.id, "")
        
        await bot.edit_message_text(chat_id = call.message.chat.id,
                                    text =  messages.settings_menu[dbWorker.get_param(call.message.chat.id, 'LANGUAGE')],
                                    message_id = call.message.message_id,
                                    reply_markup = setting_keyb)
    elif call.data == "heart_buttons":
        hButtons = dbWorker.get_param(call.message.chat.id, 'HEARTS_BUTTONS')
        if hButtons == 1:
            dbWorker.set_hearts_buttons(call.message.chat.id, 0)
        elif hButtons == 0:
            dbWorker.set_hearts_buttons(call.message.chat.id, 1)

        setting_keyb =  keyboards.Keyboards().settings(dbWorker.get_param(call.message.chat.id, 'LANGUAGE'),
                                                       dbWorker.get_param(call.message.chat.id, 'RESULTS_COUNT'),
                                                       dbWorker.get_param(call.message.chat.id, 'HEARTS_BUTTONS'))
        dbWorker.set_last_list(call.message.chat.id, "")
        dbWorker.set_last_urls_list(call.message.chat.id, "")
        dbWorker.set_urls(call.message.chat.id, "")
        dbWorker.set_without_formating(call.message.chat.id, "")

       
        await bot.edit_message_text(chat_id = call.message.chat.id,
                                    text =  messages.settings_menu[dbWorker.get_param(call.message.chat.id, 'LANGUAGE')],
                                    message_id = call.message.message_id,
                                    reply_markup = setting_keyb)


#################_____________Отредактировано
@dp.message_handler(commands = ['newpost'])
async def malling(message: aiogram.types.Message):
    text_for_malling = message.text.replace('/newpost', '')
    users_lst = dbWorker.get_all_users()

    i = 0
    for user in users_lst:
        try:
            await bot.send_message(user, text_for_malling)
            i += 1
        except (aiogram.exceptions.BotBlocked, aiogram.exceptions.ChatNotFound):
            pass

    await bot.send_message(message.chat.id, f'Сообщение получили <b>{i}</b> пользователей')

    
#################_____________Отредактировано
@dp.message_handler(commands = ['users'])
async def howusers(message: aiogram.types.Message):
    users_lst = dbWorker.get_all_users()
    await bot.send_message(message.chat.id, f"<em>Кол-во пользователей</em>\n\n<b>{len(users_lst)}</b> пользователей")

        
#################_____________Отредактировано
@dp.callback_query_handler(lambda call: call.data.startswith("playlist"))
async def select_sound(call: aiogram.types.CallbackQuery):
    get_song_num = call.data.split('_')
    playlist = dbWorker.get_favorites(call.message.chat.id)
    song_num = int(get_song_num[1]) - 1
    page = dbWorker.get_param(call.message.chat.id, 'PLAYLIST_PAGE')

    f = lambda A, n=dbWorker.get_param(call.message.chat.id, 'RESULTS_COUNT'): [ A[i:i + n] for i in range(0, len(A), n)]
    cut_playlist = f(playlist)
    keyb =  keyboards.Keyboards().like_unlike_keyboard( dbWorker.get_param(call.message.chat.id, 'HEARTS_BUTTONS'))
    for val in cut_playlist[page][song_num].values():
        await bot.send_audio(call.message.chat.id, audio = val,
                             caption = '<a href="https://t.me/dbas_music_bot">🎧DBAS Music</a>', reply_markup = keyb)


@dp.message_handler(content_types=['voice','text'])
async def repeat_all_message(message):
  file_info = await bot.get_file(message.voice.file_id)
  data = {
    'url': 'https://api.telegram.org/file/bot{0}/{1}'.format(config.API_TOKEN, file_info.file_path),
    'return': 'apple_music,spotify',
    'api_token': 'a156ca037963da105e3a7e37896a82ce'
    }

  result = requests.post('https://api.audd.io/', data=data)

  myjson = json.loads(result.content.decode('utf-8'))
  
  if myjson['result'] == None:
      await bot.send_message(message.chat.id,  'К сожалению ничего не найдено.')
      return
  name = myjson['result']['artist'] + ": " + myjson['result']['title']
  
  global number_page_message, you_in_first_page
  lng = dbWorker.get_param(message.chat.id, 'LANGUAGE')
  results_count = dbWorker.get_param(message.chat.id, 'RESULTS_COUNT')
  
  song_list, urls_list, without_formating = SongsDownloader( f"{name}").get_songs_list(results_count)
  
  song_list = replacer(song_list, "0:", "")
  
  
  you_in_first_page =  messages.you_in_first_page_message[lng]
  number_page_message =  messages.number_page_message[lng]
  
  
  if song_list == "NoSongs" and urls_list == "NoSongs":
      await bot.send_message(message.chat.id,  messages.nothing_messages[lng])
  elif not song_list and not urls_list:
      pass
  else:
      
  
      list_len = len(dbWorker.get_param(message.chat.id, 'LAST_LIST'))  # Длинна списка
  
      keyb =  keyboards.Keyboards().for_songs_list(urls_list[0],
                                                   message.chat.id,
                                                   dbWorker.get_param(message.chat.id, 'RESULTS_COUNT'))
  
      await bot.send_message(message.chat.id, number_page_message.format("1", str(len(song_list))) + '\n'.join(song_list[0]), reply_markup = keyb)
  
      dbWorker.set_last_list(message.chat.id, lst_to_str(song_list).replace("'", "`"))  # Списки песен
      dbWorker.set_urls(message.chat.id, lst_to_str(urls_list).replace("'", "`")) # Списки ссылок на песни
  
      dbWorker.set_without_formating(message.chat.id, dict_to_str(without_formating).replace("'", "`"))
     
      
      
      dbWorker.set_last_page(message.chat.id, 0) # Последняя страница
      # Последний список ссылок на песни
      dbWorker.set_last_urls_page(message.chat.id, 0)
  

    
#def update_users_write():
#    with open('users.json', 'w') as write_users:
#        json.dump(users, write_users, ensure_ascii = False, indent = 4)
        





#def update_users_read():
#    global users
#    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
#    my_file = os.path.join(THIS_FOLDER, 'users.json')
#    with open(my_file, 'r') as read_users:
#        users = json.load(read_users)
#        temp_dict = {}
#        for key, val in users.items():
#            temp_dict[int(key)] = users[key]
#        
#        users = temp_dict
#        temp_dict = {}
#        
#
#        
#        import pprint; pprint.pprint(users)


if __name__ == "__main__":
    aiogram.executor.start_polling(dp, skip_updates = True)
   
