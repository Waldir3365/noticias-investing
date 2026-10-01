from scrapling.fetchers import StealthyFetcher
from datetime import datetime

# Endpoint nuevo que descubriste
BASE_URL = "https://endpoints.investing.com/pd-instruments/v1/calendars/economic/events/occurrences"

def obtener_eventos_3_estrellas():
    hoy = datetime.now().strftime("%Y-%m-%d")
    
    # URL con parámetros (la misma que usaste en DevTools)
    url = f"{BASE_URL}?domain_id=1&limit=200&start_date={hoy}T00:00:00.000-04:00&end_date={hoy}T23:59:59.999-04:00&country_ids=5&importance=high"
    
    try:
        # StealthyFetcher abre un Chromium real y resuelve Cloudflare
        response = StealthyFetcher.fetch(
            url,
            headless=True,
            solve_cloudflare=True,  # <-- ESTO ES LA CLAVE
            timeout=60000
        )
        
        print(f"HTTP Code: {response.status}")
        print(f"Tamaño respuesta: {len(response.text)} bytes")
        
        if response.status != 200:
            print(f"Error: {response.text[:500]}")
            return []
        
        # Parsear el JSON directamente
        import json
        data = json.loads(response.text)
        events = data.get("events", [])
        occurrences = data.get("occurrences", [])
        
        event_map = {e["event_id"]: e for e in events}
        eventos_finales = []
        
        for occ in occurrences:
            ev_id = occ["event_id"]
            if ev_id in event_map:
                ev = event_map[ev_id]
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
