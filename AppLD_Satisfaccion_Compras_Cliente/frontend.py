from reactpy import component, html, use_state
import httpx  # Cliente HTTP para python
import base64

@component
def SatisfaccionCliente():
    delivery_rating, set_delivery_rating = use_state("")
    product_rating, set_product_rating = use_state("")
    service_rating, set_service_rating = use_state("")
    satisfaction_result, set_satisfaction_result = use_state("")
    graph_url, set_graph_url = use_state("")

    def handle_change(set_value):
        def _handle_change(event):
            value = event['target'].get('value', '')
            set_value(value)
        return _handle_change

    async def handle_submit(event):
        if delivery_rating and product_rating and service_rating:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://127.0.0.1:8001/api/customerRating",
                    json={
                        "entrega": float(delivery_rating),
                        "producto": float(product_rating),
                        "servicio": float(service_rating)
                    }
                )
                if response.status_code == 200:
                    result = response.json()
                    set_satisfaction_result(result.get("satisfaccion", ""))
                    set_graph_url(result.get("graph_url", ""))
                else:
                    print(f"Error: {response.status_code}")

    return html.div(
        html.h3("Califica tu compra realizada"),
        html.div(
            html.label("Calificación de Entrega:"),
            html.input({
                "type": "number",
                "value": delivery_rating,
                "min": 0,
                "max": 10,
                "step": 0.5,
                "onchange": handle_change(set_delivery_rating)
            })
        ),
        html.div(
            html.label("Calificación de Producto:"),
            html.input({
                "type": "number",
                "value": product_rating,
                "min": 0,
                "max": 10,
                "step": 0.5,
                "onchange": handle_change(set_product_rating)
            })
        ),
        html.div(
            html.label("Calificación de Servicio:"),
            html.input({
                "type": "number",
                "value": service_rating,
                "min": 0,
                "max": 10,
                "step": 0.5,
                "onchange": handle_change(set_service_rating)
            })
        ),
        html.button({
            "type": "button",  # Cambia el tipo a "button" para evitar el comportamiento por defecto del formulario
            "onclick": handle_submit
        }, "Enviar"),
        html.div(
            html.h4("Resultado de Satisfacción:"),
            html.p(satisfaction_result)
        ),
        html.div(
            html.h4("Gráfico de Satisfacción:"),
            html.img({"src": graph_url})
        )
    )
