# 📡 Nodo Sensor de Geolocalización Indoor (ESP32-C3)

Este componente del proyecto se encarga de actuar como un **nodo recolector (*sniffer*) y emisor de radiofrecuencia**. Su objetivo principal es escanear cíclicamente el entorno inalámbrico, medir la intensidad de señal de las redes vecinas y transmitir de forma segura los datos a un servidor central.

## 🚀 Arquitectura del Ciclo de Ejecución
El programa corre de manera continua dentro de un bucle infinito en **FreeRTOS** sincronizado por grupos de eventos, ejecutando las siguientes fases cada **10 segundos**:

1. **Fase de Escaneo (Sniffer):** Despierta el módem de radio y realiza un barrido síncrono/bloqueante de todos los canales Wi-Fi para capturar los identificadores (SSID) y la potencia de señal (RSSI) de los puntos de acceso cercanos.
2. **Fase de Conexión:** Utiliza las credenciales de la red local para conectarse al router que provee acceso al servidor.
3. **Sincronización por Eventos:** Detiene el hilo de ejecución de forma pasiva (`xEventGroupWaitBits`) sin consumir ciclos de reloj hasta que el controlador de red confirma la asignación de una dirección IP válida.
4. **Fase de Emisión:** Empaqueta la colección de redes en un formato estructurado JSON y realiza una petición `POST HTTP` segura inyectando un token criptográfico en los encabezados.
5. **Desconexión y Limpieza:** Corta el enlace Wi-Fi de forma ordenada para mitigar el ruido en el canal de radio y duerme el procesador durante el tiempo de descanso restante.

---

## 🛠️ Requisitos de Hardware y Entorno
* **Hardware:** Placa de desarrollo basada en el SoC **Espressif ESP32-C3** (ej: SuperMini / NodeMCU C3).
  * *Nota de hardware:* Cuenta con **4MB de memoria Flash embebida** de almacenamiento no volátil (NVS).
* **Entorno de Desarrollo:** Visual Studio Code junto con la extensión oficial **ESP-IDF** (Extensión de Espressif).
* **Toolchain de Compilación:** Compilador GCC embebido gestionado mediante el script global de entorno `idf.py`.

---

## ⚙️ Configuración del Proyecto (Kconfig)
El firmware evita el uso de valores fijos (*hardcodeados*) en el código fuente de C. Toda la parametrización se realiza de forma gráfica mediante el **SDK Configuration Editor** de VS Code.

Para modificar los parámetros esenciales:
1. Presiona `Ctrl + Shift + P` en VS Code.
2. Ejecuta `ESP-IDF: SDK Configuration Editor`.
3. Navega hasta el menú **"Example Configuration"** para configurar:
   * **WiFi SSID:** Nombre de la red local para el envío de datos.
   * **WiFi Password:** Contraseña de la red inalámbrica.
   * **API Secret Key:** Token de autenticación requerido por el servidor Flask (`X-API-Key`).
   * **Blink GPIO number:** Configurado en el **GPIO 8** (LED integrado de la placa en modo *Active Low*).

---

### 🔐 Configuración de Variables Locales (`config.h`)
Por motivos de seguridad y manejo de credenciales que no se administran mediante el menú visual de Kconfig, el firmware requiere la existencia de un archivo de cabecera local llamado `config.h` ubicado en la raíz del directorio de código fuente (`main/config.h`). 

⚠️ **Este archivo está incluido en el `.gitignore` y nunca debe subirse al repositorio público.**

Para que el proyecto compile correctamente, debes crear el archivo `main/config.h` manualmente con la siguiente estructura base:

```c
#ifndef CONFIG_H
#define CONFIG_H

#define APP_TAG             "ESP32-WiFi_Sensor"
#define MAX_SCAN_RECORDS    10

// Parámetros experimentales o direcciones IP fijas del servidor de pruebas
#define SERVER_BASE_IP      "/localhost"
#define SERVER_LOCATE_IP    "/localhost/api/localizar"

// Token de autenticación para los encabezados HTTP (si no se define en Kconfig)
#define API_SECRET_KEY      "secret_key"

#endif // CONFIG_H
```
***

## 🚀 Instrucciones de Despliegue

### 1. Activar el Entorno de ESP-IDF
Antes de compilar, carga las variables de entorno de Espressif en tu terminal de Linux:
```bash
. \$HOME/esp/esp-idf/export.sh
```

### 2. Limpieza de Caches del Compilador
Si moviste el proyecto de directorio o experimentas problemas con caracteres especiales en las rutas, limpia la configuración previa:
```bash
idf.py fullclean
```

### 3. Compilación, Grabación y Monitoreo (UART)
Conecta tu ESP32-C3 mediante el cable USB directo a la computadora. Asegúrate de configurar el método de flasheo en **UART** en la barra inferior de VS Code y ejecuta:
```bash
idf.py -p /dev/ttyACM0 build flash monitor
```
*(Reemplaza `/dev/ttyACM0` por el puerto serial asignado a la placa por tu distribución de Linux).*

### 🛠️ Resolución de Problemas Frecuentes

* **El dispositivo se queda congelado en `waiting for download`:**
  El chip entró en modo de arranque de fábrica por hardware. Presiona y suelta una sola vez el botón físico **`RST` (o `EN`)** de la placa para forzar el reinicio al modo de ejecución normal.
* **Fallo de comunicación JTAG (`** Flashing Failed **`):**
  Ocurre si OpenOCD intenta congelar el procesador mientras ejecuta tareas críticas de FreeRTOS. Cambia el método de flasheo a **UART** en la barra de VS Code para forzar el reinicio eléctrico mediante las líneas RTS/DTR del cable USB.
* **El LED parpadea de forma invertida:**
  Debido al diseño eléctrico de las placas ESP32-C3 SuperMini, el LED integrado opera en modo *Active Low*. Cuando el log de la terminal imprima `Turning the LED ON!`, el foco físico se apagará, y viceversa. Es el comportamiento esperado.
