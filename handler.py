import runpod
import subprocess
import time
import requests
import os
import base64
import urllib.request
import urllib.parse

# ==========================================
# CONFIGURAZIONE PERCORSI (BLINDATI)
# ==========================================
COMFYUI_DIR = "/runpod-volume/runpod-slim/ComfyUI"
PYTHON_EXECUTABLE = f"{COMFYUI_DIR}/.venv-cu128/bin/python"
COMFYUI_PORT = "8188"
COMFYUI_URL = f"http://127.0.0.1:{COMFYUI_PORT}"

def start_comfyui():
    """Avvia ComfyUI in background usando il tuo ambiente virtuale."""
    print("Verifica ambiente virtuale in corso...")
    
    if not os.path.exists(PYTHON_EXECUTABLE):
        print(f"ERRORE: Venv non trovato in {PYTHON_EXECUTABLE}")
        print("Fallback sul Python globale di emergenza.")
        cmd_python = "python"
    else:
        print(f"Venv trovato! Utilizzo: {PYTHON_EXECUTABLE}")
        cmd_python = PYTHON_EXECUTABLE
    
    # Avvia main.py da dentro la cartella ComfyUI
    cmd = [cmd_python, "main.py", "--listen", "127.0.0.1", "--port", COMFYUI_PORT]
    subprocess.Popen(cmd, cwd=COMFYUI_DIR)

    # Attendi che ComfyUI sia pronto a ricevere richieste
    print("In attesa dell'avvio di ComfyUI locale...")
    while True:
        try:
            response = requests.get(f"{COMFYUI_URL}/system_stats", timeout=1)
            if response.status_code == 200:
                print("ComfyUI è operativo!")
                break
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)

def get_image(filename, subfolder, folder_type):
    """Scarica l'immagine appena generata."""
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen(f"{COMFYUI_URL}/view?{url_values}") as response:
        return response.read()

def handler(job):
    """Questa funzione viene chiamata per ogni generazione."""
    job_input = job['input']
    
    workflow = job_input.get('workflow', {})
    if not workflow:
         return {"error": "Nessun workflow fornito nell'input."}

    # =======================================================
    # NOVITÀ: SALVATAGGIO IMMAGINI IN INGRESSO SUL DISCO
    # =======================================================
    input_images = job_input.get('input_images', {})
    input_dir = os.path.join(COMFYUI_DIR, "input")
    
    # Se la cartella input non esiste, la creiamo per sicurezza
    os.makedirs(input_dir, exist_ok=True)
    
    # Decodifichiamo le immagini e le salviamo con il nome corretto
    for filename, b64_data in input_images.items():
        filepath = os.path.join(input_dir, filename)
        try:
            with open(filepath, "wb") as f:
                f.write(base64.b64decode(b64_data))
            print(f"Immagine di input salvata correttamente: {filename}")
        except Exception as e:
            print(f"Errore durante il salvataggio di {filename}: {e}")
    # =======================================================

    # 1. Invia il workflow a ComfyUI
    print("Inviando il prompt a ComfyUI...")
    try:
        prompt_req = requests.post(f"{COMFYUI_URL}/prompt", json={"prompt": workflow}).json()
    except Exception as e:
        return {"error": f"Errore di comunicazione: {str(e)}"}
    
    if 'prompt_id' not in prompt_req:
        return {"error": f"Errore API ComfyUI: {prompt_req}"}
        
    prompt_id = prompt_req['prompt_id']

    # 2. Attendi la fine del lavoro
    print(f"Attendendo il completamento (ID: {prompt_id})...")
    while True:
        history_req = requests.get(f"{COMFYUI_URL}/history/{prompt_id}").json()
        if prompt_id in history_req:
            history = history_req[prompt_id]
            break
        time.sleep(1)

    # 3. Estrai e codifica le immagini
    output_images = []
    for node_id in history['outputs']:
        node_output = history['outputs'][node_id]
        if 'images' in node_output:
            for image in node_output['images']:
                image_data = get_image(image['filename'], image['subfolder'], image['type'])
                base64_image = base64.b64encode(image_data).decode('utf-8')
                output_images.append({
                    "filename": image['filename'],
                    "image_base64": base64_image
                })

    return {"status": "success", "images": output_images}

# ==========================================
# ESECUZIONE PRINCIPALE
# ==========================================
if __name__ == "__main__":
    if not os.path.exists(COMFYUI_DIR):
        print(f"ERRORE CRITICO: La cartella {COMFYUI_DIR} non esiste.")
        print("Il Network Volume non è montato o il percorso è errato.")
    else:
        start_comfyui()
        runpod.serverless.start({"handler": handler})
