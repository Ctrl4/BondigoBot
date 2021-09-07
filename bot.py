import telegram
import telegram.ext
import re
from random import randint
import logging
import requests
from obtenerBondi import obtenerBondi
from crontab import CronTab
import os

cron = CronTab(user='ctrl4')
es_agenda = False

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

API_KEY = os.environ['TELEGRAM']
updater = telegram.ext.Updater(API_KEY)
dispatcher = updater.dispatcher

WELCOME = 0
CONSULTAR = 1
AGENDAR = 2
PEDIR_BONDI = 3
PEDIR_PARADA = 4
CANCEL = 5


# The entry function
def start(update_obj, context):
    update_obj.message.reply_text("""¡Hola! Este Bot te ayudará a saber a que hora pasa tu próximo ómnibus.
¡En un futuro hasta podrás agendar alertar para saber cuando pasa ese ómnibus que esperás todos los días a la misma hora!

Opciones:
    1)Consultar
    2)Agendar
    0)Cancelar""", reply_markup=telegram.ReplyKeyboardMarkup([["1","2","0"]], one_time_keyboard=True))
    return WELCOME


def preguntarBondi(update_obj, context):
    global bondi
    bondi = update_obj.message.text

    update_obj.message.reply_text(f"Pasame número de la parada. Recordá que podés obtener este dato en blablabla.com")

    return PEDIR_PARADA

def preguntarParada(update_obj, context):
    global parada
    parada = update_obj.message.text

    if es_agenda:
        update_obj.message.reply_text(f"Te vamo a avisar")
        job = cron.new(command=f'/usr/bin/python3 /home/ctrl4/mounted/ctrl4/git/BondigoBot/obtenerBondi.py  -b{bondi} -p{parada}')
        job.hour.every(1)
        cron.write()
    else:
        update_obj.message.reply_text(f"Consultando tiempo ")
        update_obj.message.reply_text(obtenerBondi(bondi, parada),reply_markup=telegram.ReplyKeyboardRemove())

    return telegram.ext.ConversationHandler.END

def cancel(update_obj, context):
    # get the user's first name
    first_name = update_obj.message.from_user['first_name']
    update_obj.message.reply_text(
        f"Okay, no question for you then, take care, {first_name}!", reply_markup=telegram.ReplyKeyboardRemove()
    )
    return telegram.ext.ConversationHandler.END




def welcome(update_obj, context):
    if int(update_obj.message.text) == 1:
        update_obj.message.reply_text(f"Pasame número del ómnibus.")
        return PEDIR_BONDI
    elif int(update_obj.message.text) == 2:
        global es_agenda
        es_agenda = True
        update_obj.message.reply_text(f"Pasame número del ómnibus")
        return PEDIR_BONDI
    else:
        return CANCEL

def agendar(update_obj, context):
    update_obj.message.reply_text(f"Perdón viejo pero no podés agendar aún.(Soon)")
    return start(update_obj, context)


yes_no_regex = re.compile(r'^(yes|no|y|n)$', re.IGNORECASE)

handler = telegram.ext.ConversationHandler(
      entry_points=[telegram.ext.CommandHandler('start', start)],
      states={
            WELCOME: [telegram.ext.MessageHandler(telegram.ext.Filters.regex(r'^\d+$'), welcome)],
            PEDIR_BONDI: [telegram.ext.MessageHandler(telegram.ext.Filters.regex(r'^\d+$'), preguntarBondi)],
            PEDIR_PARADA: [telegram.ext.MessageHandler(telegram.ext.Filters.regex(r'^\d+$'), preguntarParada)],
            AGENDAR: [telegram.ext.MessageHandler(telegram.ext.Filters.regex(r'^\d+$'), agendar)],
            CANCEL: [telegram.ext.MessageHandler(telegram.ext.Filters.regex(yes_no_regex), cancel)],
      },
      fallbacks=[telegram.ext.CommandHandler('cancel', cancel)],
      )

dispatcher.add_handler(handler)
updater.start_polling()
updater.idle()
