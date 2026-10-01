import requests
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://www.investing.com/economic-calendar/Service/getCalendarFilteredData"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.investing.com/economic-calendar/",
    "Content-Type": "application/x-www-form-urlencoded",
}

def obtener_eventos_3_estrellas():
    hoy = datetime.now().strftime("%Y-%m-%d")
    
    payload = {
        "country[]": "5",
        "importance[]": "3",
        "dateFrom": hoy,
        "dateTo": hoy,
        "timeZone": "8",
        "timeFilter": "timeRemain",
        "currentTab": "custom",
        "limit_from": "0",
    }
    
    try:
        response = requests.post(URL, headers=HEADERS, data=payload, timeout=30)
        print(f"HTTP Code: {response.status_code}")
        print(f"Tamaño respuesta: {len(response.text)} bytes")
        
        if response.status_code != 200:
            print(f"Error: {response.text[:500]}")
            return []
        
        soup = BeautifulSoup(response.text, "lxml")
        
        eventos = []
        for fila in soup.select("tr.js-event-item"):
            try:
                hora = fila.select_one(".first.left.time")
                nombre = fila.select_one(".left.event")
                pais = fila.select_one(".left.flagCur")
                estrellas = fila.select(".grayFullBullishIcon")
                
                if nombre and len(estrellas) == 3:
                    eventos.append({
                        "hora": hora.get_text(strip=True) if hora else "",
                        "pais": pais.get_text(strip=True) if pais else "",
                        "evento": nombre.get_text(strip=True),
                    })
            except Exception:
                continue
        
        return eventos
        
    except Exception as e:
        print(f"ERROR: {e}")
        return []

if __name__ == "__main__":
    print("Consultando Investing.com...")
    eventos = obtener_eventos_3_estrellas()
    
    if not eventos:
        print("No se encontraron eventos de 3 estrellas para hoy.")
    else:
        print(f"\nEventos de 3 estrellas encontrados: {len(eventos)}\n")
        for ev in eventos:
            print(f"  {ev['hora']} | {ev['pais']} | {ev['evento']}")
