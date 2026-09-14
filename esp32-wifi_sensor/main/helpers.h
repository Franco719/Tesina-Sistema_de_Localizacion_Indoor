#ifndef HELPERS_H
#define HELPERS_H

#include "esp_wifi.h"

void send_data_to_server(wifi_ap_record_t *records, int cantidad);

#endif