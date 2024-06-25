import asyncio
import json
import os
import random
import sqlite3
import time
import requests
import telebot
import threading
from telebot import types
from telebot.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, ReactionType
from config import TOKEN
from html import escape
from language import hello_user, botton, help1, platka, NETDOSTIP, rasilkatext, setngs, profile_LANG, pref, kastom, donate, del_my_bot, models_biss_LANG, izmen_s_message_LANG
import re

bot = telebot.TeleBot(TOKEN)

    # =-=-=--=-=-=-=-=-   БАЗА ДАННЫХ   =-=-=-=--=-=-=-=-=-=
    
conn = sqlite3.connect('deleted_messages.db', check_same_thread=False)
cursor = conn.cursor()
db_lock = threading.Lock()

    # =-=-=-=-=--=-=-=-   ВСЕ ID, И ТД   =-=-=--=-=-=-=-=-=-
    
your_chat_id = 5661096875
cozsdatchannel = -1001979700204
cozdd = ['🍌', '🔱', '💝', '⚡', '👾', '🐾', '💟', '💞', '💫', '💥']

# =-=-=-=-=-=-=   КОМАНДЫ   =-=-=-=-=-=-

@bot.message_handler(commands=['start'])
def start(message):
    with db_lock:
        user_id = message.from_user.id
        args = message.text.split()[1:]
        
        cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        user_exists = cursor.fetchone()
        
        if user_exists is None:
            cursor.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (message.from_user.id,))
            conn.commit()

            lang = InlineKeyboardMarkup(row_width=2)
            RU_Lang = types.InlineKeyboardButton("🇷🇺 Русский", callback_data='lang-RU')
            EN_Lang = types.InlineKeyboardButton("🇬🇧 English", callback_data='lang-EN')
            lang.add(RU_Lang, EN_Lang)
            bot.send_message(user_id, '🇷🇺 Выберите язык:\n🇬🇧 select a language:', reply_markup=lang)
            
            if args:
                    refer = args[0]
                    cursor.execute("SELECT * FROM refers WHERE ref=?", (refer,))
                    refer_data = cursor.fetchone()
                    if refer_data:
                        cursor.execute("UPDATE refers SET stats = stats + 1 WHERE ref = ?", (refer,))
                        conn.commit()
            return
        
        if args:
                refer = args[0]
                cursor.execute("SELECT * FROM refers WHERE ref=?", (refer,))
                refer_data = cursor.fetchone()
                if refer_data:                            
                    cursor.execute("UPDATE refers SET stats = stats + 1 WHERE ref = ?", (refer,))
                    conn.commit()

        if check_subscription(message.chat.id, cozsdatchannel):
            if user_exists:
                cursor.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (message.from_user.id,))
                conn.commit()
                
                cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
                row = cursor.fetchone()
                lang = row[0]

                if lang is None:
                    lang = InlineKeyboardMarkup(row_width=2)
                    RU_Lang = types.InlineKeyboardButton("🇷🇺 Русский", callback_data='lang-RU')
                    EN_Lang = types.InlineKeyboardButton("🇬🇧 English", callback_data='lang-EN')
                    lang.add(RU_Lang, EN_Lang)
                    bot.send_message(user_id, '🇷🇺 Выберите язык:\n🇬🇧 Select a language:', reply_markup=lang)
                    return
                
                cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
                row = cursor.fetchone()
                lang = row[0]
                cozdat = botton[f'start_sozdat_{lang}']
                channel = botton[f'start_channel_{lang}']
                dowl = botton[f'start_dowl_{lang}']
                
                markup = types.InlineKeyboardMarkup(row_width=2)
                creator_button = types.InlineKeyboardButton(f"{cozdat}", url="https://t.me/vl_of")
                channel = types.InlineKeyboardButton(f"{channel}", url="https://t.me/Businessmods")
                install_button = types.InlineKeyboardButton(f"{dowl}", callback_data='install')
                markup.add(creator_button, channel, install_button)
                
                cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
                row = cursor.fetchone()
                lang = row[0]
                test = hello_user[f'hello_{lang}']
                bot.send_message(user_id, f'{test}', parse_mode='HTML', reply_markup=markup)

@bot.message_handler(commands=['help'])
def help(message):
    if check_subscription(message.chat.id, cozsdatchannel ):

        user_id = message.from_user.id
        
        markup = types.InlineKeyboardMarkup()
        step_by_step_button = types.InlineKeyboardButton("🔻", callback_data='cansel')
        markup.add(step_by_step_button)
        
        
        cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
        row = cursor.fetchone()
        lang = row[0]
        test = help1[f'help_{lang}']

        bot.send_message(user_id, f'{test}', parse_mode='HTML', reply_markup=markup)

@bot.message_handler(commands=['stats'])
def stats(message):
    with db_lock:
        cursor.execute("SELECT ref, user_id, akt, stats FROM refers")
        refers_data = cursor.fetchall()
        stats_message = "Статистика рефов:\n"
        for row in refers_data:
            ref = row[0]
            user_ids = str(row[1]).split(',') if ',' in str(row[1]) else [str(row[1])] if row[1] else []
            akt = str(row[2]).split(',') if ',' in str(row[2]) else [str(row[2])] if row[2] else []

            total_akt = len(akt)
            num_users = len(user_ids)
            stats_message += f"\|/  {ref}    |//=-=-=-=-=\nВсего: {num_users} | Активных: {total_akt}\nКлик: {row[3]}\n"

        cursor.execute("SELECT user_id FROM users")
        users = cursor.fetchall()
        
        cursor.execute("SELECT message_id FROM deleted_messages")
        sends = cursor.fetchall()
        
        cursor.execute("SELECT user_id FROM polz")
        aktivv = cursor.fetchall()
        
        total_aktivv = len(aktivv)
        total_users = len(users)
        total_message = len(sends)

        stats_message += f"\n\n=-=-=-=-=-=-=-=\nСтатистика по боту:\nВсего юзеров: {total_users},\nиз них {total_aktivv} активных\n\nВсего сообщений {total_message}"

        bot.send_message(your_chat_id, stats_message)

@bot.message_handler(commands=['newref'])
def newref(message):
    with db_lock:
        if message.from_user.id == your_chat_id:
            if len(message.text.split()) == 2:
                ref = message.text.split()[1]  # Получаем значение ref из команды
                try:
                    cursor.execute("INSERT INTO refers (ref) VALUES (?)", (ref,))
                    conn.commit()
                    bot.send_message(message.chat.id, f"Новая реф-ссылка {ref} успешно добавлена!\n\n<code>https://t.me/Businessmode_bot?start={ref}</>", parse_mode='HTML')
                except sqlite3.IntegrityError:
                    bot.send_message(message.chat.id, f"Рефка {ref} уже существует!")
            else:
                bot.send_message(message.chat.id, "Неверный формат команды. Используйте /newref {ref}")

@bot.message_handler(commands=['settings'])
def settings(message):
    with db_lock:
        if check_subscription(message.chat.id, cozsdatchannel ):

            cursor.execute("SELECT me, offon, del, izmen, contentt, pref FROM polz WHERE user_id=?", (message.chat.id,))
            row = cursor.fetchone()
            if row:
                me, offon, del_, izmen, contentt, pref = row
            else:
                user_id = message.from_user.id
                cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
                row = cursor.fetchone()
                lang = row[0]
                test = NETDOSTIP[f'NETDOSTIP_{lang}']
                bot.send_message(user_id, f'{test}', parse_mode='HTML')
                return
            
            user_id = message.from_user.id
            cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
            row = cursor.fetchone()
            lang = row[0]

            offon_LANG = setngs[f'offon_{lang}']
            offon2_LANG = setngs[f'offon2_{lang}']
            offon_tex_LANG = setngs[f'offon_tex_{lang}']
            offon_tex2_LANG = setngs[f'offon_tex2_{lang}']
            contentt_pp_LANG = setngs[f'contentt_ymolc_{lang}']
            contentt_gg_LANG = setngs[f'contentt_gg_{lang}']
            contentt_none_LANG = setngs[f'contentt_none_{lang}']
            
            offon_text = f"{offon_LANG}" if offon == 1 else f"{offon2_LANG}"
            offon_tex = f"{offon_tex_LANG}" if offon == 1 else f"{offon_tex2_LANG}"
            del_smiley = "✖️" if del_ == 1 else "✔️"
            izmen_smiley = "✖️" if izmen == 1 else "✔️"
            me_smiley = "✖️" if me == 1 else "✔️"
            if contentt == 'pp':
                contentt_smiley = f"{contentt_pp_LANG}"
            elif contentt == 'gg':
                contentt_smiley = f"{contentt_gg_LANG}"
            elif contentt == 'None':
                contentt_smiley = f"{contentt_none_LANG}"
            else:
                contentt_smiley = f"{contentt_pp_LANG}"
            
            test = setngs[f'sett_{lang}']
            message_text = test.format(
                offon_text=offon_text,
                offon_tex=offon_tex,
                del_smiley=del_smiley,
                izmen_smiley=izmen_smiley,
                me_smiley=me_smiley,
                contentt_smiley=contentt_smiley,
                pref=pref
            )

            bot.send_message(message.chat.id, message_text, parse_mode='HTML', reply_markup=create_keyboard(message.from_user.id))

