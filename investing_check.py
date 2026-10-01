from curl_cffi import requests
from datetime import datetime

# Endpoint nuevo que descubriste en DevTools
BASE_URL = "https://endpoints.investing.com/pd-instruments/v1/calendars/economic/events/occurrences"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://www.investing.com/economic-calendar/",
    "Origin": "https://www.investing.com",
}

def obtener_eventos_3_estrellas():
    hoy = datetime.now().strftime("%Y-%m-%d")
    
    # Parámetros basados en tu URL descubierta
    params = {
        "domain_id": "1",
        "limit": "200",
        "start_date": f"{hoy}T00:00:00.000-04:00",
        "end_date": f"{hoy}T23:59:59.999-04:00",
        "country_ids": "5",
        "importance": "high",
    }
    
    try:
        response = requests.get(
            BASE_URL,
            params=params,
            headers=HEADERS,
            impersonate="chrome124", # Versión más reciente
            timeout=30
        )
        print(f"HTTP Code: {response.status_code}")
        print(f"Tamaño respuesta: {len(response.text)} bytes")
        
        if response.status_code != 200:
            print(f"Error: {response.text[:500]}")
            return []
        
        # Parsear JSON
        data = response.json()
        events = data.get("events", [])
        occurrences = data.get("occurrences", [])
        
        # Crear un diccionario de eventos por ID para cruzar
        event_map = {e["event_id"]: e for e in events}
        
        eventos_finales = []
        for occ in occurrences:
            ev_id = occ["event_id"]
            if ev_id in event_map:
                ev = event_map[ev_id]
                # Solo eventos de alta importancia
                if ev.get("importance") == "high":
                    eventos_finales.append({
                        "hora": occ.get("occurrence_time", ""),
                        "pais": ev.get("currency", ""),
                        "evento": ev.get("short_name", "Sin nombre"),
                    })
        
        return eventos_finales
        
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
