import telebot
from requests import Session
from database import conn, cursor

bot = telebot.TeleBot('5529392214:AAHS0ymozmFX6mjVzIIR-F76JxR7dUl-cqM')
apiKey = '90c0eb2631ea1750e8e024d99d413f41'
session = Session()

data = {}
@bot.message_handler(commands=['start'])
def welcome(message):
    # membalas pesan
    bot.send_message(
        message.chat.id,
        'Bot Pantau Resi ngasih notif kalo paketnya gerak, biar gak appnya buka terus.\n'
        'Kode kurir: pos, wahana, jnt, sap, sicepat, jet, dse, first, ninja, lion, idl, rex, ide, sentral, anteraja, jtl'
    )

@bot.message_handler(commands=['pantau'])
def watch(message):
    bot.send_message(message.chat.id, 'Masukkan resinya geng')
    bot.register_next_step_handler(message, handleResi)

def handleResi(message):
    data["resi"] = message.text
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton('POS', callback_data='kurir-pos'),
        telebot.types.InlineKeyboardButton('WAHANA', callback_data='kurir-wahana')
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton('JNT', callback_data='kurir-jnt'),
        telebot.types.InlineKeyboardButton('SAP', callback_data='kurir-sap')
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton('SICEPAT', callback_data='kurir-sicepat'),
        telebot.types.InlineKeyboardButton('JET', callback_data='kurir-jet')
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton('DSE', callback_data='kurir-dse'),
        telebot.types.InlineKeyboardButton('FIRST', callback_data='kurir-first')
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton('NINJA', callback_data='kurir-ninja'),
        telebot.types.InlineKeyboardButton('LION', callback_data='kurir-lion')
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton('IDL', callback_data='kurir-idl'),
        telebot.types.InlineKeyboardButton('REX', callback_data='kurir-rex')
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton('IDE', callback_data='kurir-ide'),
        telebot.types.InlineKeyboardButton('SENTRAL', callback_data='kurir-sentral')
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton('ANTERAJA', callback_data='kurir-anteraja'),
        telebot.types.InlineKeyboardButton('JTL', callback_data='kurir-jtl')
    )
    bot.send_message(message.chat.id, 'Pilih kurirnya gesyak', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def iq_callback(query):
    val = query.data
    if val.startswith('kurir-'):
        bot.answer_callback_query(query.id)
        getTrackingData(query.message.chat.id, query.data[6:])
    elif val.startswith('save-'):
        bot.answer_callback_query(query.id)
        handleAutoUpdate(query.message, query.data[5:])

def getTrackingData(chatId, courier):
    bot.send_chat_action(chatId, 'typing')
    data["kurir"] = courier
    results = apiTracking(data)
    serveData(chatId, results)
    

def serveData(chatId, results):
    if(results["status"]["code"] == 200):
        manifest = ''
        results = results["result"]
        for val in results["manifest"]:
            manifest += (val["manifest_code"] + " | " + val["manifest_description"] + " | " + val["manifest_date"] + " " + val["manifest_time"] + "\n\n")
        response = ('Ekspedisi: ' + results["summary"]["courier_name"] + '\n' +
        'Resi: ' + results["summary"]["waybill_number"] + '\n' +
        'Pengirim: ' + results["summary"]["shipper_name"] + '\n' +
        'Penerima: ' + results["summary"]["receiver_name"] + '\n\n' +
        'Manifest: \n' + manifest)
        bot.send_message(chatId, response)
        data["manifest"] = str(results["manifest"])
        cursor.execute("SELECT id FROM waybill WHERE NOT waybill = ?", (results["summary"]["waybill_number"],))
        isExists = cursor.fetchall()
        if len(isExists) == 0 and results["summary"]["status"] != 'DELIVERED':
            afterTracking(chatId, results["summary"])
    else:
        response = results["status"]["description"]
        bot.send_message(chatId, response)

def afterTracking(chatId, res):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton('YES',
        callback_data='save-yes|'+res["waybill_number"]+"|"+res["courier_code"]+"|"+res["status"]),
        telebot.types.InlineKeyboardButton('NO', callback_data='save-no')
    )
    bot.send_message(chatId, 'Mo dikirim auto update gak?', reply_markup=keyboard)

def handleAutoUpdate(message, isSaved):
    summary = isSaved.split("|")
    if(summary[0] == 'yes'):
        bot.send_message(message.chat.id, 'Syap! ntar gue updatein yak kalo paket lo gerak')
        cursor.execute("SELECT id FROM waybill WHERE waybill = ?", (summary[1],))

        if item := cursor.fetchone():
            pass
        else:
            item = (None, message.chat.id, summary[1], summary[2], data["manifest"], summary[3])
            cursor.execute("INSERT INTO waybill VALUES(?, ?, ?, ?, ?, ?);", item)
            conn.commit()
    else:
        bot.send_message(message.chat.id, 'Yaudah engga deh')

def apiTracking(data):
    url = 'https://pro.rajaongkir.com/api/waybill'
    payload = {
        'waybill': data["resi"],
        'courier': data["kurir"]
    }
    headers = {
        'key': apiKey,
        'content-type': "application/x-www-form-urlencoded"
    }
    jsonData = session.post(url, headers=headers, data=payload).json()
    return jsonData["rajaongkir"]

bot.infinity_polling()