@bot.message_handler(commands=['profile'])
def profile(message):
    with db_lock:

        if check_subscription(message.chat.id, cozsdatchannel ):

            user_id = message.from_user.id

            cursor.execute("SELECT me, offon, del, izmen FROM polz WHERE user_id=?", (user_id,))
            row = cursor.fetchone()

            if row:
                me, offon, del_, izmen = row
                user_id = message.from_user.id
                cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
                row = cursor.fetchone()
                lang = row[0]
                offon_LANG = setngs[f'offon_{lang}']
                offon2_LANG = setngs[f'offon2_{lang}']

                
                offon_text = f"{offon_LANG}" if offon == 1 else f"{offon2_LANG}"

                # Считаем количество сохраненных сообщений только для текущего чата (send_to равен chat_id текущего сообщения)
                cursor.execute("SELECT COUNT(*) FROM deleted_messages WHERE send=?", (user_id,))
                count = cursor.fetchone()[0]

                cursor.execute('SELECT allmess FROM polz WHERE user_id = ?', (user_id,))
                vsego = cursor.fetchone()[0]
                
                setti = profile_LANG[f'sett_{lang}']
                test = profile_LANG[f'profile_{lang}']
                message_text = test.format(
                    offon_text=offon_text,
                    vsego=vsego,
                    count=count
                )


                keyboard = types.InlineKeyboardMarkup()
                keyboard.row(types.InlineKeyboardButton(text=f"{setti}", callback_data='settings'))

                bot.send_message(message.chat.id, message_text, reply_markup=keyboard, parse_mode='HTML')
            else:
                user_id = message.from_user.id
                cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
                row = cursor.fetchone()
                lang = row[0]
                test = NETDOSTIP[f'NETDOSTIP_{lang}']
                bot.send_message(user_id, f'{test}', parse_mode='HTML')

@bot.message_handler(commands=['rasilka'])
def rasilka(message):
    if message.from_user.id == your_chat_id:
        # Получаем все user_id из базы данных
        cursor.execute("SELECT user_id FROM users")
        user_ids = cursor.fetchall()
        bot.send_message(your_chat_id, "Рассылка началась!")
        vsego = 0
        noahh = 0
        for user_id in user_ids:
            try:
                bot.send_message(user_id[0], rasilkatext, parse_mode='HTML', disable_web_page_preview=True)
                time.sleep(1)
                print(f"ОТПРАВКА {user_id[0]}")
                vsego += 1
            except Exception as e:
                print(f"Ошибка при отправке сообщения пользователю с user_id={user_id[0]}: {e}")
                time.sleep(0.3)
                vsego += 1
                noahh += 1
                continue

        bot.send_message(your_chat_id, f"Рассылка завершена.\nстатистика:\nОтправлено сообщений {vsego}\nНе долшло до {noahh}")
    else:
        return

@bot.message_handler(commands=['sendid'])
def send_message(message):
    if message.from_user.id == your_chat_id:
        parts = message.text.split()
        if len(parts) < 4:
            bot.reply_to(message, "Неверный формат. Используйте /sendid ID ID2 TEXT")
            return
            
        user_id = parts[1]
        user_id2 = parts[2]
        text = ' '.join(parts[3:])
                
        # Получаем bissID из базы данных по user_id
        cursor.execute("SELECT bissID FROM polz WHERE user_id=?", (user_id,))
        result = cursor.fetchone()
        if result:
            gg = types.InlineKeyboardMarkup()
            gg.row(types.InlineKeyboardButton(text=f"{random.choice(cozdd)} От Владика", url='https://t.me/vl_of'))
            
            bissID = result[0]
            bot.send_message(
                chat_id=user_id2,
                text=text,
                business_connection_id=bissID,
                reply_markup=gg
            )
            bot.send_message(your_chat_id, 'Сообщение отправлено!')
        else:
            bot.reply_to(message, "Пользователь с таким ID не найден")

@bot.message_handler(commands=['pref'])
def set_pref(message):
    with db_lock:
        user_id = message.from_user.id
        cursor.execute("SELECT pref FROM polz WHERE user_id=?", (user_id,))
        row = cursor.fetchone()
        if row:
            try:
                command, text = message.text.split(maxsplit=1)
                if len(text) > 2:
                    cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
                    row = cursor.fetchone()
                    lang = row[0]
                    test = pref[f'max_{lang}']

                    bot.reply_to(message, f'{test}')
                    return
                user_id = message.from_user.id
                cursor.execute("UPDATE polz SET pref = ? WHERE user_id = ?", (text, user_id))
                conn.commit()
                cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
                kekkk = cursor.fetchone()
                lang = kekkk[0]
                test = pref[f'edit_{lang}']
                message_text = test.format(
                    text=text
                )

                bot.reply_to(message, message_text)
                bot.set_message_reaction(message.chat.id, message.message_id, [types.ReactionTypeEmoji("🆒")])
            except ValueError as e:
                cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
                kekkk = cursor.fetchone()
                lang = kekkk[0]
                test = pref[f'you_{lang}']
                message_text = test.format(
                    tekp=row[0]
                )

                bot.reply_to(message, message_text, parse_mode='HTML')
                bot.set_message_reaction(message.chat.id, message.message_id, [types.ReactionTypeEmoji("❤️")])
            except Exception as e:
                cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
                kekkk = cursor.fetchone()
                lang = kekkk[0]
                test = pref[f'warn_{lang}']


                bot.reply_to(message, test)
                bot.set_message_reaction(message.chat.id, message.message_id, [types.ReactionTypeEmoji("🗿")])

        else:
            user_id = message.from_user.id
            cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
            row = cursor.fetchone()
            lang = row[0]
            test = NETDOSTIP[f'NETDOSTIP_{lang}']
            bot.send_message(user_id, f'{test}', parse_mode='HTML')
            bot.set_message_reaction(message.chat.id, message.message_id, [types.ReactionTypeEmoji("👾")])

@bot.message_handler(commands=['url'])
def set_url(message):
    with db_lock:
        user_id = message.from_user.id
        cursor.execute("SELECT me, offon, del, izmen FROM polz WHERE user_id=?", (user_id,))
        row = cursor.fetchone()
        cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
        kekkk = cursor.fetchone()
        lang = kekkk[0]

        if row:
            args = message.text.split()[1:]
            
            if args:
                url = ' '.join(args)
                
                cursor.execute("UPDATE polz SET url = ? WHERE user_id = ?", (url, user_id))
                conn.commit()
                test = kastom[f'url1_{lang}']
                message_text = test.format(
                    url=url
                )
                bot.reply_to(message, message_text)
            else:
                test = kastom[f'url2_{lang}']
                bot.reply_to(message, test)
        else:
            user_id = message.from_user.id
            cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
            row = cursor.fetchone()
            lang = row[0]
            test = NETDOSTIP[f'NETDOSTIP_{lang}']
            bot.send_message(user_id, f'{test}', parse_mode='HTML')
            bot.set_message_reaction(message.chat.id, message.message_id, [types.ReactionTypeEmoji("👾")])

@bot.message_handler(commands=['name'])
def set_name(message):
    with db_lock:
        user_id = message.from_user.id
        cursor.execute("SELECT me, offon, del, izmen FROM polz WHERE user_id=?", (user_id,))
        row = cursor.fetchone()
        cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
        kekkk = cursor.fetchone()
        lang = kekkk[0]

        if row:
            args = message.text.split()[1:]
            
            if args:
                name = ' '.join(args)
                
                cursor.execute("UPDATE polz SET name = ? WHERE user_id = ?", (name, user_id))
                conn.commit()
                test = kastom[f'name1_{lang}']
                message_text = test.format(
                    name=name
                )
                bot.reply_to(message, message_text)
            else:
                test = kastom[f'name2_{lang}']

                bot.reply_to(message, test)
        else:
            user_id = message.from_user.id
            cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
            row = cursor.fetchone()
            lang = row[0]
            test = NETDOSTIP[f'NETDOSTIP_{lang}']
            bot.send_message(user_id, f'{test}', parse_mode='HTML')
            bot.set_message_reaction(message.chat.id, message.message_id, [types.ReactionTypeEmoji("👾")])

@bot.message_handler(commands=['button'])
def button(message):
    with db_lock:
        user_id = message.from_user.id
        cursor.execute("SELECT name, url, contentt FROM polz WHERE user_id=?", (user_id,))
        didribytiv, url, ceivord = cursor.fetchone()
        
        cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
        kekkk = cursor.fetchone()
        lang = kekkk[0]
        
        if didribytiv:
            test = kastom[f'button1_{lang}']

            pp = types.InlineKeyboardMarkup()
            pp.row(types.InlineKeyboardButton(text=f"{random.choice(cozdd)} {test}", url='https://t.me/Businessmode_bot?start=ls'))
            
            gg = types.InlineKeyboardMarkup()
            gg.row(types.InlineKeyboardButton(text=f"{random.choice(cozdd)} {didribytiv}", url=f'{url}'))
            
            if ceivord != 'None' and ceivord != 'gg' and ceivord != 'pp':
                ceivord = pp
            if ceivord == 'pp':
                ceivord = pp
            if ceivord == 'gg':
                ceivord = gg
            if ceivord == 'None':
                test = kastom[f'button2_{lang}']

                bot.send_message(user_id, test)
                return
            test = kastom[f'button3_{lang}']

            ranm = [f'\n<code>*{test}</>', '']
            random_number = random.randint(1, 5)

            if random_number == 1:
                message_to_send = ranm[0]
            else:
                message_to_send = ranm[1]
            tst = kastom[f'button4_{lang}']
            bot.send_message(user_id, f"{tst}\n{message_to_send}", reply_markup=ceivord, parse_mode='HTML')
        else:
            user_id = message.from_user.id
            cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
            row = cursor.fetchone()
            lang = row[0]
            test = NETDOSTIP[f'NETDOSTIP_{lang}']
            bot.send_message(user_id, f'{test}', parse_mode='HTML')
            bot.set_message_reaction(message.chat.id, message.message_id, [types.ReactionTypeEmoji("👾")])

