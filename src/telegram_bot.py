import telebot
import csv
import os
import requests
from datetime import datetime
from src.config import get_settings
from io import BytesIO

API_TOKEN = get_settings().telegram_token
print (API_TOKEN)

bot = telebot.TeleBot(API_TOKEN)

log_file = "user_log.csv"

API_URL = get_settings().api_url

def log_user_data(user_id, user_name, command_time, comando):
    file_exists = os.path.isfile(log_file)
    with open(log_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["User ID", "Username", "Command Time", "Date", "Command"])
        writer.writerow([user_id, user_name, command_time.strftime("%H:%M:%S"), command_time.strftime("%Y-%m-%d"), comando])


def get_user_ids_from_log():
    user_ids = set()
    try:
        with open(log_file, mode='r') as file:
            reader = csv.reader(file)
            next(reader, None)
            for row in reader:
                if row:
                    user_ids.add(int(row[0]))
    except FileNotFoundError:
        print("Archivo de log no encontrado.")
    return user_ids

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    command_time = datetime.now()
    comando = message.text

    log_user_data(user_id, user_name, command_time, comando)

    bot.reply_to(message, f"Hola {user_name}, bienvenido al bot de Analisis de Sentimientos y texto. Para ver los comandos disponibles, escribe /help")
    print (f"El {user_name} con ID {user_id} hizo el comando {comando} a las {command_time.strftime('%H:%M:%S')}")

@bot.message_handler(commands=['help'])
def handle_help(message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    command_time = datetime.now()
    comando = message.text
    log_user_data(user_id, user_name, command_time, comando)

@bot.message_handler(commands=['status'])
def handle_status(message):
    user_id = message.from_user.id
    allowed_user_ids = get_user_ids_from_log()

    if user_id not in allowed_user_ids:
        bot.reply_to(message, "No tienes permiso para usar este comando.")
        return

    user_name = message.from_user.username
    command_time = datetime.now()
    comando = message.text

    log_user_data(user_id, user_name, command_time, comando)

    status_url = API_URL + "status" 

    try:
        response = requests.get(status_url)
        if response.status_code == 200:
            status_data = response.json()
            reply_message = f"Estado del servicio: {status_data['status']}\n" \
                            f"Nombre del servicio: {status_data['service_name']}\n" \
                            f"Versión: {status_data['version']}\n" \
                            f"Nivel de log: {status_data['log_level']}\n" \
                            f"Modelos utilizados:\n" \
                            f"  - Sentiment Model: {status_data['models_info']['sentiment_model']}\n" \
                            f"  - NLP Model: {status_data['models_info']['nlp_model']}\n" \
                            f"  - GPT Model: {status_data['models_info']['gpt_model']}"
        else:
            reply_message = "Error al obtener el estado del servicio."
    except requests.exceptions.RequestException as e:
        reply_message = f"Error al conectarse con la API: {e}"

    print (f"El {user_name} con ID {user_id} hizo el comando {comando} a las {command_time.strftime('%H:%M:%S')}")
    bot.reply_to(message, reply_message)

@bot.message_handler(commands=['sentiment'])
def handle_sentiment(message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    command_time = datetime.now()
    comando = message.text

    log_user_data(user_id, user_name, command_time, comando)

    bot.send_message(user_id, "Por favor, envía el texto para el análisis de sentimiento.")

    bot.register_next_step_handler(message, analyze_sentiment_step)

def analyze_sentiment_step(message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    command_time = datetime.now()
    text = message.text

    sentiment_url = API_URL + "sentiment"
    payload = {"text": text}

    try:
        response = requests.post(sentiment_url, json=payload)
        if response.status_code == 200:
            sentiment_data = response.json()
            label = sentiment_data["prediction"]["label"]
            score = sentiment_data["prediction"]["score"]
            reply_message = f"Análisis de Sentimiento:\n" \
                            f"Texto: {text}\n" \
                            f"Sentimiento: {label}\n" \
                            f"Puntuación: {score}"
        else:
            reply_message = "Error al realizar el análisis de sentimiento."
    except requests.exceptions.RequestException as e:
        reply_message = f"Error al conectarse con la API: {e}"

    print (f"El {user_name} con ID {user_id} hizo el análisis de sentimiento a las {command_time.strftime('%H:%M:%S')}")
    bot.send_message(user_id, reply_message)

@bot.message_handler(commands=['analysis'])
def handle_analysis(message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    command_time = datetime.now()
    comando = message.text

    log_user_data(user_id, user_name, command_time, comando)

    bot.send_message(user_id, "Por favor, envía el texto para el análisis de texto.")

    bot.register_next_step_handler(message, analyze_text_step)

def analyze_text_step(message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    command_time = datetime.now()
    text = message.text

    analysis_url = API_URL + "analysis"
    payload = {"text": text}

    try:
        response = requests.post(analysis_url, json=payload)
        if response.status_code == 200:
            analysis_data = response.json()
            reply_message = "Análisis de Texto:\n"
            reply_message += f"Texto: {text}\n"
            reply_message += f"Resumen POS Tags: {analysis_data['nlp_analysis']['pos_tags_summary']}\n"
            reply_message += f"Resumen NER: {analysis_data['nlp_analysis']['ner_summary']}\n"
            reply_message += f"Sentimiento: {analysis_data['sentiment_analysis']['label']}\n"
            reply_message += f"Puntuación de Sentimiento: {analysis_data['sentiment_analysis']['score']}"
        else:
            reply_message = "Error al realizar el análisis de texto."
    except requests.exceptions.RequestException as e:
        reply_message = f"Error al conectarse con la API: {e}"

    print (f"El {user_name} con ID {user_id} hizo el análisis de texto a las {command_time.strftime('%H:%M:%S')}")
    bot.send_message(user_id, reply_message)

@bot.message_handler(commands=['reports'])
def handle_reports(message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    command_time = datetime.now()
    comando = message.text

    log_user_data(user_id, user_name, command_time, comando)

    reports_url = API_URL + "reports"

    try:
        response = requests.get(reports_url)
        if response.status_code == 200:
            report_file = BytesIO(response.content)
            report_file.name = "reporte_general.csv"
            bot.send_document(user_id, report_file, caption="Informe Combinado")
        else:
            bot.send_message(user_id, "Error al obtener el informe combinado.")
    except requests.exceptions.RequestException as e:
        bot.send_message(user_id, f"Error al conectarse con la API: {e}")

    print (f"El {user_name} con ID {user_id} solicitó el informe combinado a las {command_time.strftime('%H:%M:%S')}")

