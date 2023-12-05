# Cloud Project Generator
`Nombre`: Joseph Anthony Meneses Salguero
`Codigo`: 55669

## Descripción
Este proyecto es un servicio de análisis de texto y sentimiento, implementado en Python y desplegado con Docker en Google Cloud. Utiliza FastAPI para la creación de endpoints, Spacy para el análisis de texto y la librería Transformers para el análisis de sentimiento.

## Estructura del Proyecto
La estructura de archivos del proyecto es la siguiente:

```bash
.
├── .env
├── .gitignore
├── Dockerfile
├── README.md
├── report_analysis.csv
├── report_general.csv
├── report_sentiment.csv
├── requirements.txt
├── tree.txt
└── src
    ├── config.py
    ├── main.py
    ├── response_models.py
    ├── Sentiment.py
    └── verification.py
```

## Instalación
### Requisitos Previos
- Python 3.11
- Docker [Instalación](Installation/Docker.md)

### Pasos para la Instalación
1. Clona el repositorio:
   ```bash
   git clone https://github.com/ElJoamy/GC-llm-Sentiment.git
   ```
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

### Uso de Docker
Para construir y ejecutar el servicio usando Docker:
```bash
docker build -t myapp .
docker run -p 8080:8080 myapp
```

## Uso
El servicio puede ser accedido a través de su API, el cual ya esta deployado en GC [Swagger UI](https://gc-llm-sentiment-ll76tuby5a-uc.a.run.app/docs).

### Endpoints
- `/reports`: Obtener un informe combinado de datos.
- `/sentiment`: Analizar el sentimiento de un texto dado.
- `/analysis`: Realizar un análisis de texto completo.
- `/status`: Obtener el estado actual del servicio.

## Licencia
[MIT License](LICENSE)