@bot.message_handler(content_types=['document'])
def handle_document(message):
    if message.from_user.id == your_chat_id:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        current_dir = os.getcwd()
        current_file_path = os.path.join(current_dir, 'bot.py')
        if os.path.exists(current_file_path):
            os.remove(current_file_path)
        new_file_path = os.path.join(current_dir, message.document.file_name)
        with open(new_file_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.reply_to(message, f'Файл "{message.document.file_name}" успешно загружен и заменен')

@bot.message_handler(commands=['ohziz'])
def ПППЫПОАGG(message):
    if message.from_user.id == your_chat_id:
        cursor.execute("DELETE FROM deleted_messages")
        conn.commit()
        bot.send_message(your_chat_id, text="Все строки из таблицы deleted_messages успешно удалены.")

@bot.message_handler(commands=['lang'])
def set_lang(message):
    user_id = message.from_user.id
    lang = InlineKeyboardMarkup(row_width=2)
    RU_Lang = types.InlineKeyboardButton("🇷🇺 Русский", callback_data='lang-RU')
    EN_Lang = types.InlineKeyboardButton("🇬🇧 English", callback_data='lang-EN')
    lang.add(RU_Lang, EN_Lang)
    bot.send_message(user_id, '🇷🇺 Выберите язык:\n🇬🇧 Select a language:', reply_markup=lang)

@bot.message_handler(commands=['donate'])
def sent_donate(message):
    with db_lock:
        user_id = message.from_user.id
        cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
        kekkk = cursor.fetchone()
        lang = kekkk[0]
        mm = InlineKeyboardMarkup(row_width=3)
        mm1 = types.InlineKeyboardButton("5 ⭐️", callback_data='d-5')
        mm2 = types.InlineKeyboardButton("10 ⭐️", callback_data='d-10')
        mm3 = types.InlineKeyboardButton("15 ⭐️", callback_data='d-15')
        mm4 = types.InlineKeyboardButton("20 ⭐️", callback_data='d-20')
        mm5 = types.InlineKeyboardButton("50 ⭐️", callback_data='d-50')
        mm6 = types.InlineKeyboardButton("100 ⭐️", callback_data='d-100')
        mm7 = types.InlineKeyboardButton("200 ⭐️", callback_data='d-200')
        mm.add(mm1, mm2, mm3, mm4, mm5, mm6, mm7)
        test = donate[f'donate_{lang}']
        
        bot.send_message(message.from_user.id, test, reply_markup=mm)

@bot.pre_checkout_query_handler(func=lambda query: True)
def process_pre_checkout_query(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(func=lambda message: True, content_types=['successful_payment'])
def process_successful_payment(message):
    with db_lock:
        user_id = message.from_user.id
        cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
        kekkk = cursor.fetchone()
        lang = kekkk[0]
        test = donate[f'donate2_{lang}']
        
        telegram_payment_charge_id = message.successful_payment.telegram_payment_charge_id
        # bot.refund_star_payment(user_id, telegram_payment_charge_id)

        bot.send_message(message.chat.id, test)
        bot.send_message(your_chat_id, f'Кто-то заплатил! {user_id}\n\n{telegram_payment_charge_id}')

@bot.message_handler(commands=['ref'])
def refund(message):
    if message.from_user.id == your_chat_id:
        args = message.text.split()[1:]
        user_id = args[0]
        telegram_payment_charge_id = args[1]
        bot.refund_star_payment(user_id, telegram_payment_charge_id)
        bot.send_message(user_id, 'Деньги возвращены!')

# =-=-=-=-=-=-=-=   КНОПКИ   =-=-=-=-=-=-=-=

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'install':
        with db_lock:
            user_id = call.from_user.id
            cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
            kekkk = cursor.fetchone()
            lang = kekkk[0]

            step_by_step_button_LANG = botton[f'step_by_step_button_{lang}']
            general_button_LANG = botton[f'general_button_{lang}']
            back_button_LANG = botton[f'back_button_{lang}']
            
            install_markup = types.InlineKeyboardMarkup(row_width=2)
            step_by_step_button = types.InlineKeyboardButton(f"{step_by_step_button_LANG}", callback_data='step_by_step_1')
            general_button = types.InlineKeyboardButton(f"{general_button_LANG}", callback_data='general')
            back_button = types.InlineKeyboardButton(f"{back_button_LANG}", callback_data='/start')
            install_markup.add(step_by_step_button, general_button, back_button)
            
            text = botton[f'dowlnddd_{lang}']
            
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=install_markup, parse_mode='HTML')

    elif call.data == 'step_by_step_1':
        with db_lock:
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            user_id = call.from_user.id
            cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
            kekkk = cursor.fetchone()
            lang = kekkk[0]

            back_button_LANG = botton[f'back_button_{lang}']
            next_step_button_LANG = botton[f'next_step_button_{lang}']
            
            
            step_markup = types.InlineKeyboardMarkup()
            back_button = types.InlineKeyboardButton(back_button_LANG, callback_data='install_xx')
            next_step_button = types.InlineKeyboardButton(next_step_button_LANG, callback_data='step_by_step_2')
            step_markup.add(back_button, next_step_button)
            with open('kartin/1.jpg', 'rb') as photo:
                YYtext = botton[f'step_by_step_{lang}']
                bot.send_photo(call.message.chat.id, photo, caption=YYtext, reply_markup=step_markup, parse_mode='HTML')

    elif call.data.startswith('step_by_step_'):
        with db_lock:
            user_id = call.from_user.id
            cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
            kekkk = cursor.fetchone()
            lang = kekkk[0]

            current_page = int(call.data.split('_')[-1])
            if current_page == 1:
                pinkt = botton[f'step_by_step_go1_{lang}']
            elif current_page == 2:
                pinkt = botton[f'step_by_step_go2_{lang}']
            elif current_page == 3:
                pinkt = botton[f'step_by_step_go3_{lang}']
            elif current_page == 4:
                pinkt = botton[f'step_by_step_go4_{lang}']
            else:
                pinkt = botton[f'step_by_step_go5_{lang}']

            if current_page < 5:
                next_page = current_page + 1
                step_markup = types.InlineKeyboardMarkup()
                back_button = types.InlineKeyboardButton(botton[f'back_button_{lang}'], callback_data='install_xx')
                next_step_button = types.InlineKeyboardButton(botton[f'next_step_button_{lang}'], callback_data=f'step_by_step_{next_page}')
                step_markup.add(back_button, next_step_button)
                with open(f'kartin/{current_page}.jpg', 'rb') as photo:
                    test = botton[f'step_by_step_go_{lang}']
                    messag_text = test.format(
                        current_page=current_page,
                        pinkt=pinkt
                    )

                    bot.edit_message_media(media=telebot.types.InputMedia(type='photo', media=photo, caption=messag_text, parse_mode='HTML'), chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=step_markup)		
                    # bot.send_photo(call.message.chat.id, photo, caption=f"Шаг {current_page}/4.", reply_markup=step_markup)
            else:
                bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)  # Удаляем сообщение с кнопкой
                markup = types.InlineKeyboardMarkup()
                back_button = types.InlineKeyboardButton(botton[f'back_button_{lang}'], callback_data='/start')
                markup.add(back_button)
                bot.send_message(call.message.chat.id, botton[f'compl_step_{lang}'], reply_markup=markup)

    elif call.data == '/start':
        with db_lock:
            user_id = call.from_user.id
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)  # Удаляем сообщение с кнопкой
            cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
            row = cursor.fetchone()
            lang = row[0]
            cozdat = botton[f'start_sozdat_{lang}']
            channel = botton[f'start_channel_{lang}']
            dowl = botton[f'start_dowl_{lang}']
            
            markup = types.InlineKeyboardMarkup(row_width=2)
            creator_button = types.InlineKeyboardButton(f"{cozdat}", url="https://t.me/vl_of")
            channel = types.InlineKeyboardButton(f"{channel}", url="https://t.me/Businessmods")
            install_button = types.InlineKeyboardButton(f"{dowl}", callback_data='install')
            markup.add(creator_button, channel, install_button)
            
            cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
            row = cursor.fetchone()
            lang = row[0]
            test = hello_user[f'hello_{lang}']
            bot.send_message(user_id, f'{test}', parse_mode='HTML', reply_markup=markup)

    elif call.data == 'general':
        with db_lock:
            user_id = call.from_user.id
            cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
            kekkk = cursor.fetchone()
            lang = kekkk[0]

            markup = types.InlineKeyboardMarkup()
            install_button = types.InlineKeyboardButton(botton[f'back_to_install22_{lang}'], callback_data='install')
            markup.add(install_button)
            
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=botton[f'generalgg_{lang}'] , reply_markup=markup, parse_mode='HTML')
    
    elif call.data == 'install_xx':
        with db_lock:
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)  # Удаляем сообщение с кнопкой

            user_id = call.from_user.id
            cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
            kekkk = cursor.fetchone()
            lang = kekkk[0]

            step_by_step_button_LANG = botton[f'step_by_step_button_{lang}']
            general_button_LANG = botton[f'general_button_{lang}']
            back_button_LANG = botton[f'back_button_{lang}']
            
            install_markup = types.InlineKeyboardMarkup(row_width=2)
            step_by_step_button = types.InlineKeyboardButton(f"{step_by_step_button_LANG}", callback_data='step_by_step_1')
            general_button = types.InlineKeyboardButton(f"{general_button_LANG}", callback_data='general')
            back_button = types.InlineKeyboardButton(f"{back_button_LANG}", callback_data='/start')
            install_markup.add(step_by_step_button, general_button, back_button)
            
            text = botton[f'dowlnddd_{lang}']
            
            bot.send_message(call.message.chat.id, text, reply_markup=install_markup, parse_mode='HTML')

    elif call.data == 'cansel':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)  # Удаляем сообщение с кнопкой
        bot.answer_callback_query(call.id, '✖️ Cansel!')

    elif call.data == 'offon':
        with db_lock:
            cursor.execute("UPDATE polz SET offon = 1 - offon WHERE user_id=?", (call.from_user.id,))
            conn.commit()
                
            # Обновление текста сообщения и всех кнопок после нажатия на любую из них
            message_text, keyboard = create_keyboard_and_message(call.from_user.id)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=message_text,
                                reply_markup=keyboard, parse_mode='HTML')

    elif call.data == 'del':
        with db_lock:
            cursor.execute("UPDATE polz SET del = 1 - del WHERE user_id=?", (call.from_user.id,))
            conn.commit()
                
            # Обновление текста сообщения и всех кнопок после нажатия на любую из них
            message_text, keyboard = create_keyboard_and_message(call.from_user.id)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=message_text,
                                reply_markup=keyboard, parse_mode='HTML')

    elif call.data == 'izmen':
        with db_lock:

            cursor.execute("UPDATE polz SET izmen = 1 - izmen WHERE user_id=?", (call.from_user.id,))
            conn.commit()
        
            # Обновление текста сообщения и всех кнопок после нажатия на любую из них
            message_text, keyboard = create_keyboard_and_message(call.from_user.id)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=message_text,
                                reply_markup=keyboard, parse_mode='HTML')

    elif call.data == 'me':
        with db_lock:

            cursor.execute("UPDATE polz SET me = 1 - me WHERE user_id=?", (call.from_user.id,))
            conn.commit()

            # Обновление текста сообщения и всех кнопок после нажатия на любую из них
            message_text, keyboard = create_keyboard_and_message(call.from_user.id)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=message_text,
                            reply_markup=keyboard, parse_mode='HTML')
        
    elif call.data == 'settings':
        with db_lock:

            message_text, keyboard = create_keyboard_and_message(call.from_user.id)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=message_text,
                                reply_markup=keyboard, parse_mode='HTML')

    elif call.data == 'profile':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                            text="ЗАГРУЗКА ПРОФИЛЯ", reply_markup=None, parse_mode='HTML')

        profile_call(call)
        return
    
    elif call.data == 'delete_messages':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                            text="ЗАГРУЗКА СТАТИСТИКИ", reply_markup=None, parse_mode='HTML')

        delet_mess_call(call)
        
    elif call.data == 'confirm_delete':
        with db_lock:

            cursor.execute("DELETE FROM deleted_messages WHERE send=?", (call.message.chat.id,))
            conn.commit()
            user_id = call.from_user.id
            
            cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
            kekkk = cursor.fetchone()
            lang = kekkk[0]

            bot.send_message(call.message.chat.id, botton[f'dell_all_{lang}'])

            # Обновляем сообщение с настройками
            message_text, keyboard = create_keyboard_and_message(call.from_user.id)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                text=message_text, reply_markup=keyboard, parse_mode='HTML')
       
    elif call.data == 'contentt':
        with db_lock:
            user_id = call.from_user.id
            cursor.execute("SELECT name, url, contentt FROM polz WHERE user_id=?", (user_id,))
            didribytiv, url, contentt = cursor.fetchone()
            
            cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
            kekkk = cursor.fetchone()
            lang = kekkk[0]

            ppg = setngs[f'contentt_ymolc_{lang}']
            ppgС = setngs[f'contentt_gg_{lang}']
            ppgOFF = setngs[f'offon_tex2_{lang}']
            ON_Of_OFF = 'contenttOFF'
            ppgC = setngs[f'contentt_gg_{lang}']
            if contentt == 'pp':
                contentt_smiley = setngs[f'contentt_ymolc_{lang}']
                ppg = f'{contentt_smiley} ☑️'
            elif contentt == 'gg':
                contentt_smiley = setngs[f'contentt_gg_{lang}']
                ppgC = f'{contentt_smiley} ☑️'
            elif contentt == 'None':
                contentt_smiley = setngs[f'contentt_none_{lang}']
                ppgOFF = setngs[f'contentt_none2_{lang}']
                ON_Of_OFF = 'contenttON'
            else:
                contentt_smiley = setngs[f'contentt_gg_{lang}']
                ppg = f'{contentt_smiley} ☑️'

                
            pp = types.InlineKeyboardMarkup(row_width=2)
            pp.row(types.InlineKeyboardButton('◀️⚙️', callback_data='settings'),
                types.InlineKeyboardButton(text=f"{ppgOFF}", callback_data=f'{ON_Of_OFF}'))

            pp.row(types.InlineKeyboardButton(text=f'{ppg}', callback_data='contenttALL'))
            pp.row(types.InlineKeyboardButton(text=f'{ppgC}', callback_data='contenttCREATE'))
            test = setngs[f'contentt_settings_{lang}']
            
            mess = test.format(
                GG_LANG={random.choice(cozdd)},
                contentt_smiley=contentt_smiley
            )

            bot.edit_message_text(chat_id=user_id,
                          message_id=call.message.message_id,
                          text=mess, parse_mode='html', reply_markup=pp)

    elif call.data in ('contenttOFF', 'contenttALL', 'contenttCREATE', 'contenttON'):
        with db_lock:
            user_id = call.from_user.id
            button_text = call.data
            if button_text == 'contenttOFF':
                new = 'None'
                cursor.execute("UPDATE polz SET contentt = ? WHERE user_id=?", (new, user_id,))
                conn.commit()
                SYKA_BLYATI(call)
                return
            elif button_text == 'contenttALL':
                new = 'pp'
                cursor.execute("UPDATE polz SET contentt = ? WHERE user_id=?", (new, user_id,))
                conn.commit()
                SYKA_BLYATI(call)
                return
            elif button_text == 'contenttCREATE':
                new = 'gg'
                cursor.execute("UPDATE polz SET contentt = ? WHERE user_id=?", (new, user_id,))
                conn.commit()
                SYKA_BLYATI(call)
                return
            elif button_text == 'contenttON':
                new = 'pp'
                cursor.execute("UPDATE polz SET contentt = ? WHERE user_id=?", (new, user_id,))
                conn.commit()
                SYKA_BLYATI(call)
                return       
    
    elif call.data in ('Не хватает функций', 'Нету доверия', 'Реклама', 'Нет надобности', 'Баги', 'Не работает бот', 'Not enough functions', 'No trust', 'Advertising', 'No need', 'Bugs', 'Bot doesn\'t work'):
        with db_lock:
            user_id = call.from_user.id

            cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
            kekkk = cursor.fetchone()
            lang = kekkk[0]

            button_text = call.data
            user_id = call.from_user.id
            user_username = call.from_user.username if call.from_user.username else "nonegg"
            user_name = call.from_user.first_name if call.from_user.first_name else ""
            message = f"🚩 {user_id} отключил бота и выбрал -- {button_text}\n@{user_username} {user_name}"
            bot.send_message(your_chat_id, message)
            
            
            pp = types.InlineKeyboardMarkup(row_width=2)
            pp.row(types.InlineKeyboardButton(text=del_my_bot[f'del_mess_{lang}'], callback_data='delete_messages'))

            bot.edit_message_text(chat_id=user_id,
                                message_id=call.message.message_id,
                                text=del_my_bot[f'thns_prich_{lang}'], reply_markup=pp)
        
    elif call.data in ('lang-RU', 'lang-EN'):
        with db_lock:
            user_id = call.from_user.id
            button_text = call.data
            
            new = 'RU'
            
            if button_text == 'lang-RU':
                new = 'RU'
                
                cursor.execute("UPDATE users SET lang = ? WHERE user_id=?", (new, user_id,))
                conn.commit()
                bot.edit_message_text(chat_id=user_id,
                                    message_id=call.message.message_id,
                                    text="🇷🇺 Язык выбран!")

            elif button_text == 'lang-EN':
                new = 'EN'

                cursor.execute("UPDATE users SET lang = ? WHERE user_id=?", (new, user_id,))
                conn.commit()
                bot.edit_message_text(chat_id=user_id,
                                    message_id=call.message.message_id,
                                    text="🇬🇧 Language is chosen!")

    elif call.data in ('d-5', 'd-10', 'd-15', 'd-20', 'd-50', 'd-100', 'd-200'):
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)  # Удаляем сообщение с кнопкой
        bot.answer_callback_query(call.id, '')

        number_str = call.data.split('-')[1]
        number = int(number_str)
        chat_id = call.from_user.id
        title = f"Donate {number}"
        description = "Финансовая поддержка бота"
        currency = "XTR"
        prices = [telebot.types.LabeledPrice(label="Будем безумно рады Вашей поддержки нашего бота 💞💞💞", amount=number)]
        provider_token = ""
        invoice_payload = "podderzka"
        
        yy = types.InlineKeyboardMarkup(row_width=1)
        inline_button = types.InlineKeyboardButton(text="Telegram stats", pay=True)

        step_by_step_button = types.InlineKeyboardButton("◀️", callback_data='donateBACK')
        yy.add(inline_button, step_by_step_button)

        bot.send_invoice(chat_id,
                        title=title,
                        description=description,
                        currency=currency,
                        provider_token=provider_token,
                        invoice_payload=invoice_payload,
                        prices=prices, 
                        reply_markup=yy)

    elif call.data == 'donateBACK':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)  # Удаляем сообщение с кнопкой

        sent_donate(call)

    else:
        user_id = call.from_user.id
        bot.send_message(user_id, 'Откуда ты блять откапал эту кнопку? напиши в лс! @vl_of')
        
