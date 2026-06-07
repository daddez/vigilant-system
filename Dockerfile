# 1. Usiamo un'immagine snella e pulita con l'esatta versione: Python 3.12
FROM python:3.12-slim

# 2. Evitiamo interruzioni durante l'installazione
ENV DEBIAN_FRONTEND=noninteractive

# 3. Installiamo le librerie di sistema necessarie per OpenCV e per la manipolazione delle immagini
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. Installiamo la libreria di RunPod per far comunicare il Serverless
RUN pip install --no-cache-dir runpod requests

# 5. Copiamo il tuo handler.py all'interno della macchina virtuale
COPY handler.py /handler.py

# 6. Diciamo alla macchina cosa fare all'accensione
CMD ["python", "-u", "/handler.py"]
