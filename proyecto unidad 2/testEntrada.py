import argparse
import sys
import re

def configurar_cache():
    parser = argparse.ArgumentParser(description="Configuración de la caché")

    parser.add_argument("-bs", type=int, help="Tamaño de bloque en palabras")
    parser.add_argument("-cs", type=int, help="Tamaño del caché en número de líneas")
    parser.add_argument("-wt", action="store_true", help="Cache Write-Through (por defecto, Write-Back)")
    parser.add_argument("-fa", action="store_true", help="Cache Fully Associative (por defecto, mapeo directo)")
    parser.add_argument("-sa", type=int, help="Cache Set-Associative (LRU política para reemplazar bloques), N es el número de sets")
    parser.add_argument("-wna", action="store_true", help="Cache Write-No-Allocate (por defecto, Write-Allocate)")
    parser.add_argument("-split", action="store_true", help="Cache separado en dos secciones para instrucciones y datos")

    args = parser.parse_args()

    # Leer el archivo.trace de la entrada estándar (stdin)
    datos_trace = sys.stdin.readlines()

    # Imprimir la configuración
    print("Configuración de la caché:")
    if args.bs:
        print(f"Tamaño de bloque: {args.bs} palabras")
    if args.cs:
        print(f"Tamaño del caché: {args.cs} líneas")
    if args.wt:
        print("Cache Write-Through")
    else:
        print("Cache Write-Back (por defecto)")
    if args.fa:
        print("Cache Fully Associative")
    if args.sa:
        print(f"Cache Set-Associative: {args.sa} sets")
    if args.wna:
        print("Cache Write-No-Allocate (por defecto, Write-Allocate)")
    if args.split:
        print("Cache separado en dos secciones para instrucciones y datos")

    # Procesar los datos del archivo.trace
    print("Datos del archivo.trace:")

    instructions = []

    for linea in datos_trace:
        #transformamos la linea a un arreglo de dos elementos, la instruccion y la dirección
        splitedLine = linea.split(" ")
        #dejamos solo la primer y segunda cadena de cada linea, ignoramos los comentarios o cualquier cosa que pueda haber despues
        newLine = [splitedLine[0],splitedLine[1]]
        #quitamos los saltos de linea en las direcciones de memoria
        newLine[1] = re.sub('\n', '', newLine[1])
        instructions.append(newLine)

    for i in instructions:
        print(i)

if __name__ == "__main__":
    configurar_cache()