# Carry lookahead adder

## Describir como funciona
La principal caracteristica del carry lookahead adder **(CLA)** es que permite obtener el carry de cualquier suma desde el momento incial, sin necesidad de esperar a que termine la suma anterior
a continuación se puede ver la tabla de verdad que relaciona las entradas y los carries.
| a | b | Cin | Cout |
| - | - | ---- | ----- |
| 0|0|0|0|
| 0|0|1|0|
| 0|1|0|0|
| 0|1|1|1|
| 1|0|0|0|
| 1|0|1|1|
| 1|1|0|1|
| 1|1|1|1|

*a y b son los números a sumar, Cin es el carry de entrada y Cout el carry de salida.*

Analizando la tabla sabremos que el carry out será uno cuando: **(A and B)** o **(A xor B) and Cin** 
o expresado de otra forma:

**Cout = (A * B) + (A⊕B) * Cin**

Podemos diferenciar partes de esta expresión, donde la sección (A*B) se conocerá como *"carry generator"* y la sección
(A⊕B) como *"carry propagator"*. Carry generator no tiene dependencia de Cin solo de los valores de entrada a y b





## Porque es más rápido que ripple adder

## Cuales son sus desventajas