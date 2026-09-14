# Sistema de Localización Indoor de Carros de Transporte

Sistema de localización indoor orientado a determinar la ubicación de carros utilizados para el transporte de notebooks dentro de un establecimiento educativo.

El proyecto utiliza dispositivos **ESP32** para realizar mediciones de redes Wi-Fi disponibles y obtener sus valores de **RSSI (Received Signal Strength Indicator)**. Estas mediciones constituyen una huella digital (*Wi-Fi fingerprint*) del entorno, que posteriormente es procesada por un servidor para estimar la ubicación del carro mediante una **red neuronal**.

El proyecto corresponde a la **tesina / PAE-PPS de la carrera**, y tiene como uno de sus objetivos estudiar el impacto del procesamiento de las señales RSSI mediante un **filtro de Kalman** sobre la precisión de la localización.

---

## Objetivo

El objetivo principal es desarrollar un sistema capaz de estimar en qué aula se encuentra un carro de transporte de notebooks a partir de las redes Wi-Fi detectadas desde un dispositivo ESP32.

Los carros normalmente permanecen ubicados dentro de un aula, aunque pueden ser trasladados temporalmente a otras ubicaciones. Por este motivo, disponer de un mecanismo automatizado de localización permitiría conocer su ubicación sin necesidad de realizar una inspección física.

El sistema busca aprovechar la infraestructura Wi-Fi existente para realizar la localización sin requerir necesariamente infraestructura adicional de posicionamiento.

---

## Funcionamiento general

El sistema se basa en tres componentes principales:

```text
┌──────────────────────┐
│        ESP32         │
│                      │
│ Escaneo de redes     │
│ Wi-Fi + RSSI         │
└──────────┬───────────┘
           │
           │ Mediciones RSSI
           ▼
┌──────────────────────┐
│       Servidor       │
│                      │
│ Procesamiento        │
│ de datos             │
└──────────┬───────────┘
           │
           │ Características
           ▼
┌──────────────────────┐
│   Red Neuronal       │
│                      │
│ Estimación de        │
│ ubicación            │
└──────────┬───────────┘
           │
           ▼
      ┌─────────┐
      │  Aula   │
      └─────────┘
```

El ESP32 realiza periódicamente un escaneo de las redes Wi-Fi visibles y obtiene, para cada red detectada, información como su identificador y nivel de señal RSSI.

Los datos obtenidos son enviados al servidor, donde son procesados y utilizados como entrada para el sistema de localización.

---

## Wi-Fi Fingerprinting

La técnica utilizada se basa en **Wi-Fi fingerprinting**.

La idea consiste en caracterizar cada ubicación mediante las redes Wi-Fi que pueden ser detectadas desde ella y la intensidad de señal de cada una.

Por ejemplo, una medición podría representarse conceptualmente como:

```text
Ubicación: Aula A

AP_01 → -52 dBm
AP_02 → -67 dBm
AP_03 → -81 dBm
AP_04 → -90 dBm
```

Al realizar mediciones en diferentes aulas se construye un **dataset de entrenamiento**, donde cada conjunto de valores RSSI se encuentra asociado con una ubicación conocida.

Posteriormente, el modelo puede utilizar una nueva medición para estimar a qué ubicación corresponde.

---

## Procesamiento mediante filtro de Kalman

Uno de los aspectos de investigación del proyecto consiste en evaluar la utilización de un **filtro de Kalman** para reducir las variaciones y el ruido presentes en las mediciones RSSI.

Las señales Wi-Fi presentan fluctuaciones incluso cuando el dispositivo permanece en una misma ubicación. Estas variaciones pueden dificultar la identificación de una ubicación a partir de una única medición.

El proyecto plantea evaluar el procesamiento de los valores RSSI mediante Kalman en diferentes etapas del sistema.

### Durante la generación del dataset

```text
RSSI medido
     │
     ▼
Filtro de Kalman
     │
     ▼
RSSI procesado
     │
     ▼
Dataset de entrenamiento
```

### Durante la localización

```text
RSSI medido
     │
     ▼
Filtro de Kalman
     │
     ▼
RSSI procesado
     │
     ▼
Red neuronal
     │
     ▼
Ubicación estimada
```

De esta manera se busca analizar si la reducción del ruido de las señales permite obtener una mejora en el rendimiento del modelo de localización.

---

## Recolección del dataset

El sistema cuenta con una interfaz destinada a la recopilación de muestras para el entrenamiento.

El proceso de recolección permite seleccionar una ubicación conocida y registrar múltiples mediciones de las redes Wi-Fi disponibles.

Conceptualmente:

```text
Seleccionar aula
      │
      ▼
Iniciar entrenamiento
      │
      ▼
ESP32 realiza escaneo
      │
      ▼
Obtención de RSSI
      │
      ▼
Procesamiento
      │
      ▼
Almacenamiento de muestra
      │
      ▼
Repetición
```

Las muestras obtenidas se utilizan posteriormente para entrenar el modelo de localización.

El sistema contempla además el control del estado de la sesión de entrenamiento, evitando que una sesión permanezca activa indefinidamente.

---

## ESP32

El dispositivo ESP32 funciona como unidad de adquisición de datos.

Sus principales responsabilidades son:

- Escanear las redes Wi-Fi disponibles.
- Obtener los valores RSSI.
- Identificar las redes detectadas.
- Construir las mediciones correspondientes.
- Comunicarse con el servidor.
- Enviar los datos para su procesamiento.

