#include "sdkconfig.h"
#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_wifi.h"
#include "esp_log.h"
#include "esp_event.h"
#include "nvs_flash.h"
#include "freertos/event_groups.h"
#include "wifi_helpers.h" // Se trae la funcion connect_wifi y wifi_scan
#include "helpers.h"
#include "config.h"


// Creamos un grupo de eventos para avisarle al programa cuándo tenemos IP
static EventGroupHandle_t s_wifi_event_group;
#define WIFI_CONNECTED_BIT BIT0

// Manejador de eventos (Event Handler) ahora va a activar este BIT
static void event_handler(void* arg, esp_event_base_t event_base, int32_t event_id, void* event_data) 
{
    // Cargo variables de entorno
    char *TAG = getenv("TAG");

    if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_DISCONNECTED) {
        ESP_LOGW(TAG, "Desconectado del punto de acceso.");
    } else if (event_base == IP_EVENT && event_id == IP_EVENT_STA_GOT_IP) {
        ip_event_got_ip_t* event = (ip_event_got_ip_t*) event_data;
        ESP_LOGI(TAG, "¡IP Obtenida!: " IPSTR, IP2STR(&event->ip_info.ip));
        
        // CLAVE: Activamos el bit para destrabar el app_main
        xEventGroupSetBits(s_wifi_event_group, WIFI_CONNECTED_BIT);
    }
}

void app_main(void)
{
    // 1. Inicializar NVS y crear el grupo de eventos
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    s_wifi_event_group = xEventGroupCreate();

    // 2. Inicialización de Wi-Fi por única vez
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_sta();
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_start());

    // Registrar los eventos de desconexión y obtención de IP
    ESP_ERROR_CHECK(esp_event_handler_instance_register(WIFI_EVENT, ESP_EVENT_ANY_ID, &event_handler, NULL, NULL));
    ESP_ERROR_CHECK(esp_event_handler_instance_register(IP_EVENT, IP_EVENT_STA_GOT_IP, &event_handler, NULL, NULL));

    // Colección de datos en el Stack del main (A salvo)
    wifi_ap_record_t wifi_record[MAX_SCAN_RECORDS];

    // 🔄 BUCLE INFINITO DE LOCALIZACIÓN
    while (1) {

        // Forzamos la desconexión para limpiar cualquier intento previo fallido
        esp_wifi_disconnect();

        ESP_LOGI(APP_TAG, "--- NUEVOS 10 SEGUNDOS: INICIANDO CICLO ---");

        // Limpiamos por completo el array llenándolo con ceros en cada ciclo
        memset(wifi_record, 0, sizeof(wifi_record));

        // PASO A: Escanear el aire (Guarda los dBm de las redes vecinas)
        wifi_scan(wifi_record); 

        // PASO B: Conectarse a la red objetivo para poder transmitir
        connect_wifi(wifi_record);

        // PASO C: Sincronización en C. El programa se frena acá de forma segura 
        // esperando hasta 5 segundos a que el router de IP.
        EventBits_t bits = xEventGroupWaitBits(s_wifi_event_group,
                                              WIFI_CONNECTED_BIT,
                                              pdTRUE, // Limpiar el bit al salir
                                              pdFALSE,
                                              pdMS_TO_TICKS(5000)); // Timeout de 5 seg

        if (bits & WIFI_CONNECTED_BIT) {
            ESP_LOGW(APP_TAG, "¡Listo para enviar datos al servidor!");
            
            // sizeof da la longitud en bits
            uint8_t cant_wifi_records = sizeof(wifi_record) / sizeof(wifi_record[0]);

            send_data_to_server(wifi_record, cant_wifi_records); 
            
            vTaskDelay(pdMS_TO_TICKS(1000)); // Esperamos un segundo a que termine de transmitir
            
            // PASO E: Nos desconectamos para dejar el chip limpio para el próximo escaneo
            esp_wifi_disconnect();
        } else {
            ESP_LOGE(APP_TAG, "No se pudo obtener IP a tiempo. Saltando envío en este ciclo.");
        }

        // PASO F: Descanso del ciclo (Completar los 10 segundos en total)
        ESP_LOGI(APP_TAG, "Ciclo terminado. Durmiendo...");
        vTaskDelay(pdMS_TO_TICKS(5000)); 
    }
}