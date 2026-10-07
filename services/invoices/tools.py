from google.genai import types

submit_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="submit_invoice",
            description=(
                "Llamar cuando el negocio que emitió la factura es un "
                "supermercado o tienda de víveres, y por lo tanto debe "
                "registrarse como una compra de mercado."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "message_id": {
                        "type": "string",
                        "description": "Id del mensaje que se está analizando"
                    }}},
        )
    ]
)
