from marshmallow import Schema, fields, validate, validates_schema, ValidationError


class PreEntrenamientoSchema(Schema):
    
    metodo_filtrado = fields.Str(required=True,validate=validate.OneOf(["Kalman", "Mediana", "Media", "Ninguno"]))
    nombre_entrenamiento = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    
class CambiarNombreSchema(Schema):

    nuevo_nombre = fields.Str(required=True, validate=validate.Length(min=1, max=100))

    
pre_entrenamiento_schema = PreEntrenamientoSchema()
cambio_nombre_schema = CambiarNombreSchema()