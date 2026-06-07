# 1. Usiamo l'immagine snella con Python 3.12
FROM python:3.12-slim

# 2. Evitiamo interruzioni durante l'installazione
ENV DEBIAN_FRONTEND=noninteractive

# 3. Installiamo le librerie di sistema
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# ==========================================
# LA MAGIA: Creiamo lo specchio per il VENV
# ==========================================
RUN ln -s /runpod-volume /workspace

# 4. Installiamo la libreria di RunPod
RUN pip install --no-cache-dir runpod requests

# 5. Copiamo il tuo handler.py
COPY handler.py /handler.py

# 6. Accensione
CMD ["python", "-u", "/handler.py"]
