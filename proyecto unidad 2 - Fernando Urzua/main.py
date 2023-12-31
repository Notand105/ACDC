import argparse
import sys
import re
import math 

#Configuración
blockSize = 2
cacheSize = 2
offset = 0
line = 0
tag = 0
writeThrough = False
fullyAssociative = False
setAssociative = 0
noAllocate = False
splitCache = False

historialParaFA = []

#estadisticas
missesDatos = 0
hitsDatos = 0
missesInstrucciones = 0
hitsInstrucciones = 0
lineas_a_analizar = 0
wordsCopiados = 0
wordsEscritos = [0,0]

def convertir_a_binario(cadena):
    aDecimal = int(cadena, 16)
    binario = bin(aDecimal)[2:]
    if len(binario) < 32:
        binario = "0" * (32 - len(binario)) + binario 
    return binario

def actualizar_cache_fa(cache, index):
    #recibimos una posicion del cache y la mandamos al final, de esta manera el cache[0] siempre sera el LRU
    pos = cache.pop(index)
    cache.append(pos)
    return cache
def configurar_cache():
    
    global blockSize,cacheSize,writeThrough, fullyAssociative,setAssociative ,noAllocate ,splitCache 

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
        blockSize = args.bs
        print(f"Tamaño de bloque: {blockSize} palabras")
    if args.cs:
        cacheSize = args.cs
        print(f"Tamaño del caché: {cacheSize} líneas")
    if args.wt:
        writeThrough = True
        print("Cache Write-Through")
    else:
        print("Cache Write-Back (por defecto)")
    if args.fa:
        fullyAssociative = True
        print("Cache Fully Associative")
    if args.sa:
        setAssociative = args.sa
        print(f"Cache Set-Associative: {args.sa} sets (no implementado), se usará mapeo directo")
    if args.wna:
        noAllocate = True
        print("Cache Write-No-Allocate (por defecto, Write-Allocate)")
    if args.split:
        splitCache = True
        print("Cache separado en dos secciones para instrucciones y datos (no implementado)")

    if (setAssociative and fullyAssociative):
        setAssociative = False
        fullyAssociative = False

    # Procesar los datos del archivo.trace

    instructions = []

    for linea in datos_trace:
        #transformamos la linea a un arreglo de dos elementos, la instruccion y la dirección
        splitedLine = linea.split(" ")
        #dejamos solo la primer y segunda cadena de cada linea, ignoramos los comentarios o cualquier cosa que pueda haber despues
        newLine = [splitedLine[0],splitedLine[1]]
        #quitamos los saltos de linea en las direcciones de memoria
        newLine[1] = re.sub('\n', '', newLine[1])
        #llenamos new line[1] con ceros si este es menor a 8
        if (len(newLine[1])<8):
            ceros = 8 - len(newLine[1])
            newLine[1] = "0"*ceros + newLine[1]
        #convertimos la direccion a binario
        newLine[1] = convertir_a_binario(newLine[1])
        instructions.append(newLine)

    return instructions

#cuando hay mapeo directo necesitamos considerar un line, sin embargo cuando es fully associative solo necesitamos tag y offset
def dividir_entrada():
    global offset, line, tag, blockSize, cacheSize
    offset = int(math.log(blockSize, 2))
    line = int(math.log(cacheSize, 2))
    #asumimos todas las entradas de 32 bits
    tag = 32 - (offset + line )

def dividir_entrada_fa():
    global offset, tag, blockSize
    offset = int(math.log(blockSize, 2))
    #asumimos todas las entradas de 32 bits
    tag = 32 - offset 

def creaCache():
    #tenemos que crear un cache de cacheSize lineas
    global cacheSize 
    cache = []
    for i in range(cacheSize):
        cache.append('empty')
    return cache

def mapeo_directo(cache, instruccion):
    global offset, line, tag
    ##addr[0] es el tag , addr[1] es la linea en la que guardarla
    addr = format_instructions(instruccion[1])
    lineInCache = int(addr[1],2)
    if (instruccion[0] == '0'):
        #print("leer dato")
        cache = leerDatoMD(cache, lineInCache, addr[0])
    elif(instruccion[0]=='1'):
        #print('escribir dato')
        cache = escribirDato(cache, lineInCache, addr[0])
    elif (instruccion[0])=='2':
        #print('leer instruccion')
        cache = leerInstruccionMD(cache, lineInCache, addr[0])
    return cache