# =-=-=-=-=-=-=   БИЗНЕС ХЭНДЛЕРЫ   =-=-=-=-=-=-=

@bot.business_message_handler(content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'sticker', 'animation', 'video_note'])
def calcBusiness(message):
    with db_lock:
        business_connection_id = message.json['business_connection_id']
        business_connection = bot.get_business_connection(business_connection_id)
        user_iid = business_connection.user.id
        user_id = message.from_user.id
        chatt = message.chat.id
        name_chat = message.chat.first_name
        prefix = get_prefix(user_iid)
        cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_iid,))
        kekkk = cursor.fetchone()
        lang = kekkk[0]
        test = kastom[f'button1_{lang}']

        pp = types.InlineKeyboardMarkup()
        pp.row(types.InlineKeyboardButton(text=f"{random.choice(cozdd)} {test}", url='https://t.me/Businessmode_bot?start=ls'))
        
        
        cursor.execute("SELECT name, url, contentt FROM polz WHERE user_id=?", (user_iid,))
        didribytiv, url, ceivord = cursor.fetchone()
        gg = types.InlineKeyboardMarkup()
        gg.row(types.InlineKeyboardButton(text=f"{random.choice(cozdd)} {didribytiv}", url=f'{url}'))
        
        if ceivord != 'None' and ceivord != 'gg' and ceivord != 'pp':
            ceivord = pp
        if ceivord == 'pp':
            ceivord = pp
        if ceivord == 'gg':
            ceivord = gg
        if ceivord == 'None':
            ceivord = None
        
        if message.content_type in ['photo', 'video', 'document', 'audio', 'voice', 'sticker', 'animation', 'video_note']:
            save_media_to_database(message, user_iid)

            print("МЕДИА!!!!!!!!1")
            return
        
        text = message.text.strip()
        
        if text.startswith(str(prefix) + 'calc') or text.startswith(str(prefix) + 'калк') or text.startswith(str(prefix) + 'кк') or text.startswith(str(prefix) + 'cc') or text.startswith(str(prefix) + 'к'):
            expression = text[len(str(prefix)) + 4:].strip()
            if contains_letters(expression):
                bot.send_message(
                    chat_id=message.chat.id,
                    text=models_biss_LANG[f'tvari_{lang}'],
                    business_connection_id=business_connection_id,
                    parse_mode='HTML',
                    reply_markup=ceivord
                )
                return

            if expression:
                result = str(eval(expression))
                calc = models_biss_LANG[f'calc_LANG_{lang}']
                bot.send_message(
                    chat_id=message.chat.id,
                    text=f"<tg-emoji emoji-id=\"5789927068208730568\">❇️</tg-emoji> {calc} {result}",
                    business_connection_id=business_connection_id,
                    parse_mode='HTML',
                    reply_markup=ceivord
                )
            elif message.reply_to_message:
                reply_text = message.reply_to_message.text
                if contains_letters(reply_text):
                    bot.send_message(
                        chat_id=message.chat.id,
                        text=models_biss_LANG[f'tvari_{lang}'],
                        business_connection_id=business_connection_id,
                        parse_mode='HTML',
                        reply_markup=ceivord
                    )
                    return

                result = str(eval(reply_text))
                calc = models_biss_LANG[f'calc_LANG_{lang}']

                bot.send_message(
                    chat_id=message.chat.id,
                    text=f"<tg-emoji emoji-id=\"5789927068208730568\">❇️</tg-emoji> {calc} {result}",
                    business_connection_id=business_connection_id, 
                    parse_mode='HTML',
                    reply_markup=ceivord
                )
            else:
                bot.send_message(
                    chat_id=message.chat.id,
                    text="<tg-emoji emoji-id=\"5208814054574929660\">🤓</tg-emoji> 2+2=5",
                    business_connection_id=business_connection_id,
                    parse_mode='HTML',
                    reply_markup=ceivord
                )
        
        if text.startswith(str(prefix) + 'ball') or text.startswith(str(prefix) + 'балл') or text.startswith(str(prefix) + 'бал'):
            text_without_command = text[len(str(prefix)) + 4:].strip()
            if not text_without_command:
                bot.send_message(
                    chat_id=message.chat.id,
                    text="<tg-emoji emoji-id=\"5870931487146119264\">❗️</tg-emoji> <b>Нет вопроса после команды 0_0<b>",
                    business_connection_id=business_connection_id,
                    parse_mode='HTML',
                    reply_markup=ceivord
                )
                return
            else:
                list = [models_biss_LANG[f'ball5_{lang}'], models_biss_LANG[f'ball6_{lang}']]
                list2 = [models_biss_LANG[f'ball1_{lang}'], models_biss_LANG[f'ball2_{lang}'], models_biss_LANG[f'ball3_{lang}'], models_biss_LANG[f'ball4_{lang}']]
                ball = (
                    f"<tg-emoji emoji-id=\"5370765563226236970\">🗣</tg-emoji> <code>{text_without_command}</code>\n"
                    + f"<b><tg-emoji emoji-id=\"5361837567463399422\">🔮</tg-emoji> {random.choice(list2)} {random.choice(list)}</b>"
                )
                bot.send_message(
                    chat_id=message.chat.id,
                    text=ball,
                    business_connection_id=business_connection_id,
                    parse_mode='HTML',
                    reply_markup=ceivord
                )
        
        if text.startswith(str(prefix) + 'sav') or text.startswith(str(prefix) + 'сох') or text.startswith(str(prefix) + 'вау') or text.startswith(str(prefix) + ':)') or text.startswith(str(prefix) + 's'):
            if not user_id == user_iid:
                return
            media_type = message.reply_to_message.content_type
            
            if media_type == "photo":
                photo = message.reply_to_message.photo[-1]
                photo_url = bot.get_file_url(photo.file_id)
                photo_data = requests.get(photo_url).content
                
                bot.send_photo(user_iid, photo_data, caption=models_biss_LANG[f'send_media_{lang}'], parse_mode='html')
            elif media_type == "video":
                photo = message.reply_to_message.video
                photo_url = bot.get_file_url(photo.file_id)
                photo_data = requests.get(photo_url).content

                bot.send_video(user_iid, photo_data, caption=models_biss_LANG[f'send_media_{lang}'], parse_mode='html')
            elif media_type == "audio":
                photo = message.reply_to_message.audio
                photo_url = bot.get_file_url(photo.file_id)
                photo_data = requests.get(photo_url).content

                bot.send_audio(user_iid, photo_data, caption=models_biss_LANG[f'send_media_{lang}'], parse_mode='html')
            elif media_type == "voice":
                photo = message.reply_to_message.voice
                photo_url = bot.get_file_url(photo.file_id)
                photo_data = requests.get(photo_url).content

                bot.send_voice(user_iid, photo_data, caption=models_biss_LANG[f'send_media_{lang}'], parse_mode='html')
            elif media_type == "video_note":
                photo = message.reply_to_message.video_note
                photo_url = bot.get_file_url(photo.file_id)
                photo_data = requests.get(photo_url).content
                bot.send_message(user_iid, models_biss_LANG[f'send_media_{lang}'], parse_mode='HTML')
                bot.send_video_note(user_iid, photo_data)
           
        if text.startswith(str(prefix) + 'stats') or text.startswith(str(prefix) + 'статс'):
            cursor.execute("SELECT colvo FROM dialogs WHERE sobez=?", (chatt,))
            colvo = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM deleted_messages WHERE send_to=? AND send=?", (chatt, user_iid))
            all_mess = cursor.fetchone()[0]

            gg = f"<tg-emoji emoji-id=\"5778465982339093574\">ℹ️</tg-emoji> <b>Статистика переписки c {html_escape(name_chat)}:\n" \
                    f"- {colvo} </><i>сообщений было написано за<b> время работы бота</></>\n" \
                    f"<b>~ {all_mess} сообщений осталось на нашем сервере</>"
                    
            bot.send_message(
                chat_id=message.chat.id,
                text=gg,
                business_connection_id=business_connection_id,
                parse_mode='HTML',
                reply_markup=ceivord
            )
        else:
            print("Пришло сообщение на:", user_iid)   
            save_message_to_database(message.message_id, message.text, message.chat.id, message.from_user.id, message.from_user.first_name, message.from_user.username, user_iid)     
            print("Записано сообщение!")
            check_db(user_iid, business_connection_id, message.chat.id)

