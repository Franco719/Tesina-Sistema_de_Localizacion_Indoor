#include "sdkconfig.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_wifi.h"
#include "esp_log.h"
#include "esp_event.h"
#include "nvs_flash.h"
#include "freertos/event_groups.h"
#include "wifi_helpers.h"
#include "config.h"

// Datos de la red específica a conectar
#define TARGET_SSID CONFIG_EXAMPLE_WIFI_SSID
#define TARGET_PASS CONFIG_EXAMPLE_WIFI_PASSWORD

void wifi_scan(wifi_ap_record_t *ap_records)
{   
    ESP_LOGI(APP_TAG, "Iniciando escaneo de redes Wi-Fi...");

    // 1. Configurar parámetros de escaneo (Dejamos todo vacío para que escanee todo por defecto)
    wifi_scan_config_t scan_config = {
        .ssid = NULL,
        .bssid = NULL,
        .channel = 0,
        .show_hidden = false
    };

    // 2. Ejecutar escaneo físico. El 'true' significa bloqueante (el programa espera acá a terminar)
    ESP_ERROR_CHECK(esp_wifi_scan_start(&scan_config, true));

    // 3. Averiguar cuántas redes se detectaron en total
    uint16_t ap_count = 0;
    ESP_ERROR_CHECK(esp_wifi_scan_get_ap_num(&ap_count));
    ESP_LOGI(APP_TAG, "Redes encontradas en total: %d", ap_count);

    // Si encontró redes, procesamos hasta MAX_SCAN_RECORDS
    if (ap_count > 0) {
        // Ajustamos la cantidad para leer: si detectó 30, solo traemos un máximo de 10 bytes/estructuras
        uint16_t number_to_read = (ap_count > MAX_SCAN_RECORDS) ? MAX_SCAN_RECORDS : ap_count;
        
        // Esta función llena nuestro array con el SSID y RSSI y libera la RAM interna del driver
        ESP_ERROR_CHECK(esp_wifi_scan_get_ap_records(&number_to_read, ap_records));

        //bool red_encontrada = false;

        // 4. El bucle 'for' clásico para recorrer el array
        for (int i = 0; i < number_to_read; i++) {
            // Imprimimos el nombre de la red (SSID) y su fuerza de señal (RSSI)
            ESP_LOGI(
                APP_TAG,
                "[%d] SSID: %-20s | BSSID: %02X:%02X:%02X:%02X:%02X:%02X | RSSI: %d dBm",
                i + 1,
                ap_records[i].ssid,
                ap_records[i].bssid[0],
                ap_records[i].bssid[1],
                ap_records[i].bssid[2],
                ap_records[i].bssid[3],
                ap_records[i].bssid[4],
                ap_records[i].bssid[5],
                ap_records[i].rssi
            );

        }

    } 
    else {
        ESP_LOGE(APP_TAG, "No se detectaron redes inalámbricas.");
    }
}

void connect_wifi (wifi_ap_record_t *ap_records)
{   
    uint8_t i = 0;
    bool red_encontrada = false;
    while ((!red_encontrada) && (i < MAX_SCAN_RECORDS)) {
        if (strcmp((char *)ap_records[i].ssid, TARGET_SSID) == 0) {
            ESP_LOGI(
                APP_TAG,
                "[%d] SSID: %-20s | BSSID: %02X:%02X:%02X:%02X:%02X:%02X | RSSI: %d dBm",
                i + 1,
                ap_records[i].ssid,
                ap_records[i].bssid[0],
                ap_records[i].bssid[1],
                ap_records[i].bssid[2],
                ap_records[i].bssid[3],
                ap_records[i].bssid[4],
                ap_records[i].bssid[5],
                ap_records[i].rssi
            );
            
            ESP_LOGI(APP_TAG, "Configurando credenciales y conectando...");
            
            wifi_config_t wifi_config = {0}; // Recaudo de C: Inicializamos la estructura en 0 completo
            
            // Copiamos de forma segura los textos hacia los arreglos fijos de la estructura
            strcpy((char *)wifi_config.sta.ssid, TARGET_SSID);
            strcpy((char *)wifi_config.sta.password, TARGET_PASS);

            ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wifi_config));
            
            // Ordenamos la conexión manual
            esp_err_t res = esp_wifi_connect();
            if (res == ESP_OK) {
                ESP_LOGW(APP_TAG, "Comando de conexión enviado con éxito.");
            }

            red_encontrada = true;
        }

        else {
            i ++;
        }
    }
}