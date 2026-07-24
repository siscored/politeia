# -*- coding: utf-8 -*-
"""
Descarga masiva de resultados electorales (DINE - resultados.mininterior.gob.ar)
para Pilar y San Fernando, 2011-2025, todos los cargos y tipos de eleccion.

Uso:
    pip install requests
    python descarga_masiva_dine.py

Genera:
    datos-electorales/raw/<municipio>/<año>_<eleccion>_<cargo>.csv
    datos-electorales/log_descarga.csv  (registro de que se bajo y que no existia)
"""

import csv
import io
import time
from pathlib import Path

import requests

BASE = "https://resultados.mininterior.gob.ar/api/resultado/totalizadocsv"

SECCIONES = {
    89: "pilar",
    105: "san_fernando",
}

ANIOS = [2011, 2013, 2015, 2017, 2019, 2021, 2023, 2025]

# idEleccion segun la URL del sitio (/resultados/{año}/{idEleccion}/...):
# 2 = Generales (verificado con la descarga manual). PASO y Segunda vuelta
# se prueban con los demas ids; si no existen para ese año la API devuelve vacio.
TIPOS_ELECCION = {
    1: "paso",
    2: "generales",
    3: "segunda_vuelta",
}

# idCargo: 1=Presidente (verificado). El resto se prueba por barrido;
# los que no apliquen para ese año/eleccion vuelven vacios y se registran en el log.
CARGOS = {
    1: "presidente",
    2: "senadores_nac",
    3: "diputados_nac",
    4: "gobernador",
    5: "senadores_prov",
    6: "diputados_prov",
    7: "intendente",
    8: "mercosur_nac",
    9: "mercosur_reg",
    10: "concejales",
}

DISTRITO_BSAS = 2
PAUSA_SEGUNDOS = 1.0  # ser amable con el servidor
OUT = Path("datos-electorales")


def descargar(anio, id_eleccion, id_cargo, id_seccion):
    """Devuelve el texto CSV si hay datos, None si no existe esa combinacion."""
    params = {
        "año": anio,
        "recuento": "Provisorio",
        "idEleccion": id_eleccion,
        "idCargo": id_cargo,
        "idDistrito": DISTRITO_BSAS,
        "idSeccion": id_seccion,
    }
    try:
        r = requests.get(BASE, params=params, timeout=120)
    except requests.RequestException as e:
        return f"ERROR:{e}"
    if r.status_code != 200:
        return None
    texto = r.text.strip()
    # sin datos: respuesta vacia, solo encabezado, o mensaje de no disponible
    if not texto or texto.count("\n") < 1:
        return None
    if texto.startswith("mensaje") or "Resultados no disponibles" in texto:
        return None
    return texto


def limpiar_archivos_invalidos(raw):
    """Borra archivos guardados en corridas previas que solo contienen
    el mensaje 'Resultados no disponibles' de la API."""
    borrados = 0
    for archivo in raw.glob("*/*.csv"):
        with open(archivo, encoding="utf-8") as f:
            primera = f.readline().strip()
        if primera == "mensaje":
            archivo.unlink()
            borrados += 1
    if borrados:
        print(f"limpieza: {borrados} archivos invalidos borrados (se reintentaran)")


def main() -> None:
    raw = OUT / "raw" / "dine"
    raw.mkdir(parents=True, exist_ok=True)
    limpiar_archivos_invalidos(raw)
    log_path = OUT / "log_descarga.csv"

    with open(log_path, "w", newline="", encoding="utf-8") as flog:
        log = csv.writer(flog)
        log.writerow(["año", "eleccion", "cargo", "municipio", "estado", "filas", "archivo"])

        for id_seccion, municipio in SECCIONES.items():
            destino = raw / municipio
            destino.mkdir(exist_ok=True)
            for anio in ANIOS:
                for id_eleccion, eleccion in TIPOS_ELECCION.items():
                    for id_cargo, cargo in CARGOS.items():
                        nombre = f"{anio}_{eleccion}_{cargo}.csv"
                        archivo = destino / nombre
                        if archivo.exists():
                            print(f"ya existe   {municipio}/{nombre}")
                            continue

                        texto = descargar(anio, id_eleccion, id_cargo, id_seccion)
                        time.sleep(PAUSA_SEGUNDOS)

                        if texto is None:
                            log.writerow([anio, eleccion, cargo, municipio, "sin_datos", 0, ""])
                            continue
                        if texto.startswith("ERROR:"):
                            print(f"ERROR       {municipio}/{nombre} -> {texto}")
                            log.writerow([anio, eleccion, cargo, municipio, "error", 0, texto])
                            continue

                        filas = sum(1 for _ in io.StringIO(texto)) - 1
                        archivo.write_text(texto, encoding="utf-8")
                        print(f"descargado  {municipio}/{nombre}  ({filas} filas)")
                        log.writerow([anio, eleccion, cargo, municipio, "ok", filas, str(archivo)])
                        flog.flush()

    print(f"\nListo. Revisar {log_path} para el detalle.")


if __name__ == "__main__":
    main()