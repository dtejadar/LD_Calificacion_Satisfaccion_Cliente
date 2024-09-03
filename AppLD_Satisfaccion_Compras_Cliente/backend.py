from fastapi import FastAPI, Request
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt
import io
import base64
from fastapi.responses import JSONResponse

#Se importa para que no se intente levantar una ventana emergente con la gráfica
import matplotlib
matplotlib.use('Agg')

app = FastAPI()

# Definición de las variables de entrada y salida
entrega = ctrl.Antecedent(np.arange(0, 11, 0.5), 'entrega')
producto = ctrl.Antecedent(np.arange(0, 11, 0.5), 'producto')
servicio = ctrl.Antecedent(np.arange(0, 11, 0.5), 'servicio')
satisfaccion = ctrl.Consequent(np.arange(0, 11, 0.5), 'satisfaccion')

# Funciones de membresía para las entradas y la salida
entrega['muy_lento'] = fuzz.trapmf(entrega.universe, [0, 0, 2, 4])
entrega['lento'] = fuzz.trimf(entrega.universe, [2, 5, 8])
entrega['rapido'] = fuzz.trapmf(entrega.universe, [6, 8, 10, 10])

producto['defectuoso'] = fuzz.trapmf(producto.universe, [0, 0, 2, 4])
producto['aceptable'] = fuzz.trimf(producto.universe, [3, 5, 7])
producto['perfecto'] = fuzz.trapmf(producto.universe, [6, 8, 10, 10])

servicio['malo'] = fuzz.trapmf(servicio.universe, [0, 0, 2, 4])
servicio['regular'] = fuzz.trimf(servicio.universe, [3, 5, 7])
servicio['excelente'] = fuzz.trapmf(servicio.universe, [6, 8, 10, 10])

satisfaccion['insatisfecho'] = fuzz.trimf(satisfaccion.universe, [0, 0, 5])
satisfaccion['neutral'] = fuzz.trimf(satisfaccion.universe, [4, 5, 6])
satisfaccion['satisfecho'] = fuzz.trimf(satisfaccion.universe, [5, 10, 10])

# Reglas de inferencia difusa
rule1 = ctrl.Rule(entrega['muy_lento'] | producto['defectuoso'], satisfaccion['insatisfecho'])
rule2 = ctrl.Rule(entrega['rapido'] & servicio['excelente'], satisfaccion['satisfecho'])
rule3 = ctrl.Rule(servicio['malo'] & producto['defectuoso'], satisfaccion['insatisfecho'])
rule4 = ctrl.Rule(entrega['lento'] & servicio['regular'] & producto['aceptable'], satisfaccion['neutral'])
rule5 = ctrl.Rule(entrega['rapido'] & producto['perfecto'] & servicio['excelente'], satisfaccion['satisfecho'])

satisfaccion_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5])
satisfaccion_sim = ctrl.ControlSystemSimulation(satisfaccion_ctrl)

# Ruta para manejar la calificacion del cliente
@app.post("/customerRating")
async def obtener_calificacion(request: Request):
    data = await request.json()

    # Asignar valores de entrada
    satisfaccion_sim.input['entrega'] = data['entrega']
    satisfaccion_sim.input['producto'] = data['producto']
    satisfaccion_sim.input['servicio'] = data['servicio']

    # Ejecutar la simulación difusa
    satisfaccion_sim.compute()

    # Obtener el resultado de satisfacción
    try:
        resultado = satisfaccion_sim.output['satisfaccion']
    except KeyError as e:
        print(f"KeyError: {e}")
        return {"error": "Error en la simulación difusa"}
    
    # Visualizar resultado
    fig, ax = plt.subplots()
    satisfaccion.view(sim=satisfaccion_sim, ax=ax)
    plt.title('Resultado de Satisfacción')

    # Guardar gráfico en un buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # Convertir la imagen a base64
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')

     # Retornar el resultado y la imagen en base64
    return JSONResponse(content={
        "satisfaccion": resultado,
        "graph_url": f"data:image/png;base64,{img_base64}"
    })
