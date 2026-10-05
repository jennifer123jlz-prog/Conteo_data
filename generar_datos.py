#!/usr/bin/env python3
"""
generar_datos.py - Lee puntos_geocodificados.csv y genera los datos de la pagina.

Solo toma los puntos con coordenadas propias del sitio (geocod_metodo =
'sitio_original'). Escribe:
  - puntos.json   (datos limpios, para revisar o reutilizar)
  - datos.js      (mismos datos como `window.PUNTOS = [...]`, que carga index.html;
                   se usa un .js y no un fetch del .json para que la pagina tambien
                   funcione abierta directamente desde el disco)

Uso:  python generar_datos.py ruta/puntos_geocodificados.csv
"""
import csv, json, sys

ENTRADA = sys.argv[1] if len(sys.argv) > 1 else "puntos_geocodificados.csv"
GEOTECNICAS = {"Vía afectada", "Puente afectado", "Deslizamiento"}

filas = list(csv.DictReader(open(ENTRADA, encoding="utf-8-sig")))
puntos = []
for r in filas:
    if r.get("geocod_metodo") != "sitio_original":
        continue
    try:
        lat, lon = float(r["lat"]), float(r["lon"])
    except (ValueError, KeyError):
        continue
    desc = " ".join((r.get("descripcion") or "").split())
    puntos.append({
        "codigo": r["codigo"],
        "categoria": r["nombre"],
        "tipo": "geotecnico" if r["nombre"] in GEOTECNICAS else "edificacion",
        "estado": r.get("estado", ""),
        "departamento": r.get("departamento", ""),
        "municipio": r.get("municipio", ""),
        "barrio": r.get("barrio", ""),
        "direccion": " ".join((r.get("direccion") or "").split()),
        # texto de ubicacion tal como lo muestra la pagina (direccion, municipio, departamento)
        "ubicacion": " ".join((r.get("ubicacion") or "").split()),
        "descripcion": desc,
        "lat": round(lat, 7),
        "lon": round(lon, 7),
        "precision": (r.get("precision_ubicacion") or "").upper(),
    })

# orden estable: municipio, luego numero de codigo
def num(c):
    try: return int(c.split("-")[1])
    except Exception: return 0
# primero los municipios de mayor interes, en este orden; luego el resto por nombre
PRIORIDAD = ["Cali", "Pereira", "Manizales", "Buenaventura", "Armenia", "Quibdó"]
def orden(p):
    m = p["municipio"]
    return (PRIORIDAD.index(m) if m in PRIORIDAD else len(PRIORIDAD), m, num(p["codigo"]))
puntos.sort(key=orden)
# numero correlativo 1..N: es lo que la persona usa para su rango
for i, p in enumerate(puntos, 1):
    p["n"] = i

json.dump(puntos, open("puntos.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
js = json.dumps(puntos, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
open("datos.js", "w", encoding="utf-8").write("window.PUNTOS = " + js + ";\n")
print(f"{len(puntos)} puntos escritos en puntos.json y datos.js")
