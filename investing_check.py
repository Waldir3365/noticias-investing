from scrapling.fetchers import StealthyFetcher
from datetime import datetime
from zoneinfo import ZoneInfo
import json

# Endpoint nuevo descubierto en DevTools
BASE_URL = "https://endpoints.investing.com/pd-instruments/v1/calendars/economic/events/occurrences"


def obtener_eventos_3_estrellas():
    hoy = datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d")

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

        contenido = ""
        if response.text:
            contenido = response.text
        elif response.body:
            try:
                contenido = response.body.decode("utf-8")
            except Exception:
                contenido = str(response.body)

        if not contenido:
            print("El contenido está vacío.")
            return []

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
                    hora_str = occ.get("occurrence_time", "")
                    hora_ny = ""
                    if hora_str:
                        try:
                            hora_utc = datetime.fromisoformat(hora_str.replace("Z", "+00:00"))
                            hora_ny = hora_utc.astimezone(ZoneInfo("America/New_York")).strftime("%H:%M")
                        except Exception:
                            hora_ny = hora_str

                    eventos_finales.append({
                        "hora": hora_ny,
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
