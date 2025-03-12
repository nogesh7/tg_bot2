import telebot ##Проект для мамы
import config
from telebot import types
import json
import pandas as pd
#from docx import Document  # Correct usage of python-docx
from spire.doc import *
from spire.doc.common import *
import re
from datetime import datetime, date, time

bot = telebot.TeleBot(config.token_pomoshnik)

not_time_sleep = 0

with open("json_user.json", "r") as fh:
    user = json.load(fh)

with open("user_changed.json", "r") as fh:
    user_change = json.load(fh)


global date
global TIME
global time_rass

time_rass = 0
date = "01.01"
TIME = "00:00"

@bot.message_handler(commands=['start'])
def start(message):
    not_time_sleep = 1
    with open("json_user.json", "r") as fh:
        user = json.load(fh)
    if message.from_user.id not in user.keys(): ## Если пользователя нет в базе данных
        bot.send_message(message.from_user.id, "Введите Фамилию")
        user_change[str(message.from_user.id)] = [["01.01", "00:01", "остальная информация", "Имя фамилия"], ["01.01", "00:01", "остальная информация", "Имя фамилия"], ["01.01", "00:01", "остальная информация", "Имя фамилия"], ["01.01", "00:01", "остальная информация", "Имя фамилия"],]
        user[str(message.from_user.id)] = ["user", 0, "Имя фамилия"]
        with open("json_user.json", "w") as fh:
            json.dump(user, fh)



@bot.message_handler(commands=['info'])
def start(message):
    if user[str(message.from_user.id)][0] == "adm":
        bot.send_message(message.from_user.id, "Напишите дату, на которую сейчас пришлете таблицу в формате ДД.ММ")
        user[str(message.from_user.id)][1] = "Присылает дату"
        with open("json_user.json", "w") as fh:
            json.dump(user, fh)
    else:
        bot.send_message(message.from_user.id, "Вы не админ")


@bot.message_handler(commands=['send_time'])
def start(message):
    if str(message.from_user.id) in user.keys():
        bot.send_message(message.from_user.id, user_change[str(message.from_user.id)][0][2])
   

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    with open("json_user.json", "r") as fh:
        user = json.load(fh)
    if user[str(message.from_user.id)][1] == 0:
        bot.send_message(message.from_user.id, "Подтвердите что ваша фамилия:" + message.text + " (Введите свою фамилию еще раз)")
        user[str(message.from_user.id)][1] = 1
        user[str(message.from_user.id)][2] = message.text
        user_change[str(message.from_user.id)][0][3] = message.text
        with open("json_user.json", "w") as fh:
            json.dump(user, fh)

        with open("user_changed.json", "w") as fh:
            json.dump(user_change, fh)    
       
            
    elif user[str(message.from_user.id)][1] == 1:
        if message.text == user[str(message.from_user.id)][2]:
            bot.send_message(message.from_user.id, "Вы зарегистрированы,если вы админ, введите ключ-пароль!")
            ## статус 2 -- пользватель зарегистрирован
            user[str(message.from_user.id)][1] = 2

        elif message.text != user[str(message.from_user.id)][2]:
            user[str(message.from_user.id)][1] = 0


        with open("json_user.json", "w") as fh:
            json.dump(user, fh)

    elif user[str(message.from_user.id)][1] == 2:## проверка статуса админа
        print(config.admin)
        if message.text == config.admin:
            user[str(message.from_user.id)][0] = "adm" ## выдача статуса админа или обычного юзера
        else:
            user[str(message.from_user.id)][0] = "user"

        user[str(message.from_user.id)][1] = 3
        
        if user[str(message.from_user.id)][0] == "adm":
            bot.send_message(message.from_user.id, "Пришлите список фамилий (Каждая фамилия с новой строки)") ## у пользователя статус 3
        else:
            bot.send_message(message.from_user.id, "Ключ неправильный(")
        with open("json_user.json", "w") as fh:
            json.dump(user, fh)

        
    elif user[str(message.from_user.id)][1] == 3 and user[str(message.from_user.id)][0] == "adm":
        user[str(message.from_user.id)][1] = 4 
        a = user.values()
        spisoc_polza = []
        for i in a:
            spisoc_polza.append(i[2]) ## b - список имен согласно тому, какие пользователи заходили
        spisoc_polz = sorted(spisoc_polza)
        spisoc_polz_ot_admina = sorted(message.text.split(sep='\n')) ## список имён от админа



        if spisoc_polz in spisoc_polz_ot_admina and len(spisoc_polz) < len(spisoc_polz_ot_admina):
            otsutstvie = []
            for i in spisoc_polz_ot_admina:
                if i not in spisoc_polz:
                    otsutstvie.append(i)
            q = '\n'.join(otsutstvie)
            bot.send_message(message.from_user.id, "Есть незарегистрировавшиеся работники, но вы всё равно можете прислать расписние, оно пришлется зарегистрированным пользовтелей") ## зарегистрировавшихся пользователей меньше чем официальный список
            bot.send_message(message.from_user.id, "ФИО незарегистрированых пользователей:" + q)

        elif spisoc_polz == spisoc_polz_ot_admina:

            bot.send_message(message.from_user.id, "Все работники зарегистрированы")

        elif spisoc_polz_ot_admina in spisoc_polz and len(spisoc_polz) > len(spisoc_polz_ot_admina):
            bot.send_message(message.from_user.id, "Все работники зарегистрированы") ## но есть зарегистрированные пользователи, которых нет в списке")
        
        else:
            otsutstvie = []
            for i in spisoc_polz_ot_admina:
                if i not in spisoc_polz:
                    otsutstvie.append(i)
            q = '\n'.join(otsutstvie)
            bot.send_message(message.from_user.id, "Есть незарегистрировавшиеся работники, но вы всё равно можете прислать расписние, оно пришлется зарегистрированным пользовтелей")
            bot.send_message(message.from_user.id, "Фамилии незарегистрированых пользователей:" + q)
        
        with open("json_user.json", "w") as fh:
            json.dump(user, fh)
    
    elif user[str(message.from_user.id)][1] == "Присылает дату":
        bot.send_message(message.from_user.id, "Пришлите график")
        global date
        date = message.text
        user[str(message.from_user.id)][1] = "Присылает таблицу"
        with open("json_user.json", "w") as fh:
            json.dump(user, fh)


  
