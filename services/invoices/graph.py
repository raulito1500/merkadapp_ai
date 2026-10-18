from langgraph.graph import StateGraph, START, END
from shared.llm import client, MODEL_NAME
from services.invoices.agent import _submit_invoice_for_real
from services.invoices.tools import submit_tool
from shared.errors import InvoiceProcessingError
from typing import TypedDict

from google.genai import types


class InvoiceState(TypedDict):
    service: object
    message_id: str
    business_name: str
    contents: list
    function_call: object | None
    args: dict | None
    result: dict | None
    final_text: str | None


def decide_node(state: InvoiceState) -> dict:
    prompt = (
        f"El negocio que emitió la factura con id : {state['message_id']} es: {state['business_name']}. "
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
    contents.append(response.candidates[0].content)

    return {
        "contents": contents,
        "function_call": part.function_call,
        "final_text": response.text if part.function_call is None else None,
        "args": None if part.function_call is None else part.function_call.args
    }


def execute_node(state: InvoiceState) -> dict:
    fc = state["function_call"]
    if fc.name != "submit_invoice":
        raise InvoiceProcessingError(
            f"Gemini pidió una tool desconocida: {fc.name}")
    result = _submit_invoice_for_real(state["service"], state["args"])
    return {"result": result}


def respond_node(state: InvoiceState) -> dict:
    contents = state["contents"] + [
        types.Content(
            role="user",
            parts=[types.Part.from_function_response(
                name="submit_invoice", response=state["result"])],
        )
    ]
    final_response = client.models.generate_content(
        model=MODEL_NAME,
        contents=contents,
        config=types.GenerateContentConfig(tools=[submit_tool]),
    )
    return {"final_text": final_response.text}


def route_after_decision(state: InvoiceState) -> str:
    return END if state["function_call"] is None else "execute"


graph = StateGraph(InvoiceState)
graph.add_node("decide", decide_node)
graph.add_node("execute", execute_node)
graph.add_node("respond", respond_node)

graph.add_edge(START, "decide")
graph.add_conditional_edges("decide", route_after_decision, {
                            "execute": "execute", END: END})
graph.add_edge("execute", "respond")
graph.add_edge("respond", END)

invoice_graph = graph.compile()