@bot.deleted_business_messages_handler()    
def handle_deleted_business_messages(deleted_messages):
    with db_lock:
        business_connection_id = deleted_messages.business_connection_id
        business_connection = bot.get_business_connection(business_connection_id)
        user_id = business_connection.user.id
        cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
        kekkk = cursor.fetchone()
        lang = kekkk[0]

        deleted_message_ids = deleted_messages.message_ids
        
        for message_id in deleted_messages.message_ids:
            cursor.execute('SELECT send_from FROM deleted_messages WHERE message_id = ? AND send = ?', (message_id, user_id,))
            send_from_user_id = cursor.fetchone()
            if send_from_user_id and send_from_user_id[0] == user_id:
                
                cursor.execute('SELECT me FROM polz WHERE user_id = ?', (user_id,))
                rosasa = cursor.fetchone()
                if rosasa:
                    if rosasa[0] == 1:
                        return 
                    
        cursor.execute('SELECT offon FROM polz WHERE user_id = ?', (user_id,))
        rosdasa = cursor.fetchone()
        if rosdasa:
            if rosdasa[0] == 1:
                return 
            
        cursor.execute('SELECT del FROM polz WHERE user_id = ?', (user_id,))
        rosasa = cursor.fetchone()
        if rosasa:
            if rosasa[0] == 1:
                return 
         
        for message_id in deleted_message_ids:
            deleted_message_text = get_message_text_from_database(message_id, user_id)
            if deleted_message_text:
                # Проверяем, начинается ли текст сообщения с "{type:"
                if deleted_message_text.startswith("{type:"):
                    # Разбираем информацию о медиа из строки
                    media_info = parse_media_info(deleted_message_text)
                    if media_info:
                        media_type = media_info.get("type")
                        file_id = media_info.get("file_id")
                        # Получаем информацию о пользователе, от которого было удалено сообщение
                        cursor.execute('SELECT name, username, send_to FROM deleted_messages WHERE message_id = ? AND send = ?', (message_id, user_id,))
                        user_info = cursor.fetchone()
                        name, username, idd = user_info

                        if media_type == "photo":
                            bot.send_photo(user_id, file_id, caption=izmen_s_message_LANG[f'delit_media_{lang}'].format(html_escape(name), username, idd, message_id), parse_mode='html')
                        elif media_type == "video":
                            bot.send_video(user_id, file_id, caption=izmen_s_message_LANG[f'delit_media_{lang}'].format(html_escape(name), username, idd, message_id), parse_mode='html')
                        elif media_type == "audio":
                            bot.send_audio(user_id, file_id, caption=izmen_s_message_LANG[f'delit_media_{lang}'].format(html_escape(name), username, idd, message_id), parse_mode='html')
                        elif media_type == "voice":
                            bot.send_voice(user_id, file_id, caption=izmen_s_message_LANG[f'delit_media_{lang}'].format(html_escape(name), username, idd, message_id), parse_mode='html')
                        elif media_type == "document":
                            bot.send_document(user_id, file_id, caption=izmen_s_message_LANG[f'delit_media_{lang}'].format(html_escape(name), username, idd, message_id), parse_mode='html')
                        elif media_type == "sticker":
                            bot.send_message(user_id, izmen_s_message_LANG[f'delit_media_{lang}'].format(html_escape(name), username, idd, message_id), parse_mode='html')
                            bot.send_sticker(user_id, file_id)
                        elif media_type == "animation":
                            bot.send_animation(user_id, file_id, caption=izmen_s_message_LANG[f'delit_media_{lang}'].format(html_escape(name), username, idd, message_id), parse_mode='html')
                        elif media_type == "video_note":
                            bot.send_message(user_id, izmen_s_message_LANG[f'delit_media_{lang}'].format(html_escape(name), username, idd, message_id), parse_mode='html')
                            bot.send_video_note(user_id, file_id)
                    
        for message_id in deleted_message_ids:
            deleted_message_text = get_message_text_from_database(message_id, user_id)
            if deleted_message_text:
                if deleted_message_text.startswith("{type:"):
                    return
                # Получаем информацию о пользователе, от которого было удалено сообщение
                cursor.execute('SELECT name, username, send_to FROM deleted_messages WHERE message_id = ? AND send = ?', (message_id, user_id,))
                user_info = cursor.fetchone()
                if user_info:
                    name, username, idd = user_info
                    if user_info:
                        bot.send_message(user_id, izmen_s_message_LANG[f'delit_mess_{lang}'].format(html_escape(name), username, idd, message_id, html_escape(deleted_message_text)), parse_mode='html')
                    else:
                        return                

