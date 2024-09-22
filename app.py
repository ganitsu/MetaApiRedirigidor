from flask import Flask, request, jsonify
from meta_ai_api import MetaAI
import time
import threading

app = Flask(__name__)

# Almacena las instancias de MetaAI
instances = {}
# Almacena el tiempo de creación de cada instancia
instance_timestamps = {}

# Función para eliminar instancias inactivas
def cleanup_instances():
    while True:
        time.sleep(30)  # Espera 30 segundos
        current_time = time.time()
        for instance_id in list(instances.keys()):
            if current_time - instance_timestamps[instance_id] > 30:
                del instances[instance_id]
                del instance_timestamps[instance_id]
                print(f"Instancia {instance_id} eliminada por inactividad.")

# Inicia el hilo de limpieza
cleanup_thread = threading.Thread(target=cleanup_instances, daemon=True)
cleanup_thread.start()

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    message = data.get('message')
    instance_id = data.get('instance_id')

    # Si se proporciona un ID de instancia, usa esa instancia, de lo contrario crea una nueva
    if instance_id in instances:
        ai = instances[instance_id]
        print(f"Usando la instancia existente: {instance_id}")
    else:
        ai = MetaAI()
        if instance_id == "":
            instance_id = str(len(instances) + 1)  # Generar un nuevo ID de instancia
        instances[instance_id] = ai
        instance_timestamps[instance_id] = time.time()
        print(f"Creada una nueva instancia: {instance_id}")

    # Actualiza el timestamp de la instancia
    instance_timestamps[instance_id] = time.time()
    
    print(f"Me ha llegado un mensaje: {message}")
    response = ai.prompt(message=message)
    print(f"Respuesta ha sido: {response['message']}")
    
    return jsonify({'response': response["message"], 'instance_id': instance_id})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2050, debug=True)