El dispositivo realiza ciclos periódicos de adquisición para obtener nuevas mediciones del entorno.

---

## Servidor

El servidor recibe las mediciones realizadas por el ESP32 y proporciona los servicios necesarios para el procesamiento y la localización.

Entre sus responsabilidades se encuentran:

- Recepción de mediciones Wi-Fi.
- Procesamiento de valores RSSI.
- Gestión de las muestras del dataset.
- Gestión de las sesiones de entrenamiento.
- Comunicación con el modelo de inteligencia artificial.
- Estimación de la ubicación del carro.

El sistema dispone de un endpoint destinado al proceso de localización:

```text
/api/localizar
```

---

## Red neuronal

La estimación de la ubicación se realiza mediante una **red neuronal entrenada a partir del dataset de fingerprints Wi-Fi**.

El modelo recibe como entrada las características obtenidas a partir de las señales Wi-Fi y produce como resultado una estimación de la ubicación.

De forma simplificada:

```text
              Entrada
                 │
        ┌────────▼────────┐
        │  Valores RSSI   │
        │ de redes Wi-Fi  │
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │  Red neuronal   │
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │    Ubicación    │
        │    estimada     │
        └─────────────────┘
```

El rendimiento del modelo puede evaluarse comparando la ubicación estimada con la ubicación real conocida durante las pruebas.

---

## Arquitectura del sistema

La arquitectura general puede representarse de la siguiente manera:

```text
                    Wi-Fi
                     │
                     ▼
              ┌─────────────-┐
              │    ESP32     │
              │              │
              │ Wi-Fi Scan   │
              │ RSSI         │
              └──────┬──────-┘
                     │
                     │ HTTP
                     ▼
              ┌─────────────-┐
              │   Servidor   │
              │              │
              │ API          │
              │ Procesamiento│
              └──────┬──────-┘
                     │
              ┌──────┴──────┐
              │             │
              ▼             ▼
       ┌────────────┐ ┌─────────────┐
       │  Dataset   │ │   Modelo    │
       │            │ │  neuronal   │
       └────────────┘ └──────┬──────┘
                             │
                             ▼
                      Ubicación estimada
```

---

## Tecnologías

### Hardware

- ESP32
- Infraestructura Wi-Fi existente

### Software

- C/C++ para ESP32
- Python
- API HTTP
- Red neuronal
- Filtro de Kalman
- Redis para gestión del estado de las sesiones de entrenamiento

---

## Flujo de localización

El funcionamiento de una localización puede resumirse en los siguientes pasos:

1. El ESP32 inicia un ciclo de escaneo.
2. Se detectan las redes Wi-Fi disponibles.
3. Se obtiene el RSSI de cada red.
4. Los datos son enviados al servidor.
5. Los valores RSSI son procesados.
6. El conjunto de características se entrega al modelo.
7. La red neuronal realiza la predicción.
8. El sistema obtiene la ubicación estimada.

```text
Escaneo Wi-Fi
      ↓
Obtención de RSSI
      ↓
Envío al servidor
      ↓
Filtrado / procesamiento
      ↓
Red neuronal
      ↓
Predicción
      ↓
Ubicación
```

---

## Hipótesis de investigación

Una de las hipótesis planteadas en el proyecto es que el procesamiento de las mediciones RSSI mediante un **filtro de Kalman** puede reducir el ruido de las señales y mejorar el desempeño del sistema de localización.

La evaluación contempla comparar el comportamiento del sistema utilizando los datos RSSI originales frente a datos procesados mediante el filtro.

De esta forma se busca determinar experimentalmente si el filtrado de las señales produce una mejora significativa en la capacidad del modelo para identificar correctamente la ubicación.

---

## Dataset

El dataset se construye mediante mediciones realizadas en ubicaciones conocidas.

Cada muestra contiene información relacionada con las redes Wi-Fi detectadas y sus correspondientes valores RSSI, asociándose además con la ubicación en la que fue obtenida.

Conceptualmente:

| Red Wi-Fi | RSSI | Ubicación |
|---|---:|---|
| AP_01 | -52 dBm | Aula A |
| AP_02 | -67 dBm | Aula A |
| AP_03 | -81 dBm | Aula A |

Las mediciones se realizan repetidamente para obtener una cantidad suficiente de muestras representativas de cada ubicación.

---

## Estado del proyecto

El proyecto se encuentra en desarrollo dentro del marco de la **tesina / PAE-PPS**.

Actualmente se trabaja en:

- Sistema de adquisición de datos mediante ESP32.
- Comunicación entre ESP32 y servidor.
- Recolección del dataset de fingerprints Wi-Fi.
- Procesamiento de señales RSSI.
- Implementación y evaluación del filtro de Kalman.
- Entrenamiento de la red neuronal.
- Evaluación de la precisión de localización.
- Comparación entre datos RSSI sin filtrar y filtrados.

---

## Objetivos experimentales

Las pruebas del sistema buscan evaluar principalmente:

- Precisión de la localización.
- Comportamiento de las mediciones RSSI.
- Variabilidad de las señales Wi-Fi.
- Influencia del filtrado sobre los datos.
- Desempeño de la red neuronal.
- Diferencia entre utilizar RSSI original y RSSI procesado mediante Kalman.

El objetivo final es determinar si el procesamiento de las señales permite obtener una localización indoor más estable y precisa.