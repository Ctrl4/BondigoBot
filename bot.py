import logging
import os
import re

import telegram
import telegram.ext
from crontab import CronTab

from obtenerBondi import obtenerbondi

API_KEY = os.environ['TELEGRAM']
cron = CronTab(user=True)
es_agenda = False
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
updater = telegram.ext.Updater(API_KEY)
dispatcher = updater.dispatcher

WELCOME = 0
CONSULTAR = 1
AGENDAR = 2
PREGUNTAR_BONDI = 3
PREGUNTAR_PARADA = 4
PREGUNTAR_DIAS = 5
PREGUNTAR_HORAS = 6
PREGUNTAR_MINUTOS = 7
CANCEL = 8


# The entry function
def start(update_obj, context):
    update_obj.message.reply_text("""¡Hola! Este Bot te ayudará a saber a que hora pasa tu próximo ómnibus.
¡En un futuro hasta podrás agendar alertar para saber cuando pasa ese ómnibus que esperás todos los días a la misma hora!

Opciones:
    1)Consultar
    2)Agendar
    0)Cancelar""", reply_markup=telegram.ReplyKeyboardMarkup([["1","2","0"]], one_time_keyboard=True))
    return WELCOME


def preguntarbondi(update_obj, context):
    context.user_data['bondi'] = str(update_obj.message.text)
    update_obj.message.reply_text(f"Pasame número de la parada. Recordá que podés obtener este dato en blablabla.com")
    return PREGUNTAR_PARADA


def preguntarparada(update_obj, context):
    context.user_data['parada'] = str(update_obj.message.text)

    bondi = context.user_data['bondi']
    parada = context.user_data['parada']
    es_agenda = context.user_data['es_agenda']
#    breakpoint()
    if es_agenda:
        horas = context.user_data['horas']
        minutos = context.user_data['minutos']
        dias = context.user_data['dias']
        update_obj.message.reply_text(f"A partir de la hora especificada te vamos a estar alertando cada 1 minuto (max 5 minutos)",reply_markup=telegram.ReplyKeyboardRemove())
        job = cron.new(command=f"export TELEGRAM={API_KEY} && /usr/bin/python3 /home/ctrl4/mounted/ctrl4/git/BondigoBot/obtenerBondi.py  -b{bondi} -p{parada} -i{update_obj.message.chat_id}")
        job.hour.on(horas)
        job.minute.on(minutos)
        job.dow.on(dias)
        cron.write()
    else:
        update_obj.message.reply_text(f"Consultando tiempo ")
        update_obj.message.reply_text(obtenerbondi(bondi, parada), reply_markup=telegram.ReplyKeyboardRemove())
    return telegram.ext.ConversationHandler.END


def cancel(update_obj, context):
    # get the user's first name
    first_name = update_obj.message.from_user['first_name']
    update_obj.message.reply_text(
        f"Okay, no question for you then, take care, {first_name}!", reply_markup=telegram.ReplyKeyboardRemove()
    )
    return telegram.ext.ConversationHandler.END


def welcome(update_obj, context):
    context.user_data['es_agenda'] = False
    if int(update_obj.message.text) == 1:
        update_obj.message.reply_text(f"Pasame número del ómnibus.")
        return PREGUNTAR_BONDI
    elif int(update_obj.message.text) == 2:
        context.user_data["es_agenda"] = True
        update_obj.message.reply_text(f"""¿Qué días querés agendar?
Para todos los días escribi: todos
Para rango semanal por ejempĺo Lunes a viernes escribi: MON-FRI
        """)
        return PREGUNTAR_DIAS
    else:
        return CANCEL


def preguntarDias(update_obj, context):
    context.user_data['dias'] = tuple(update_obj.message.text)
    update_obj.message.reply_text(f"¿A que hora querés que te empecemos avisar? (Entre 0 y 23)")
    return PREGUNTAR_HORAS


def preguntarHoras(update_obj, context):
    context.user_data['horas'] = update_obj.message.text
    update_obj.message.reply_text(f"Pasame minutos (Entre 0 y 59)")
    return PREGUNTAR_MINUTOS


def preguntarMinutos(update_obj, context):
    context.user_data['minutos'] = update_obj.message.text
    update_obj.message.reply_text(f"Pasame número del ómnibus.")
    return PREGUNTAR_BONDI


yes_no_regex = re.compile(r'^(yes|no|y|n)$', re.IGNORECASE)
handler = telegram.ext.ConversationHandler(
      entry_points=[telegram.ext.CommandHandler('start', start)],
      states={
            WELCOME: [telegram.ext.MessageHandler(telegram.ext.Filters.regex(r'^\d+$'), welcome)],
            PREGUNTAR_BONDI: [telegram.ext.MessageHandler(telegram.ext.Filters.regex(r'^\d+$'), preguntarbondi)],
            PREGUNTAR_PARADA: [telegram.ext.MessageHandler(telegram.ext.Filters.regex(r'^\d+$'), preguntarparada)],
            PREGUNTAR_DIAS: [telegram.ext.MessageHandler(telegram.ext.Filters.all, preguntarDias)],
            PREGUNTAR_HORAS: [telegram.ext.MessageHandler(telegram.ext.Filters.all, preguntarHoras)],
            PREGUNTAR_MINUTOS: [telegram.ext.MessageHandler(telegram.ext.Filters.all, preguntarMinutos)],
            CANCEL: [telegram.ext.MessageHandler(telegram.ext.Filters.regex(yes_no_regex), cancel)],
      },
      fallbacks=[telegram.ext.CommandHandler('cancel', cancel)],
      )
dispatcher.add_handler(handler)
updater.start_polling()
updater.idle()
