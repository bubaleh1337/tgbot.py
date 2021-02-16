# - *- coding: utf- 8 - *-

from pyrogram import Client, filters
import sqlite3 as sql
from dotenv import load_dotenv
import os

# считываем файл config.ini
load_dotenv('config.env')
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
donor = os.getenv('SOURCE_PUBLIC')
channel = os.getenv('PUBLIC_PUBLIC')
phone_number = os.getenv('PHONE_NUMBER')

# создаем клиент телеграм
app = Client("parser", api_id=api_id, api_hash=api_hash, phone_number=phone_number)


@app.on_message(filters.chat(donor))
def get_post(client, message):
    username = message.chat.username
    message_id = message.message_id
    con = sql.connect('bd.db')
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS DataBase(username, message_id)""")
    con.commit()

    # проверяем есть ли в БД message_id
    # если есть, то добавляем в БД и отправляем на модерку (в наш канал)
    cur.execute("""SELECT message_id FROM DataBase WHERE message_id=?""", (message_id,))
    if not cur.fetchall():  # Если такого id в базе нет, то добавляем название канала и id поста
        cur.execute("""INSERT INTO DataBase VALUES (?,?)""", (username, message_id))
        con.commit()

        # получение последнего ROWID
        for a in cur.execute("""SELECT ROWID,* FROM DataBase LIMIT 1 OFFSET (SELECT COUNT(*) FROM DataBase)-1"""):
            # Получаем последний id из базы, а затем отпр-ем полученный ранее пост в канал модерации и следом за ним
            # id из базы
            last_id = a[0]

            # пересылаем пост в наш канал
            message.forward(channel)


if __name__ == '__main__':
    print('Attempt to run telegram bot!')
    app.run()
    app.restart()
