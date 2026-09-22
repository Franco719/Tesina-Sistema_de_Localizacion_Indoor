from marshmallow import Schema, fields, validate, validates_schema, ValidationError

METODOS_CON_VENTANA = {"Media", "Mediana"}

class PreEntrenamientoSchema(Schema):

    nombre_sala = fields.Str(required=True, validate=validate.Length(min=1, max=32))
    metodo_filtrado = fields.Str(required=True,validate=validate.OneOf(["Kalman", "Mediana", "Media", "Ninguno"]))
    ventana = fields.Integer(required=False, allow_none=True, validate=validate.Range(min=3, max=99))

    @validates_schema
    def validar_ventana(self, data, **kwargs):

        metodo = data["metodo_filtrado"]

        if metodo in METODOS_CON_VENTANA:

            ventana = data.get("ventana")

            if ventana is None:
                raise ValidationError(
                    "La ventana es obligatoria para este método.",
                    field_name="ventana"
                )

            if ventana % 2 == 0:
                raise ValidationError(
                    "La ventana debe ser un número impar.",
                    field_name="ventana"
                )
        
     
pre_entrenamiento_schema = PreEntrenamientoSchema()   
    