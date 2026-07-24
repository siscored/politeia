# -*- coding: utf-8 -*-
"""
Descarga los CSV de estadisticas historicas de la Junta Electoral PBA
(elecciones provinciales/municipales, nivel MUNICIPIO) para Pilar y San Fernando.

Uso:
    pip install requests
    python descarga_junta_pba.py

Genera: datos-electorales/raw/junta_pba/<municipio>/<año>.csv
        datos-electorales/raw/junta_pba/log_junta.csv
"""

import csv
import time
from pathlib import Path

import requests

URL = "https://www.juntaelectoral.gba.gov.ar/distritoEstadisticasHistoricasAcsv.php"

DISTRITOS = {"089": "pilar", "105": "san_fernando"}
ANIOS = [2003, 2005, 2007, 2009, 2011, 2013, 2015, 2017, 2019, 2021, 2023, 2025]

OUT = Path("datos-electorales") / "raw" / "junta_pba"


def descargar(anio, did):
    """La pagina envia un form (anio, did) al endpoint Acsv. Probamos POST y GET."""
    data = {"anio": str(anio), "did": did}
    for metodo in ("post", "get"):
        try:
            r = getattr(requests, metodo)(
                URL, **({"data": data} if metodo == "post" else {"params": data}),
                timeout=60,
            )
        except requests.RequestException as e:
            return f"ERROR:{e}"
        if r.status_code == 200 and r.text.strip() and "<html" not in r.text[:200].lower():
            return r.text
    return None


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    log_path = OUT / "log_junta.csv"
    with open(log_path, "w", newline="", encoding="utf-8") as flog:
        log = csv.writer(flog)
        log.writerow(["año", "municipio", "estado", "filas"])
        for did, municipio in DISTRITOS.items():
            destino = OUT / municipio
            destino.mkdir(exist_ok=True)
            for anio in ANIOS:
                archivo = destino / f"{anio}.csv"
                if archivo.exists():
                    print(f"ya existe   {municipio}/{anio}.csv")
                    continue
                texto = descargar(anio, did)
                time.sleep(1)
                if texto is None:
                    log.writerow([anio, municipio, "sin_datos", 0])
                    print(f"sin datos   {municipio}/{anio}")
                    continue
                if texto.startswith("ERROR:"):
                    log.writerow([anio, municipio, "error", 0])
                    print(f"ERROR       {municipio}/{anio} -> {texto[:120]}")
                    continue
                archivo.write_text(texto, encoding="utf-8")
                filas = texto.count("\n")
                log.writerow([anio, municipio, "ok", filas])
                print(f"descargado  {municipio}/{anio}.csv ({filas} filas)")
    print(f"\nListo. Log en {log_path}")


if __name__ == "__main__":
    main()