@bot.edited_business_message_handler()
def handle_edited_business_message(edited_message):
    with db_lock:
        business_connection_id = edited_message.business_connection_id
        
        business_connection = bot.get_business_connection(business_connection_id)
        user_id = business_connection.user.id

        cursor.execute('SELECT send_from, send FROM deleted_messages WHERE message_id = ? AND send = ?', (edited_message.message_id, user_id,))
        result = cursor.fetchone()

        cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
        kekkk = cursor.fetchone()
        lang = kekkk[0]


        if result and result[0] == result[1]:
            upgrade_save_message_to_database(edited_message.message_id, edited_message.text, user_id)
            return 

    
        cursor.execute('SELECT izmen FROM polz WHERE user_id = ?', (user_id,))
        rosasa = cursor.fetchone()

        if rosasa:
            if rosasa[0] == 1:
                return 
    
        old_message_text = get_message_text_from_database(edited_message.message_id, user_id)
        if old_message_text:
            if old_message_text.startswith("{type:"):
                return
            cursor.execute('SELECT name, username, send_to FROM deleted_messages WHERE message_id = ? AND send = ?', (edited_message.message_id, user_id,))
            user_info = cursor.fetchone()
            if user_info:
                name, username, idd = user_info
                if user_info:
                    bot.send_message(user_id, izmen_s_message_LANG[f'izmen_mess_{lang}'].format(html_escape(name), username, idd, edited_message.message_id, html_escape(old_message_text), html_escape(edited_message.text)), parse_mode='html')
                    upgrade_save_message_to_database(edited_message.message_id, edited_message.text, user_id)
                else:
                    return                

@bot.business_connection_handler()
def connect_id(business_connection):
    with db_lock:
        user_id = business_connection.user_chat_id
        
        cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
        kekkk = cursor.fetchone()
        lang = kekkk[0]
        
        if business_connection.is_enabled:
            cursor.execute("SELECT * FROM polz WHERE user_id=?", (user_id,))
            user = cursor.fetchone()

            if user is None:
                cursor.execute("INSERT INTO polz (user_id, offon, me, del, izmen, allmess) VALUES (?, ?, ?, ?, ?, ?)",
                            (user_id, 0, 1, 0, 0, 0))
                conn.commit()

                bot.send_message(user_id, izmen_s_message_LANG[f'new_user_{lang}'], parse_mode='HTML')
                bot.send_message(your_chat_id, f"УРА! + Еще один полноценный ползователь бота!\n{user_id}")
            else:
                bot.send_message(user_id, izmen_s_message_LANG[f'no_new_user_{lang}'])
                bot.send_message(your_chat_id, f'В бота вернулся {user_id}\nУРА!')
        else:
            pp = types.InlineKeyboardMarkup(row_width=2)
            pp.row(types.InlineKeyboardButton(text=del_my_bot[f'prich1_{lang}'], callback_data=del_my_bot[f'prich1_{lang}']))
            pr2 = types.InlineKeyboardButton(del_my_bot[f'prich2_{lang}'], callback_data=del_my_bot[f'prich2_{lang}'])
            pr3 = types.InlineKeyboardButton(del_my_bot[f'prich3_{lang}'], callback_data=del_my_bot[f'prich3_{lang}'])
            pr4 = types.InlineKeyboardButton(del_my_bot[f'prich4_{lang}'], callback_data=del_my_bot[f'prich4_{lang}'])
            pr5 = types.InlineKeyboardButton(del_my_bot[f'prich5_{lang}'], callback_data=del_my_bot[f'prich5_{lang}'])
            pr6 = types.InlineKeyboardButton(del_my_bot[f'prich6_{lang}'], callback_data=del_my_bot[f'prich6_{lang}'])
            pp.add(pr2, pr3, pr4, pr5, pr6)

            bot.send_message(user_id, del_my_bot[f'user_del_bot_{lang}'], reply_markup=pp)
            bot.send_message(your_chat_id, f'{user_id} отключил бота. ждем ответа на почему')

# =-=-=-=-=--=-=   ВСЕ ХЭНДЛЕРЫ ДЛЯ ОБРАБОТЧИКОВ КОМАНД   =-=-=-=-=-=-=-=-=-=

