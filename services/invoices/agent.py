from google.genai import types

from shared.llm import client, MODEL_NAME
from shared.errors import InvoiceProcessingError
from services.invoices.tools import submit_tool


def run_invoice_agent(service, message_id: str, business_name: str) -> str:
    prompt = (
        f"El negocio que emitió la factura con id : {message_id} es: {business_name}. "
        "Si es un supermercado o tienda de víveres, llama a la función "
        "`submit_invoice`. Si no lo es, responde en texto explicando en no "
        "mas de 50 caracteres cómo fue identificado el negocio ej, optica, almacen de ropa, etc."
        "Llama a `submit_invoice` con el parámetro `message_id`"
        "Cuando tengas la respuesta de submit_invoice "
        "dile al usuario que el bill se ha creado e indicale que puede visualizar en "
        "https://merkadapp-638bb.web.app/#/bills/edit/`bill_id`"
    )
    contents = [types.Content(role="user", parts=[types.Part(text=prompt)])]

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=contents,
        config=types.GenerateContentConfig(tools=[submit_tool]),
    )

    part = response.candidates[0].content.parts[0]

    if part.function_call is None:
        return response.text

    if part.function_call.name != "submit_invoice":
        raise InvoiceProcessingError(
            f"Gemini pidió una tool desconocida: {part.function_call.name}")

    handler = _submit_invoice_for_real
    result = handler(service, part.function_call.args)

    contents.append(response.candidates[0].content)
    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_function_response(
                name="submit_invoice", response=result)],
        )
    )
    final_response = client.models.generate_content(
        model=MODEL_NAME,
        contents=contents,
        config=types.GenerateContentConfig(tools=[submit_tool]),
    )
    return final_response.text


def _submit_invoice_for_real(service, args: dict) -> dict:
    from services.invoices.mail_reader import find_zip_attachment, extract_xml_from_zip
    from shared.merkadapp_client import submit_to_merkadapp_api

    zip_bytes = find_zip_attachment(service, args["message_id"])
    if zip_bytes is None:
        return {"status": "error", "message": "No se encontró adjunto ZIP"}
    xml_bytes = extract_xml_from_zip(zip_bytes)
    bill_id = submit_to_merkadapp_api(xml_bytes)
    return {"status": "success", "bill_id": bill_id}
