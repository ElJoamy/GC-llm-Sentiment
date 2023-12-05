import os
import time
import spacy
import csv
# import src.telegram_bot as telegram_bot
import psutil
from fastapi import FastAPI, UploadFile, File, HTTPException, status,Depends, Request
from fastapi.responses import JSONResponse, Response, FileResponse
from functools import cache
from datetime import datetime
from starlette.middleware.cors import CORSMiddleware
from src.Sentiment import SentimentAnalysisService
from src.config import get_settings
from src.verification import check_and_create_csv, get_csv_file_path, append_to_csv
from typing import List
from src.response_models import (
    CombinedReportResponse,
    SentimentAnalysisResponse,
    TextAnalysisResponse,
    StatusResponse,
)
from threading import Thread

_SETTINGS = get_settings()

app = FastAPI(
    title=_SETTINGS.service_name,
    version=_SETTINGS.k_revision
)

# def start_telegram_bot():
#     telegram_bot.bot.polling(none_stop=True)

nlp = spacy.load("es_core_news_sm")

def get_sentiment_service():
    return SentimentAnalysisService()

@app.get("/reports", response_model=List[CombinedReportResponse], summary="Obtiene informe combinado", description="Obtiene un informe combinado de datos.")
def get_combined_reports():
    sentiment_file_path = get_csv_file_path("sentiment")
    analysis_file_path = get_csv_file_path("analysis")
    combined_file_path = get_csv_file_path("general")

    check_and_create_csv(sentiment_file_path, ["Nombre del Archivo", "Label", "Score", "Fecha y Hora", "Tiempo de Ejecución", "Modelos", "Longitud del Texto", "Uso de Memoria", "Uso de CPU"])
    check_and_create_csv(analysis_file_path, ["Texto Analizado", "POS Tags Resumen", "POS Tags Conteo", "NER Resumen", "NER Conteo", "Sentimiento Label", "Sentimiento Score", "Fecha y Hora", "Tiempo de Ejecución", "Modelos", "Longitud del Texto", "Uso de Memoria", "Uso de CPU"])

    with open(combined_file_path, 'w', newline='', encoding='utf-8') as combined_file:
        combined_writer = csv.writer(combined_file)

        with open(sentiment_file_path, 'r', encoding='utf-8') as sentiment_file:
            sentiment_reader = csv.reader(sentiment_file)
            for row in sentiment_reader:
                combined_writer.writerow(row)

        with open(analysis_file_path, 'r', encoding='utf-8') as analysis_file:
            analysis_reader = csv.reader(analysis_file)
            next(analysis_reader)
            for row in analysis_reader:
                combined_writer.writerow(row)

    return FileResponse(combined_file_path, media_type="text/csv", filename="reporte_general.csv")

@app.post("/sentiment", response_model=SentimentAnalysisResponse, summary="Analiza sentimiento", description="Realiza un análisis de sentimiento en el texto proporcionado.")
def analyze_sentiment(text: str, sentiment_service: SentimentAnalysisService = Depends(SentimentAnalysisService)):
    start_time = time.time()
    result = sentiment_service.analyze_sentiment(text)
    end_time = time.time()
    execution_time = end_time - start_time

    prediction_datetime = datetime.now().isoformat()
    text_length = len(text)
    model_version = _SETTINGS.sentiment_model_id 
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info().rss 
    cpu_usage = process.cpu_percent(interval=1)

    adjusted_score = (result[0]['score'] * 2) - 1

    csv_data = {
        "Nombre del Archivo": "Sentiment Analysis",
        "Texto Analizado": text,
        "Label": result[0]['label'],
        "Score": adjusted_score,
        "Fecha y Hora": prediction_datetime,
        "Tiempo de Ejecución": execution_time,
        "Modelos": model_version,
        "Longitud del Texto": text_length,
        "Uso de Memoria": memory_info,
        "Uso de CPU": cpu_usage
    }
    file_path = get_csv_file_path("sentiment")
    headers = ["Nombre del Archivo", "Texto Analizado", "Label", "Score", "Fecha y Hora", "Tiempo de Ejecución", "Modelos", "Longitud del Texto", "Uso de Memoria", "Uso de CPU"]
    append_to_csv(file_path, csv_data, headers)

    return {
        "prediction": {
            "label": result[0]['label'],
            "score": adjusted_score
        },
        "execution_info": {
            "execution_time": execution_time,
            "prediction_datetime": prediction_datetime,
            "text_length": text_length,
            "model_version": model_version,
            "memory_usage": memory_info,
            "cpu_usage": cpu_usage
        }
    }

