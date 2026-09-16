#include <stdio.h>
#include "helpers.h"
#include "esp_http_client.h"
#include "cJSON.h"
#include "esp_wifi.h"
#include "esp_log.h"
#include "config.h"
/*#include "esp_crt_bundle.h"*/


void send_data_to_server(wifi_ap_record_t *records, int cantidad)
{
    // 1. Crear el objeto JSON en memoria usando cJSON
    cJSON *root = cJSON_CreateArray();
    
    for(int i = 0; i < cantidad; i++) {
        // Validación A: Si el SSID está vacío (primer caracter es fin de cadena), lo salteamos
        if (records[i].ssid[0] == '\0') {
            continue;
        }

        // Validación B: Verificar que el SSID solo tenga caracteres legibles (ASCII 32 al 126)
        bool ssid_valido = true;
        for (int j = 0; j < sizeof(records[i].ssid) && records[i].ssid[j] != '\0'; j++) {
            char c = records[i].ssid[j];
            if (c < 32 || c > 126) {
                ssid_valido = false;
                break; // Carácter basura detectado
            }
        }

        // Si pasó los filtros, lo agregamos de forma segura al JSON
        if (ssid_valido) {
            cJSON *item = cJSON_CreateObject();
            cJSON_AddStringToObject(item, "ssid", (char*)records[i].ssid);
            cJSON_AddNumberToObject(item, "rssi", records[i].rssi);
            cJSON_AddItemToArray(root, item);
        }
    }
    
    char *post_data = cJSON_PrintUnformatted(root); // Convierte a string

    // 2. Configurar el cliente HTTP de ESP-IDF
    esp_http_client_config_t config = {
        .url = SERVER_LOCATE_IP,
        .method = HTTP_METHOD_POST,
    };
    esp_http_client_handle_t client = esp_http_client_init(&config);

    // Para HTTPS, no funciona pero es por aca
    /*esp_http_client_config_t config = {
        .url = SERVER_LOCATE_IP,
        .transport_type = HTTP_TRANSPORT_OVER_SSL,
        .method = HTTP_METHOD_POST,
        .crt_bundle_attach = esp_crt_bundle_attach,
    };
    esp_http_client_handle_t client = esp_http_client_init(&config);*/

    // Encabezado para asegurar la validacion con el servidor
    esp_http_client_set_header(client, "API-Key", API_SECRET_KEY);
    
    // Encabezado para enviar JSON
    esp_http_client_set_header(client, "Content-Type", "application/json");
    esp_http_client_set_post_field(client, post_data, strlen(post_data));

    // Ejecutar el envío físico por la antena
    esp_err_t err = esp_http_client_perform(client);
    if (err == ESP_OK) {
        ESP_LOGI(APP_TAG, "Datos enviados de forma limpia. Código HTTP: %d", esp_http_client_get_status_code(client));
    }
    
    // 3. Limpieza de memoria RAM en C
    esp_http_client_cleanup(client);
    cJSON_Delete(root);
    free(post_data);
}