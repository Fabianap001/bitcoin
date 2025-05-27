import schedule
import time
import os

def ejecutar_script():
    print("⏱ Ejecutando bitcoin_api.py...")
    os.system("python bitcoin_api.py")

# Ejecutar cada minuto
schedule.every(1).minutes.do(ejecutar_script)

print("🔁 Iniciando ejecución automática cada minuto...")
while True:
    schedule.run_pending()
    time.sleep(1)