def upgrade_save_message_to_database(message_id, text, user_id):
    cursor.execute('UPDATE deleted_messages SET text = ? WHERE message_id = ? AND send = ?', (text, message_id, user_id))
    conn.commit()

def save_message_to_database(message_id, text, chat_id, from_user_id, name, username, user_iid):
    cursor.execute('INSERT OR REPLACE INTO deleted_messages (message_id, text, send_to, send_from, name, username, send) VALUES (?, ?, ?, ?, ?, ?, ?)', (message_id, text, chat_id, from_user_id, name, username, user_iid))
    conn.commit()
        # Проверяем общее количество записей с нулями
        
    # Проверяем общее количество записей с нулями
    cursor.execute('SELECT COUNT(*) FROM deleted_messages')
    count_records = cursor.fetchone()[0]
    
    if str(count_records).endswith("00"):
        bot.send_message(your_chat_id, f"Поздравляю с {count_records} сообщениями!")
        SUPER_stats()
            
def get_message_text_from_database(message_id, user_id):
    cursor.execute('SELECT text FROM deleted_messages WHERE message_id = ? AND send = ?', (message_id, user_id,))

    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        return None    
    
def check_db(user_iid, new_bissID, sobez):
    user_id = user_iid
    cursor.execute("SELECT * FROM polz WHERE user_id=?", (user_iid,))
    user = cursor.fetchone()

    if user is None:
        # Если пользователя нет, добавляем его в базу данных polz
        cursor.execute("INSERT INTO polz (user_id, offon, me, del, izmen, allmess) VALUES (?, ?, ?, ?, ?, ?)",
                       (user_iid, 0, 1, 0, 0, 1))
        conn.commit()

        cursor.execute("SELECT * FROM refers")
        refers_data = cursor.fetchall()

        for refer_data in refers_data:
            refer = refer_data[0]
            user_ids = refer_data[1].split(",") if refer_data[1] else []  # Получаем список user_id из строки

            if str(user_id) in user_ids:
                # Если user_id найден в списке user_ids, добавляем его в столбец akt
                akt = refer_data[2]  # Получаем значение akt из строки
                if isinstance(akt, int):  # Проверяем, что akt является целым числом
                    akt_users = [str(akt)]
                else:
                    akt_users = akt.split(",") if akt else []  # Получаем список user_id из столбца akt

                if str(user_id) not in akt_users:  # Проверяем, что user_id еще не в akt
                    akt_users.append(str(user_id))
                    updated_akt = ','.join(akt_users)
                    cursor.execute("UPDATE refers SET akt=? WHERE ref=?", (updated_akt, refer))
                    conn.commit()

        bot.send_message(user_iid, "<b><i>💫 Спасибо, что начали пользоваться нашим ботом 💖\n\n🎉 Вам был открыт доступ к команде </>/settings !</>\n\n⚡️ <i><b>Наш канал: @Businessmods\n\n🙏 Спасибо за ваше доверие! 🥰</></>", parse_mode='HTML')
        bot.send_message(your_chat_id, f"УРА! + Еще один полноценный ползователь бота!\n{user_iid}\n\nСООБЩЕНИЕ ОТ CHECK_DB")
    else:
        cursor.execute("UPDATE polz SET allmess=allmess+1, bissID=? WHERE user_id=?", (new_bissID, user_iid))
        conn.commit()
        
        cursor.execute("SELECT * FROM dialogs WHERE sobez = ? AND send = ?", (sobez, user_iid))
        existing_entry = cursor.fetchone()

        if existing_entry is None:
            cursor.execute("INSERT INTO dialogs (sobez, send, colvo) VALUES (?, ?, 1)", (sobez, user_iid))
            conn.commit()
        else:
            cursor.execute("UPDATE dialogs SET colvo = colvo + 1 WHERE sobez = ? AND send = ?", (sobez, user_iid))
            conn.commit()
     
def create_keyboard(user_id):
    cursor.execute("SELECT me, offon, del, izmen, contentt FROM polz WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
    kekkk = cursor.fetchone()
    lang = kekkk[0]

    if row:
        me, offon, del_, izmen, contentt = row
    else:
        cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
        row = cursor.fetchone()
        lang = row[0]
        test = NETDOSTIP[f'NETDOSTIP_{lang}']
        bot.send_message(user_id, f'{test}', parse_mode='HTML')
        return
    
        

    offon_text = setngs[f'offon_{lang}'] if offon == 1 else setngs[f'offon2_{lang}']
    offon_tex = setngs[f'offon_tex_{lang}'] if offon == 1 else setngs[f'offon_tex2_{lang}']
    del_smiley = "✖️" if del_ == 1 else "✔️"
    izmen_smiley = "✖️" if izmen == 1 else "✔️"
    me_smiley = "✖️" if me == 1 else "✔️"
    if contentt == 'pp':
        contentt_smiley = setngs[f'contentt_ymolc_{lang}']
    elif contentt == 'gg':
        contentt_smiley = setngs[f'contentt_gg_{lang}']
    elif contentt == 'None':
        contentt_smiley = setngs[f'contentt_none_{lang}']
    else:
        contentt_smiley = setngs[f'contentt_ymolc_{lang}']

    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(types.InlineKeyboardButton(text=f"◀️👤", callback_data='profile'),
                types.InlineKeyboardButton(text=f"{offon_tex}", callback_data='offon'))
    udaleniah_LANG = setngs[f'udaleniah_{lang}']
    izmeneniah_LANG = setngs[f'izmeneniah_{lang}']
    keyboard.row(types.InlineKeyboardButton(text=f"{udaleniah_LANG} {del_smiley}", callback_data='del'),
                types.InlineKeyboardButton(text=f"{izmeneniah_LANG} {izmen_smiley}", callback_data='izmen'))
    my_message_LANG = setngs[f'my_message_{lang}']
    keyboard.row(types.InlineKeyboardButton(text=f"{my_message_LANG} {me_smiley}", callback_data='me'))
    keyboard.row(types.InlineKeyboardButton(text=f"{contentt_smiley}", callback_data='contentt'))

    keyboard.row(types.InlineKeyboardButton(text=setngs[f'del_my_message_{lang}'], callback_data='delete_messages'))
    return keyboard

def create_keyboard_and_message(user_id):
    cursor.execute("SELECT me, offon, del, izmen, contentt, pref FROM polz WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
    kekkk = cursor.fetchone()
    lang = kekkk[0]

    if row:
        me, offon, del_, izmen, contentt, pref = row
    else:
        return

    offon_text = setngs[f'offon_{lang}'] if offon == 1 else setngs[f'offon2_{lang}']
    offon_tex = setngs[f'offon_tex_{lang}'] if offon == 1 else setngs[f'offon_tex2_{lang}']
    del_smiley = "✖️" if del_ == 1 else "✔️"
    izmen_smiley = "✖️" if izmen == 1 else "✔️"
    me_smiley = "✖️" if me == 1 else "✔️"
    if contentt == 'pp':
        contentt_smiley = setngs[f'contentt_ymolc_{lang}']
    elif contentt == 'gg':
        contentt_smiley = setngs[f'contentt_gg_{lang}']
    elif contentt == 'None':
        contentt_smiley = setngs[f'contentt_none_{lang}']
    else:
        contentt_smiley = setngs[f'contentt_ymolc_{lang}']


    GGgGG = setngs[f'sett_{lang}']
    message_text = GGgGG.format(
        offon_text=offon_text,
        del_smiley=del_smiley,
        izmen_smiley=izmen_smiley,
        me_smiley=me_smiley,
        pref=pref,
        contentt_smiley=contentt_smiley,
    )
        
    if offon == 1:
        message_text = setngs[f'settoff_{lang}'].format(
        offon_text=offon_text
        )
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(types.InlineKeyboardButton(text=f"◀️👤", callback_data='profile'),
                    types.InlineKeyboardButton(text=f"{offon_tex}", callback_data='offon'))
        return message_text, keyboard

    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(types.InlineKeyboardButton(text=f"◀️👤", callback_data='profile'),
                types.InlineKeyboardButton(text=f"{offon_tex}", callback_data='offon'))
    udaleniah_LANG = setngs[f'udaleniah_{lang}']
    izmeneniah_LANG = setngs[f'izmeneniah_{lang}']
    keyboard.row(types.InlineKeyboardButton(text=f"{udaleniah_LANG} {del_smiley}", callback_data='del'),
                types.InlineKeyboardButton(text=f"{izmeneniah_LANG} {izmen_smiley}", callback_data='izmen'))
    my_message_LANG = setngs[f'my_message_{lang}']
    keyboard.row(types.InlineKeyboardButton(text=f"{my_message_LANG} {me_smiley}", callback_data='me'))
    keyboard.row(types.InlineKeyboardButton(text=f"{contentt_smiley}", callback_data='contentt'))

    keyboard.row(types.InlineKeyboardButton(text=setngs[f'del_my_message_{lang}'], callback_data='delete_messages'))
    return message_text, keyboard

def delet_mess_call(call):
    cursor.execute("SELECT COUNT(*) FROM deleted_messages WHERE send=?", (call.message.chat.id,))
    count = cursor.fetchone()[0]

    cursor.execute('SELECT allmess FROM polz WHERE user_id = ?', (call.message.chat.id,))
    vsego = cursor.fetchone()[0]

    vsegydal = vsego - count
    cursor.execute("SELECT lang FROM users WHERE user_id=?", (call.message.chat.id,))
    kekkk = cursor.fetchone()
    lang = kekkk[0]


    # Создаем клавиатуру с кнопками "назад" и "ДА!"
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(types.InlineKeyboardButton(text=setngs[f'bask_gg_{lang}'], callback_data='settings'),
                types.InlineKeyboardButton(text=setngs[f'yes_gg_{lang}'], callback_data='confirm_delete'))

    # Редактируем текущее сообщение с новым текстом и клавиатурой
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                        text=setngs[f'del_mess_{lang}'].format(count=count, vsego=vsego, vsegydal=vsegydal), reply_markup=keyboard, parse_mode='HTML')

def profile_call(call):
    user_id = call.from_user.id

    cursor.execute("SELECT me, offon, del, izmen FROM polz WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    cursor.execute("SELECT lang FROM users WHERE user_id=?", (call.message.chat.id,))
    kekkk = cursor.fetchone()
    lang = kekkk[0]

    if row:
        me, offon, del_, izmen = row
        offon_text = setngs[f'offon_{lang}'] if offon == 1 else setngs[f'offon2_{lang}']
            
        # Считаем количество сохраненных сообщений только для текущего чата (send_to равен chat_id текущего сообщения)
        cursor.execute("SELECT COUNT(*) FROM deleted_messages WHERE send=?", (user_id,))
        count = cursor.fetchone()[0]

        cursor.execute('SELECT allmess FROM polz WHERE user_id = ?', (user_id,))
        vsego = cursor.fetchone()[0]

        message_text = profile_LANG[f'profile_{lang}'].format(
            offon_text=offon_text,
            vsego=vsego,
            count=count
        )
        # Создаем клавиатуру с кнопкой "Настройки"
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(types.InlineKeyboardButton(text=profile_LANG[f'sett_{lang}'], callback_data='settings'))
            
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                            text=message_text, reply_markup=keyboard, parse_mode='HTML')
    else:
        cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
        row = cursor.fetchone()
        lang = row[0]
        test = NETDOSTIP[f'NETDOSTIP_{lang}']
        bot.send_message(user_id, f'{test}', parse_mode='HTML')
 
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                            text=NETDOSTIP, reply_markup=keyboard, parse_mode='HTML')

