from marshmallow import Schema, fields, validate


class ESP32ReceiverSchema(Schema):
    ssid = fields.Str(required=True, validate=validate.Length(min=1, max=32))
    rssi = fields.Int(required=True, validate=validate.Range(min=-127, max=0))


wifi_records_schema = ESP32ReceiverSchema(many=True)