def full_associative(cache, instruccion):
    global offet,tag
    addr = format_instructions_fa(instruccion[1])
    if(instruccion[0]=='0'):
        cache = leerDatoFA(cache, addr)
    elif(instruccion[0]=='1'):
        cache = escribirDatoFA(cache, addr)
    elif(instruccion[0]=='2'):
        cache = leerInstruccionFA(cache, addr)
    return cache


def leerDatoMD(cache, line, tag):
    global missesDatos, hitsDatos, wordsCopiados, blockSize, wordsEscritos
    if (cache[line] == 'empty'):
       # print("miss por no existir, lo traemos de memoria")
        cache[line] = tag
        missesDatos += 1
        wordsCopiados += blockSize 
    elif(cache[line] != tag  ):
       # print("miss por existir otro, reemplazamos por el nuevo trayendolo desde memoria")
        cache[line] = tag
        missesDatos += 1
        wordsCopiados += blockSize 
        
    elif (cache[line] == tag):
       # print("hit")
        hitsDatos += 1

    return cache

def leerDatoFA(cache,tag):
    global missesDatos, hitsDatos, wordsCopiados, blockSize, wordsEscritos
    #buscamos en todo el cache si existe el tag
    for index,linea in enumerate(cache):
        if (linea == tag):
            #existe asi que le asignamos un hit 
            hitsDatos += 1
            cache = actualizar_cache_fa(cache, index)
            return cache
    #si llegamos aqui es porque no existe entonces buscamos si hay un espacio libre y lo agregamos ahi ademas sabemos que es un miss
    missesDatos += 1 
    wordsCopiados += blockSize
    for linea in cache:
        if (linea == 'empty'):
            cache[index]= tag
            cache = actualizar_cache_fa(cache, index)
            return cache
    #finalmente si no está vacio y ademas el cache está lleno 
    cache[0] = tag
    cache = actualizar_cache_fa(cache,0) 
    return cache

def leerInstruccionMD(cache, line, tag):
    global missesInstrucciones, hitsInstrucciones, wordsCopiados, blockSize, wordsEscritos
    if (cache[line] == 'empty'):
        #print("miss por no existir, lo traemos de memoria")
        #agrergar logica para escribir
        cache[line] = tag
        missesInstrucciones += 1
        wordsCopiados += blockSize 
    elif(cache[line] != tag  ):
        #print("miss por existir otro, reemplazamos por el nuevo trayendolo desde memoria")
        #agrergar logica para escribir
        cache[line] = tag
        missesInstrucciones += 1
        wordsCopiados += blockSize 
    elif (cache[line] == tag):
        #print("hit")
        hitsInstrucciones += 1

    return cache

def leerInstruccionFA(cache,tag):
    global missesInstrucciones, hitsInstrucciones, wordsCopiados, blockSize, wordsEscritos
    #buscamos en todo el cache si existe el tag
    for index,linea in enumerate(cache):
        if (linea == tag):
            #existe asi que le asignamos un hit 
            hitsInstrucciones += 1
            cache = actualizar_cache_fa(cache, index)
            return cache
    #si llegamos aqui es porque no existe entonces buscamos si hay un espacio libre y lo agregamos ahi ademas sabemos que es un miss
    missesInstrucciones += 1 
    wordsCopiados += blockSize
    for linea in cache:
        if (linea == 'empty'):
            cache[index]= tag
            cache = actualizar_cache_fa(cache, index)
            return cache
    #finalmente si no está vacio y ademas el cache está lleno 
    cache[0] = tag
    cache = actualizar_cache_fa(cache,0) 
    return cache


def escribirDato(cache,line,tag):
    global writeThrough, noAllocate,wordsEscritos 
    #si es write through accedemos a cache y memoria al mismo tiempo
    if (writeThrough):
        #si es writeTrough no tiene sentido el usar noAllocate
        #agregar a al inidice 0 implica que se cargo a memoria
        wordsEscritos[0] += 1
        cache[line] = tag
    else:
        #si tenia un dirty bit desde antes entonces escribimos en memoria antes de actualizar el tag
        #print(len(cache[line])>len(tag))
        if(len(cache[line]) > len(tag) ):
            # si es not notAllocate o simplemente allocate guardamos en memoria y en cache, si es not allocate guardamos en memoria pero no en cache
            if(not noAllocate):
                cache[line] = tag
            wordsEscritos[0] += 1
        else:
            #escribimos solo a cache pero la posicion la marcaremos con un dirty bit
            if (not noAllocate):
                cache[line] = '1' + tag
            #como solo accedimos a cache 
            if (noAllocate):
                wordsEscritos[0] += 1
            else:    
                wordsEscritos[1] += 1
    return cache

