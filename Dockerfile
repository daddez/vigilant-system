# 1. Usiamo l'immagine snella con Python 3.12
FROM python:3.12-slim

# 2. Evitiamo interruzioni durante l'installazione
ENV DEBIAN_FRONTEND=noninteractive

# 3. Installiamo le librerie video/grafiche di sistema base
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# ==========================================
# 4. GLI SPECCHI MAGICI (SYMLINKS)
# ==========================================
# Inganna i percorsi assoluti dei file dicendo che workspace è runpod-volume
RUN ln -s /runpod-volume /workspace
# Inganna l'ambiente virtuale fornendogli il collegamento al vecchio nome di Python
RUN ln -s /usr/local/bin/python /usr/bin/python3.12

# 5. Installiamo la libreria di comunicazione di RunPod
RUN pip install --no-cache-dir runpod requests

# 6. Copiamo il tuo cervello Serverless
COPY handler.py /handler.py

# 7. Accendiamo il ricevitore
CMD ["python", "-u", "/handler.py"]
