import json
import os
import sys
from funciones_smn import(
    cantidad_ciudades,
    cantidad_ciudades_completas,
    contar_archivos,
    datos_faltantes_por_campo,
    detectar_encoding,
    guardar_json_smn,
    leer_observaciones,
)


def main():
    argumentos = sys.argv[1:]
    if len(argumentos) > 1:
        print('Se ingresó más de un parámetro. Ingresar una única ruta')
        sys.exit(1)
    if len(argumentos) == 0:
        txt_count = contar_archivos('datos', '.txt')
        json_count = contar_archivos('obs_json', '.json')
        print('No se encontró ningún archivo de entrada')
        print(f"Archivos .txt en 'datos/': {txt_count} ")
        print(f"Archivos .json en 'obs_json/': {json_count} ")
        sys.exit(0)

    ruta_archivo = argumentos[0]
    
    if ruta_archivo.endswith('.txt'):
        print('Archivo del SMN, detectando codificación...')
        try:
            encoding = detectar_encoding(ruta_archivo)
        except FileNotFoundError:
            print(f"Error: el archivo '{ruta_archivo}' no existe.")
            sys.exit(1)
    
        print(f'Codificación detectada: {encoding}. Leyendo datos...')
        observaciones = leer_observaciones(ruta_archivo, encoding)

        nombre_base = os.path.basename(ruta_archivo)
        nombre_json = os.path.splitext(nombre_base)[0] + '.json'
        ruta_json = os.path.join('obs_json', nombre_json)

        print('Archivo del SMN, convirtiendo a json...')
        guardar_json_smn(observaciones, ruta_json)

        total = cantidad_ciudades(observaciones)
        completas = cantidad_ciudades_completas(observaciones)
        print(f'Cantidad de ciudades que contiene el archivo: {total}')
        print(f'Cantidad de ciudades informadas: {completas}')

        print('\nDATOS FALTANTES POR CAMPO Y ESTACIONES:')
        faltantes = datos_faltantes_por_campo(observaciones)
        for campo, estaciones in faltantes.items():
            cantidad = len(estaciones)
            nombres_estaciones = ', '.join(estaciones) if estaciones else 'Ninguna'
            print(f'- {campo}: {cantidad} faltantes -> Estaciones: {nombres_estaciones}')

    elif ruta_archivo.endswith('.json'):
        if not os.path.exists(ruta_archivo):
            print(f"El archivo '{ruta_archivo}' no existe.")
            sys.exit(1)

        print(f"Leyendo archivo JSON '{ruta_archivo}'...")
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as t:
                observaciones = json.load(t)

            total = cantidad_ciudades(observaciones)
            completas = cantidad_ciudades_completas(observaciones)
            print(f'Cantidad de ciudades que contiene el archivo: {total}')
            print(f'Cantidad de ciudades informadas: {completas}')
        
        except Exception as e:
            print(f'Error al leer el archivo JSON: {e}')
            sys.exit(1)
    
    else:
        print('Error: Formato de archivo no soportado. Ingrese un archivo .txt o .json.')
        sys.exit(1)

if __name__ == '__main__':
    main()