def escribirDatoFA(cache,tag):
    global writeThrough, noAllocate,wordsEscritos 
    #si es write through accedemos a cache y memoria al mismo tiempo
    if (writeThrough):
        #si es writeTrough no tiene sentido el usar noAllocate
        #agregar a al inidice 0 implica que se cargo a memoria
        wordsEscritos[0] += 1
        for index,linea in enumerate(cache):
            #si hay una linea vacia escribimos ahi
            if(linea == 'empty'):
                cache[index]= tag
                cache = actualizar_cache_fa(cache, index)
                return cache
        #si no hay linea vacia reemplazamos el menos usado
        cache[0] = tag
        cache = actualizar_cache_fa(cache,0)
        return cache

    else:
        #si tenia un dirty bit desde antes entonces escribimos en memoria antes de actualizar el tag
        #print(len(cache[line])>len(tag))
        if (noAllocate): # si es no allocate vamos directamente a memoria no nos preocupamos por guardar
            wordsEscritos[0] += 1
            return cache
        else: 
            for index,linea in enumerate(cache):
            #si hay una linea vacia escribimos ahi, pero no pasaremos a memoria aun marcamos con dirty bit
                if(linea == 'empty'):
                    cache[index]= '1' + tag
                    cache = actualizar_cache_fa(cache, index)
                    wordsEscritos[1] += 1
                    return cache
            #si no hay linea vacia reemplazamos el menos usado considerando que pueda tener un dirty bit
            if (len(cache[0])>len(tag)):
                #llevamos el tag a memoria y despues reemplazamos
                wordsEscritos[0] += 1
                cache[0] = tag
                cache =  actualizar_cache_fa(cache, 0)
                return cache
            else :
                wordsEscritos[1] += 1
                cache[0] = '1' + tag
                cache =  actualizar_cache_fa(cache, 0)
                return cache



def format_instructions(instruction):
    global offset,tag,line

    itag = instruction[:tag] 
    iline = instruction[tag:tag + line]
    return [itag,iline] 

def format_instructions_fa(instruction):
    global offset,tag

    itag = instruction[:tag] 
    return itag 


def print_stats():
    global missesDatos, hitsDatos, missesInstrucciones, hitsInstrucciones, blockSize, writeThrough, wordsEscritos
    print("referencias a Instrucciones: ", missesInstrucciones+ hitsInstrucciones)
    print("referencias a datos: ", missesDatos + hitsDatos)
    print("misses datos: ", missesDatos)
    print("misses Instrucciones: ", missesInstrucciones)
    print("palabras copiadas desde memoria hasta caché: ", wordsCopiados)

    if (not writeThrough):
        print("veces que se añadido solo a cache: ", wordsEscritos[1], ", veces que se añadio a memoria principal: ", wordsEscritos[0] )

    print("palabras escritas desde caché a memoria: ", (wordsEscritos[0] + wordsEscritos[1])*blockSize)
    tiempo = (hitsDatos * 5) + (hitsInstrucciones * 5) + (wordsCopiados * 100) + (((wordsEscritos[0] * 100) + (wordsEscritos[1]*5))*blockSize)
    print("tiempo: ", tiempo, " nanosegundos")
    if(tiempo > 1000000):
        print("tiempo: ", tiempo / math.pow(10,9), " segundos")



if __name__ == "__main__":
    instructions = configurar_cache()
    if(fullyAssociative ):
        print("\n")
        print("Fully asociative")
        print("\n")
        dividir_entrada_fa()
        cache = creaCache()
        for i in instructions:
            cache = full_associative(cache, i)
    else:
        print("\n")
        print("Mapeo Directo")
        print("\n")
        dividir_entrada() 
        cache = creaCache()
        for i in instructions:
            cache = mapeo_directo(cache, i)
    print_stats() 
    