@app.post("/analysis", response_model=TextAnalysisResponse, summary="Analiza texto", description="Realiza un análisis de texto, incluyendo etiquetas POS y entidades NER, y también realiza un análisis de sentimiento.")
def analyze_text(text: str, sentiment_service: SentimentAnalysisService = Depends(get_sentiment_service)):
    start_time = time.time()

    doc = nlp(text)
    pos_tags = [(token.text, token.pos_) for token in doc]
    ner_entities = [(ent.text, ent.label_) for ent in doc.ents]

    pos_tags_summary = {tag: [] for _, tag in pos_tags}
    for word, tag in pos_tags:
        pos_tags_summary[tag].append(word)
    pos_tag_count = {tag: len(words) for tag, words in pos_tags_summary.items()}

    ner_summary = {label: [] for _, label in ner_entities}
    for text, label in ner_entities:
        ner_summary[label].append(text)
    ner_count = {label: len(texts) for label, texts in ner_summary.items()}

    sentiment_result = sentiment_service.analyze_sentiment(text)
    adjusted_score = (sentiment_result[0]['score'] * 2) - 1

    end_time = time.time()
    execution_time = end_time - start_time

    prediction_datetime = datetime.now().isoformat()
    text_length = len(text)
    model_version = "Spacy & Sentiment Model"
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info().rss
    cpu_usage = process.cpu_percent(interval=1)

    csv_data = {
        "Texto Analizado": text,
        "POS Tags Resumen": str(pos_tags_summary),
        "POS Tags Conteo": str(pos_tag_count),
        "NER Resumen": str(ner_summary),
        "NER Conteo": str(ner_count),
        "Sentimiento Label": sentiment_result[0]['label'],
        "Sentimiento Score": adjusted_score,
        "Fecha y Hora": prediction_datetime,
        "Tiempo de Ejecución": execution_time,
        "Modelos": model_version,
        "Longitud del Texto": text_length,
        "Uso de Memoria": memory_info,
        "Uso de CPU": cpu_usage
    }
    file_path = get_csv_file_path("analysis")
    headers = ["Texto Analizado", "POS Tags Resumen", "POS Tags Conteo", "NER Resumen", "NER Conteo", "Sentimiento Label", "Sentimiento Score", "Fecha y Hora", "Tiempo de Ejecución", "Modelos", "Longitud del Texto", "Uso de Memoria", "Uso de CPU"]
    append_to_csv(file_path, csv_data, headers)

    return {
        "nlp_analysis": {
            "pos_tags_summary": pos_tags_summary,
            "pos_tag_count": pos_tag_count,
            "ner_summary": ner_summary,
            "ner_count": ner_count,
            "embeddings": [token.vector.tolist() for token in doc]
        },
        "sentiment_analysis": {
            "label": sentiment_result[0]['label'],
            "score": adjusted_score
        },
        "execution_info": {
            "execution_time": execution_time,
            "prediction_datetime": prediction_datetime,
            "text_length": text_length,
            "model_version": model_version,
            "memory_usage": memory_info,
            "cpu_usage": cpu_usage
        }
    }

@app.get("/status", response_model=StatusResponse, summary="Obtiene estado del servicio", description="Obtiene el estado actual del servicio, incluyendo información sobre los modelos utilizados.")
def get_status():
    return {
        "service_name": _SETTINGS.service_name,
        "version": _SETTINGS.k_revision,
        "log_level": _SETTINGS.log_level,
        "status": "Running",
        "models_info": {
            "sentiment_model": _SETTINGS.sentiment_model_id,
            "nlp_model": "Spacy es_core_news_sm",
            "gpt_model": _SETTINGS.model 
        }
    }


if __name__ == "__main__":
    import uvicorn
    # Thread(target=start_telegram_bot).start()
    uvicorn.run("src.main:app", reload=True)