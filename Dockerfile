# 1. Base snella
FROM python:3.12-slim
ENV DEBIAN_FRONTEND=noninteractive

# 2. Librerie di sistema indispensabili
RUN apt-get update && apt-get install -y \
    git \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. Copiamo il file requirements.txt dal tuo GitHub al container
COPY requirements.txt /requirements.txt

# 4. Installiamo TUTTE le dipendenze di ComfyUI globalmente nell'immagine
RUN pip install --no-cache-dir -r /requirements.txt

# 5. Installiamo le dipendenze per l'API Serverless
RUN pip install --no-cache-dir runpod requests

# 6. Copiamo il tuo handler
COPY handler.py /handler.py

# 7. Avvio
CMD ["python", "-u", "/handler.py"]
