from scrapling.fetchers import StealthyFetcher
from datetime import datetime
import json

# Endpoint nuevo descubierto en DevTools
BASE_URL = "https://endpoints.investing.com/pd-instruments/v1/calendars/economic/events/occurrences"


def obtener_eventos_3_estrellas():
    from zoneinfo import ZoneInfo
    hoy = datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d")

    # URL con parámetros (igual que en DevTools)
    url = (
        f"{BASE_URL}"
        f"?domain_id=1"
        f"&limit=200"
        f"&start_date={hoy}T00:00:00.000-04:00"
        f"&end_date={hoy}T23:59:59.999-04:00"
        f"&country_ids=5"
        f"&importance=high"
    )

    try:
        response = StealthyFetcher.fetch(
            url,
            headless=True,
            solve_cloudflare=True,
            timeout=60000
        )

        print(f"HTTP Code: {response.status}")
        print(f"Tamaño response.text: {len(response.text) if response.text else 0} bytes")
        print(f"Tamaño response.body: {len(response.body) if response.body else 0} bytes")

        # Intentar obtener el contenido de distintas formas
        contenido = ""
        if response.text:
            contenido = response.text
        elif response.body:
            try:
                contenido = response.body.decode("utf-8")
            except Exception:
                contenido = str(response.body)

        if not contenido:
            print("El contenido está vacío. Headers de la respuesta:")
            print(response.headers)
            return []

        print("Primeros 300 caracteres del contenido:")
        print(contenido[:300])

        data = json.loads(contenido)
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
