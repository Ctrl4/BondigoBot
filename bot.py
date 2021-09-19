import logging
import os
import re

import telegram
import telegram.ext
from crontab import CronTab

from obtenerBondi import obtenerbondi


API_KEY = os.environ['TELEGRAM']
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
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
Hasta podrás agendar alertar para saber cuando pasa ese ómnibus que esperás todos los días a la misma hora!

Opciones:
    1)Consultar
    2)Agendar
    0)Cancelar""", reply_markup=telegram.ReplyKeyboardMarkup([["1","2","0"]], one_time_keyboard=True))
    return WELCOME


def preguntarbondi(update_obj, context):
    context.chat_data['bondi'] = str(update_obj.message.text)
    update_obj.message.reply_text(f"Pasame número de la parada.")
    update_obj.message.reply_text(f" Estamos trabajando en mejorar la obtención de este dato. Mandame un MD que te lo consigo: @ctrl4")
    return PREGUNTAR_PARADA


def preguntarparada(update_obj, context):
    context.chat_data['parada'] = str(update_obj.message.text)

    bondi = context.chat_data['bondi']
    parada = context.chat_data['parada']
    es_agenda = context.chat_data['es_agenda']
#    breakpoint()
    if es_agenda:
        horas = context.chat_data['horas']
        minutos = context.chat_data['minutos']
        dias = context.chat_data['dias']
        job = cron.new(command=f"export TELEGRAM={API_KEY} && /usr/bin/python3 {BASE_DIR}/obtenerBondi.py  -b{bondi} -p{parada} -i{update_obj.message.chat_id}")
        job.hour.on(horas)
        job.minute.on(minutos)
        job.dow.on(*dias)
        cron.write()
        update_obj.message.reply_text(f"""Quedó configurada la alarma para el {bondi} en la parada {parada} con los siguientes datos:
Hora: {horas}:{minutos}
Dias: {dias}""",
                                      reply_markup=telegram.ReplyKeyboardRemove())
        update_obj.message.reply_text(f"""Por lo pronto no se puede eliminar la agenda desde el bot. Si querés dejar de recibirlas, mandame un MD @ctrl4.""")
    else:
        update_obj.message.reply_text(f"Consultando tiempo ")
        update_obj.message.reply_text(obtenerbondi(bondi, parada),
                                      reply_markup=telegram.ReplyKeyboardRemove())
    return telegram.ext.ConversationHandler.END


def cancel(update_obj, context):
    # get the user's first name
    first_name = update_obj.message.from_user['first_name']
    update_obj.message.reply_text(
        f"Okay, no question for you then, take care, {first_name}!",
        reply_markup=telegram.ReplyKeyboardRemove()
    )
    return telegram.ext.ConversationHandler.END


def welcome(update_obj, context):
    context.chat_data['es_agenda'] = False
    if int(update_obj.message.text) == 1:
        update_obj.message.reply_text(f"Pasame número del ómnibus.",
                                      reply_markup=telegram.ReplyKeyboardRemove())
        return PREGUNTAR_BONDI
    elif int(update_obj.message.text) == 2:
        context.chat_data["es_agenda"] = True
        update_obj.message.reply_text(f"""¿Qué días querés agendar?
Algunos ejemplos:
0 = Domingo,
1 = Lunes,
2 = Martes,
3 = Miércoles,
4 = Jueves,
5 = Viernes,
6 = Sábado

Si querés distintos días a la semana podés poner cada número separado por coma. Es decir:
# Lunes, Miercoles y Viernes = 1,3,5
        """, reply_markup=telegram.ReplyKeyboardRemove())
        return PREGUNTAR_DIAS
    else:
        return CANCEL


def preguntarDias(update_obj, context):
    context.chat_data['dias'] = list(map(int, update_obj.message.text.split(",")))
    update_obj.message.reply_text(f"¿A que hora querés que te empecemos avisar? (Entre 0 y 23)")
    return PREGUNTAR_HORAS


def preguntarHoras(update_obj, context):
    context.chat_data['horas'] = update_obj.message.text
    update_obj.message.reply_text(f"Pasame minutos (Entre 0 y 59)")
    return PREGUNTAR_MINUTOS


def preguntarMinutos(update_obj, context):
    context.chat_data['minutos'] = update_obj.message.text
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