def contains_letters(expression):
    # Используем регулярное выражение для поиска букв
    return bool(re.search('[a-zA-Z]', expression))

# .
    # =-=-=--=-=-=-=-=-=- ПРОВЕРКА ПОДПИСКИ =-=-=-=-=-=-=-=
def check_subscription(user_id, cozsdatchannel):
    x = bot.get_chat_member(cozsdatchannel, user_id)
    cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
    kekkk = cursor.fetchone()
    lang = kekkk[0]

    if row is None or row[0] is None:
        lang = InlineKeyboardMarkup(row_width=2)
        RU_Lang = types.InlineKeyboardButton("🇷🇺 Русский", callback_data='lang-RU')
        EN_Lang = types.InlineKeyboardButton("🇬🇧 English", callback_data='lang-EN')
        lang.add(RU_Lang, EN_Lang)
        bot.send_message(user_id, '🇷🇺 Выберите язык:\n🇬🇧 select a language:', reply_markup=lang)
        return False
    else:
        lang = row[0]
        test = platka[f'sponsor_{lang}']

        if x.status in ("member", "creator", "administrator"):
            return True
        else:
            chanell_LANG = setngs[f'chanell_sozdat_{lang}']
            podpisk = types.InlineKeyboardMarkup(row_width=1)
            cozdat = types.InlineKeyboardButton(f"{random.choice(cozdd)} {chanell_LANG}", url="https://t.me/+OExux_o-dT1hYzFi")
            podpisk.add(cozdat)
            bot.send_message(user_id, f'{test}', reply_markup=podpisk)
            return False

def html_escape(text):
    return escape(text)

def get_prefix(user_id):
    cursor.execute("SELECT pref FROM polz WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return '+'  # Возвращаем значение по умолчанию, если префикс не найден

def save_media_to_database(message, glava):
    media_type = message.content_type
    file_id = None

    if media_type == 'photo':
        file_id = message.photo[-1].file_id  # Получаем file_id самого высокого качества
    elif media_type == 'video':
        file_id = message.video.file_id
    elif media_type == 'document':
        file_id = message.document.file_id
    elif media_type == 'audio':
        file_id = message.audio.file_id
    elif media_type == 'voice':
        file_id = message.voice.file_id
    elif media_type == 'sticker':
        file_id = message.sticker.file_id
    elif media_type == 'animation':
        file_id = message.animation.file_id
    elif media_type == 'video_note':
        file_id = message.video_note.file_id
    
    if file_id:
        media_text = f'{{type:"{media_type}", file_id:"{file_id}"}}'
        save_message_to_database(message.message_id, media_text, message.chat.id, message.from_user.id, message.from_user.first_name, message.from_user.username, glava)

def parse_media_info(media_text):
    """
    Разбирает информацию о медиа из строки в формате "{type:"photo", file_id:"AgACAgIAAxkDAAEFZCFmUlUNEBqBzes7meGVYPyqBll6xwAD3TEbpL-RSrJizX-tip9FAQADAgADbQADNQQ"}"
    и возвращает словарь с типом и file_id.
    """
    try:
        media_info = {}
        media_text = media_text.strip("{}")
        parts = media_text.split(",")
        for part in parts:
            key, value = part.split(":")
            media_info[key.strip()] = value.strip().strip('"')
        return media_info
    except Exception as e:
        print("Error parsing media info:", e)
        return None

def SYKA_BLYATI(call):
    user_id = call.from_user.id
    cursor.execute("SELECT name, url, contentt FROM polz WHERE user_id=?", (user_id,))
    didribytiv, url, contentt = cursor.fetchone()
    
    cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
    kekkk = cursor.fetchone()
    lang = kekkk[0]

        
    ppg = setngs[f'contentt_ymolc_{lang}']
    ppgС = setngs[f'contentt_gg_{lang}']
    ppgOFF = setngs[f'xz_off_{lang}']
    ON_Of_OFF = 'contenttOFF'
    if contentt == 'pp':
        contentt_smiley = setngs[f'contentt_ymolc_{lang}']
        ppg = f'{ppg} ☑️'
    elif contentt == 'gg':
        contentt_smiley = setngs[f'contentt_gg_{lang}']
        ppgC = f'{ppgС} ☑️'
    elif contentt == 'None':
        contentt_smiley = setngs[f'contentt_none_{lang}']
        ppgOFF = setngs[f'contentt_none2_{lang}']
        ON_Of_OFF = 'contenttON'
    else:
        contentt_smiley = setngs[f'contentt_ymolc_{lang}']
        ppg = f'{ppg} ☑️'

                
    pp = types.InlineKeyboardMarkup(row_width=2)
    pp.row(types.InlineKeyboardButton('◀️⚙️', callback_data='settings'),
        types.InlineKeyboardButton(text=f"{ppgOFF}", callback_data=f'{ON_Of_OFF}'))

    pp.row(types.InlineKeyboardButton(text=f'{ppg}', callback_data='contenttALL'))
    pp.row(types.InlineKeyboardButton(text=f'{ppgC}', callback_data='contenttCREATE'))

    bot.edit_message_text(chat_id=user_id,
                          message_id=call.message.message_id,
                          text=setngs[f'contentt_settings_{lang}'].format(GG_LANG=random.choice(cozdd), contentt_smiley=contentt_smiley), parse_mode='html', reply_markup=pp)

def SUPER_stats():
    cursor.execute("SELECT ref, user_id, akt, stats FROM refers")
    refers_data = cursor.fetchall()
    stats_message = "Статистика рефов:\n"
    for row in refers_data:
        ref = row[0]
        user_ids = str(row[1]).split(',') if ',' in str(row[1]) else [str(row[1])] if row[1] else []
        akt = str(row[2]).split(',') if ',' in str(row[2]) else [str(row[2])] if row[2] else []

        total_akt = len(akt)
        num_users = len(user_ids)
        stats_message += f"\|/  {ref}    |//=-=-=-=-=\nВсего: {num_users} | Активных: {total_akt}\nКлик: {row[3]}\n"

    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
        
    cursor.execute("SELECT message_id FROM deleted_messages")
    sends = cursor.fetchall()
        
    cursor.execute("SELECT user_id FROM polz")
    aktivv = cursor.fetchall()
        
    total_aktivv = len(aktivv)
    total_users = len(users)
    total_message = len(sends)

    stats_message += f"\n\n=-=-=-=-=-=-=-=\nСтатистика по боту:\nВсего юзеров: {total_users},\nиз них {total_aktivv} активных\n\nВсего сообщений {total_message}"

    bot.send_message(your_chat_id, stats_message)



# =-=-=--=-=-=-=   СТАРТ БОТА   =-=-=-=-=-=--=-

bot.send_message(your_chat_id, "start!")
# bot.polling()

while True:
    try:
        bot.polling()
    except Exception as e:
        print("Error:", e)
        bot.send_message(your_chat_id, e)
        continue