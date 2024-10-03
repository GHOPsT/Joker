# Informe de Refactorización y Reporte SonarLint

Este documento detalla las refactorizaciones realizadas en dos funciones de descarga paralela y secuencial, respectivamente, para mejorar la calidad del código en cuanto a mantenibilidad, modularidad y manejo de errores, así como el análisis estático utilizando SonarLint para detectar problemas críticos.

---

## Refactorización 1: Código para Descarga Paralela

### Violaciones y Refactorizaciones

#### 1. Violación: Alta Complejidad Ciclomática
   - **Descripción**: La función `descarga_paralela` contenía múltiples responsabilidades, lo que incrementaba la complejidad ciclomatica y dificultaba su mantenimiento.
   - **Corrección/Refactorización**: Se modularizó el código dividiendo las tareas en subfunciones como `calcular_rangos`, `gestionar_descargas`, y `reconstruir_archivo`, mejorando la legibilidad.
   - **Fragmento Refactorizado**:
     ```python
     def calcular_rangos(size, fragmentos):
         tamF = size // fragmentos
         ranges = [[i, i + tamF - 1] for i in range(0, size, tamF)]
         ranges[-1][-1] = size
         return ranges

     def gestionar_descargas(url, ranges, frag, semaphore):
         threads = [threading.Thread(target=descargar, args=(url, i, r, frag, semaphore)) for i, r in enumerate(ranges)]
         for thread in threads:
             thread.start()
         for thread in threads:
             thread.join()

     def reconstruir_archivo(frag, nombre, directorio):
         ruta_completa = os.path.join(directorio, nombre)
         with open(ruta_completa, 'wb') as file:
             for i, data in enumerate(frag):
                 if data is None or data == '#Error':
                     print(f'El fragmento {i} no se pudo descargar. No se puede reconstruir el archivo.')
                     return False
                 file.write(data)
         print(f'Archivo descargado y reconstruido con éxito en el directorio: {ruta_completa}')
         return True
     ```

#### 2. Violación: Acoplamiento Elevado
   - **Descripción**: Variables como `frag` eran manipuladas en múltiples funciones, lo que creaba un alto acoplamiento.
   - **Corrección/Refactorización**: Se utilizó un semáforo (`semaphore`) para controlar el acceso concurrente a la lista compartida `frag`, reduciendo el acoplamiento.
   - **Fragmento Refactorizado**:
     ```python
     def descargar(url, orden, rango, frag, semaphore, retry_limit=3):
         try:
             print('Obteniendo fragmento {}. Descargando desde byte {} hasta byte {}.'.format(orden, *rango))
             req = urllib.request.Request(url)
             req.add_header('Range', 'bytes={}-{}'.format(*rango))
             for _ in range(retry_limit):
                 try:
                     data = urllib.request.urlopen(req).read()
                     if data:
                         with semaphore:
                             frag[orden] = data
                         print('Fragmento {} descargado correctamente. Obtenidos {} bytes.'.format(orden, len(data)))
                         break
                 except Exception as e:
                     print(f'Error al descargar fragmento {orden}: {e}')
             else:
                 with semaphore:
                     frag[orden] = '#Error'
         except Exception as e:
             print(f'Error al descargar fragmento {orden}: {e}')
     ```

#### 3. Violación: Código Repetido (DRY)
   - **Descripción**: El cálculo de rangos y el manejo de fragmentos se repetía varias veces en el código.
   - **Corrección/Refactorización**: Se consolidaron las operaciones de cálculo de rangos en una única función reutilizable.
   - **Fragmento Refactorizado**:
     ```python
     def calcular_rangos(size, fragmentos):
         tamF = size // fragmentos
         ranges = [[i, i + tamF - 1] for i in range(0, size, tamF)]
         ranges[-1][-1] = size
         return ranges
     ```

---

## Refactorización 2: Código para Descarga Secuencial

### Violaciones y Refactorizaciones

#### 1. Violación: Alta Complejidad Ciclomática
   - **Descripción**: La función `descarga_secuencial` manejaba múltiples tareas, lo que aumentaba su complejidad.
   - **Corrección/Refactorización**: Se dividió en subfunciones para verificar soporte de descarga parcial, calcular rangos, y reconstruir el archivo.
   - **Fragmento Refactorizado**:
     ```python
     def verificar_soporte_descarga_parcial(response):
         if 'Accept-Ranges' not in response.headers or response.headers['Accept-Ranges'].lower() != 'bytes':
             raise ValueError("Descarga parcial no soportada")
         print('Descarga parcial soportada')

     def obtener_rangos_descarga(size, fragmentos):
         tamF = size // fragmentos
         ranges = [(i, i + tamF - 1) for i in range(0, size, tamF)]
         ranges[-1] = (ranges[-1][0], size - 1)
         return ranges
     ```

#### 2. Violación: Código Repetido (DRY)
   - **Descripción**: La lógica de manejo de fragmentos descargados se encontraba duplicada.
   - **Corrección/Refactorización**: Se encapsuló esta lógica en una función dedicada para su reutilización.
   - **Fragmento Refactorizado**:
     ```python
     def manejar_fragmentos(fragmentos_descargados, directorio, nombre):
         ruta_completa = os.path.join(directorio, nombre)
         with open(ruta_completa, 'wb') as file:
             for data in fragmentos_descargados:
                 if data is None:
                     raise IOError("Error en fragmentos, no se pudo reconstruir el archivo.")
                 file.write(data)
         print(f'Archivo descargado y reconstruido con éxito en: {ruta_completa}')
     ```

#### 3. Violación: Manejo de Errores Distribuido
   - **Descripción**: El manejo de errores estaba disperso a lo largo del código, complicando la detección y gestión de excepciones.
   - **Corrección/Refactorización**: Se centralizó el manejo de errores utilizando una función dedicada para capturar y registrar errores.
   - **Fragmento Refactorizado**:
     ```python
     def manejar_errores(e, contexto):
         print(f"Error en {contexto}: {e}")
     ```

---

## Reporte SonarLint de Análisis Estático

### Refactorización 1: Código para Descarga Paralela

1. **Complejidad Ciclomática Reducida**: El análisis de SonarLint reportaba alta complejidad debido a la sobrecarga de la función `descarga_paralela`. Tras la refactorización, la complejidad disminuyó significativamente al dividir responsabilidades en funciones más pequeñas.

2. **Duplicación de Código Eliminada**: Se reportó código duplicado relacionado con la lógica de rangos y manejo de fragmentos. Esto fue resuelto consolidando la lógica en funciones reutilizables.

3. **Manejo de Errores Mejorado**: La gestión de errores distribuida fue corregida centralizando el manejo de excepciones, eliminando advertencias críticas relacionadas con posibles fallos.

### Refactorización 2: Código para Descarga Secuencial

1. **Reducción de Complejidad**: La complejidad ciclomatica fue reducida al dividir las responsabilidades en subfunciones más pequeñas y específicas.

2. **Mejor Manejo de Errores**: La inclusión de una función para el manejo centralizado de errores eliminó advertencias sobre la falta de robustez en el manejo de excepciones.

---