@bot.message_handler(content_types=['document'])
def get_document_messages(message):
    with open("json_user.json", "r") as fh:
        user = json.load(fh)
        
    if user[str(message.from_user.id)][1] == "Присылает таблицу" and user[str(message.from_user.id)][0] == "adm":

        doc = Document()
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open("received_document.docx", "wb") as new_file:
            new_file.write(downloaded_file)

        doc.LoadFromFile("received_document.docx")  # Corrected usage of python-docx to open the file
        
        for i in range(doc.Sections.Count):
            section = doc.Sections.get_Item(i)
            tables = section.Tables
            for j in range(0, tables.Count): ## перебор таблиц
                table = tables.get_Item(j)
                for m in range(0, table.Rows.Count):
                    info = ""
                    for n in range(0, table.Rows.get_Item(m).Cells.Count): # перебор таблицы

                        cell = table.Rows.get_Item(m).Cells.get_Item(n)
                        cellText = ""
                        if m != 0: # вся остальная информация о съемке

                            for para in range(cell.Paragraphs.Count):
                                paragraphText = cell.Paragraphs.get_Item(para).Text
                                info += "\n" + paragraphText
                            if n == 3: # добавление времени и даты 
                                cor = table.Rows.get_Item(m).Cells.get_Item(n + 1)
                                corr = ""
                                for para in range(cor.Paragraphs.Count):
                                    corr = cor.Paragraphs.get_Item(para).Text # текст ячейки корреспондентов
                            
                                t = table.Rows.get_Item(m).Cells.get_Item(n)
                                time = []
                                for para in range(t.Paragraphs.Count):
                                    time.append(t.Paragraphs.get_Item(para).Text) # текст ячейки с временем
                                    Time = ' '.join(time)


                                a = []
                                for w in range(len(Time) - 2):
                                    if Time[w + 2] in ".:" and type(Time[w]) == int:
                                        a.append(int(Time[w:w + 2:]))
                                
                                if a:
                                    TIME = str(min(a)) + ".00"  # минимальное время нааписаное в ячейке
                                else:
                                    TIME = "12.00"



                                for key, value in user_change.items():
                                    for i in range(len(value)):
                                        if value[i][3] in corr: ## распознавание корреспондента
                                            value[i][0] = date
                                            value[i][1] = TIME
                                            value[i][2] = info
                        
        with open("json_user.json", "w") as fh:
            json.dump(user, fh)

        with open("user_changed.json", "w") as fh:
            json.dump(user_change, fh)


        for Id, value in user_change.items():
            print(user_change[str(Id)][0][2])
            if user_change[str(Id)][0][1] != "00:01":
                bot.send_message(int(Id), user_change[str(Id)][0][2])

       

        user[str(message.from_user.id)][1] = 4
        with open("json_user.json", "w") as fh:
            json.dump(user, fh)
 
def time_min():
    times = []
    for key, value in user_change.items():
        times.append(int(re.split(r'[;,.:\s]+', value[0][1])[0])) ##  Достаем значения часов
    time_rass = min(times)
try:
    if user_change:
        for Id, value in user_change.items():
            mounth, Date, time = re.split(r'[; ,.:\s]+', user_change[str(Id)][0][0])[1], re.split(r'[; ,.:\s]+', user_change[str(Id)][0][0])[0], re.split(r'[;,.:\s]+', user_change[str(Id)][0][0])[1]
            time_min()
            date = value[0][0]
            if time_rass >= 9:
                time_rass -= 24
            if datetime.now().timetuple().tm_mon >= int(mounth) and datetime.now().timetuple().tm_mday >= int(Date) and int(time_rass) + 15 <= datetime.now().timetuple().tm_hour and user_change[str(Id)][0][1] != "00:01": ## проверка на час и день
                bot.send_message(int(Id), user_change[str(Id)][0][2]) ## рассылка сообщений
                value.append(["01.01", "00:01", "остальная информация", "Имя фамилия"])
                user_change[str(Id)].pop(0)
except:
    bot.send_message(int(Id), "Дата в неверном формате")

    with open("json_user.json", "w") as fh:
            json.dump(user, fh)    

bot.polling(none_stop=True, interval=0)
