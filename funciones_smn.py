import json
import os
from datetime import datetime

meses = {'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04', 'mayo': '05', 'junio': '06', 'julio': '07',
        'agosto': '08', 'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'}


def detectar_encoding(ruta_archivo: str) -> str:
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as texto:
            texto.read()
        return 'utf-8'
    except UnicodeEncodeError:
        return 'latin-1'


def parsear_fecha_y_hora(fecha_str: str, hora_str: str) -> datetime:

    partes_fecha = fecha_str.split('-')

    dia = int(partes_fecha[0])
    mes = int(meses[partes_fecha[1].lower()])
    anio = int(partes_fecha[2])

    partes_hora = hora_str.split(':')


    hora = int(partes_hora[0])
    minuto = int(partes_hora[1])
    return datetime(anio, mes, dia, hora, minuto)


def separar_viento(campo_viento: str) -> tuple:
    """Convierte un campo de viento como 'Norte  3' en (direccion, velocidad).
    Contempla el caso 'Calma' (sin velocidad numérica)."""

    campo_viento = campo_viento.strip()
    if campo_viento.lower() == 'calma':
        return ('Calma', 0)
    
    partes = campo_viento.rsplit(None, 1)

    direccion = partes[0]
    velocidad = int(partes[1])
    return (direccion, velocidad)


def leer_observaciones(ruta: str) -> dict:
    """Lee el archivo de observaciones del SMN y devuelve un diccionario
    {ciudad: datos}, con los nombres de ciudad limpios y el campo de viento
    ya separado en dirección y velocidad."""

    observaciones = {}
    
    with open(ruta, 'r', encoding='latin-1') as texto:
        for linea in texto:
            linea = linea.strip()
            if not linea:
                continue

            datos = linea.split(';')
            if len(datos) != 10:
                continue

            ciudad = datos[0].strip()

            texto_st = datos[6].strip()
            if texto_st.lower() == 'no se calcula':
                sens_termica = None
            else:
                sens_termica = float(texto_st)

            direccion, velocidad = separar_viento(datos[8])

            txt_presion = datos[9].strip(' /')

            fecha = datos[1].strip()
            hora = datos[2].strip()

            observaciones[ciudad] = {
                'fecha_y_hora': parsear_fecha_y_hora(fecha, hora),
                'condicion': datos[3].strip(),
                'visibilidad': datos[4].strip(),
                'temperatura': float(datos[5].strip()),
                'sens_termica': sens_termica,
                'humedad': float(datos[7].strip()),
                'dir_viento': direccion,
                'vel_viento': velocidad,
                'presion': float(txt_presion),
            }
    return observaciones
   

def cantidad_ciudades(observaciones: dict) -> int:
    """Devuelve la cantidad total de ciudades leídas."""
    
    return len(observaciones)


def cantidad_ciudades_completas(observaciones: dict) -> int:
    """Devuelve la cantidad de ciudades sin ningún dato faltante."""

    ciud_comp = 0
    for datos_ciudad in observaciones.values():
        if None not in datos_ciudad.values():
            ciud_comp += 1

    return ciud_comp


def top_n_ciudades(observaciones: dict, campo: str, n: int, descendente: bool = True) -> list:
    """Devuelve las n (por parámetro) ciudades ordenadas según 'campo', de mayor a menor
    (o al revés si descendente=False), en una lista. Reutilizable tanto para temperatura
    como para viento."""

    vale = []
    for ciudad, datos in observaciones.items():
        valor = datos.get(campo)
        if valor is not None and isinstance(valor, (int, float)):
            vale.append(ciudad)

    def valor(ciudad):
        return observaciones[ciudad][campo]
    
    ciud_ord = sorted(vale, key=valor, reverse=descendente)
    return ciud_ord[:n]


def horarios_reportados(observaciones: dict) -> list:
    """devuelve una lista de los horarios a los que las estaciones 
    reportaron en la observación dada. 
    La lista tendrá horas en el formato string "HH:MM",
    será sin repetir y ordenadas de menor a mayor"""

    horarios = []
    for datos in observaciones.values():
        fyh = datos.get('fecha_y_hora')
        if fyh is not None:
            hora = fyh.strftime('%H:%M')
            if hora not in horarios:
                horarios.append(hora)
    return sorted(horarios)


def datos_faltantes_por_campo(observaciones: dict) -> dict:
    faltantes = {}

    for datos in observaciones.values():
        for campo, valor in datos.items():
            if campo not in faltantes:
                faltantes[campo] = 0
            if valor is None:
                faltantes[campo] += 1
    
    return faltantes


def guradado_json(observaciones: dict, ruta_salida: str) -> None:
    
    datos_json = {}

    for ciudad, datos in observaciones.items():
        datos_copia = datos.copy()
        if isinstance(datos_copia['fecha_y_hora'], datetime):
            datos_copia['fecha_y_hora'] = datos_copia['fecha_y_hora'].isoformat(timespec='minutes')
        datos_json[ciudad] = datos_copia

    directorio = os.path.dirname(ruta_salida)
    if directorio and not os.path.exists(directorio):
        print(f"El directorio '{directorio}' no existe, creándolo...")
        os.makedirs(directorio, exist_ok=True)

    with open(ruta_salida, 'w', encoding = 'utf-8') as t:
        json.dump(datos_json, t, ensure_ascii = False, indent = 4)


def contar_archivos(directorio: str, extension: str) -> int:
    if not os.path.exists(directorio):
        return 0
    return len([t for t in os.listdir(directorio) if t.endswith(extension)])