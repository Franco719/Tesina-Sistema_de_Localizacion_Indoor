#ifndef WIFI_HELPERS_H
#define WIFI_HELPERS_H

#include "esp_wifi.h"

void connect_wifi (wifi_ap_record_t *ap_records);
void wifi_scan(wifi_ap_record_t *ap_records);

#endif