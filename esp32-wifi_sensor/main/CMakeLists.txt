idf_component_register(SRCS "wifi_helpers.c" "app_main.c" "helpers.c"
                    PRIV_REQUIRES esp_wifi nvs_flash 
                    INCLUDE_DIRS "."
                    REQUIRES esp_http_client mbedtls)
