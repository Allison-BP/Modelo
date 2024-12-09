import os
import openai
import tiktoken
from dotenv import load_dotenv, find_dotenv



# Carga las variables de entorno del archivo .env
_ = load_dotenv(find_dotenv())


# Asigna la clave API desde las variables de entorno
openai.api_key  = os.environ['OPENAI_API_KEY']

def get_completion_from_messages(messages, 
                                 model="gpt-3.5-turbo", 
                                 temperature=0, 
                                 max_tokens=500):
    
# Envía los messages a la API de OpenAI.
# La respuesta de la API se almacena en response.
# Devuelve solo el contenido de la respuesta (choices[0].message["content"]).

    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature, # this is the degree of randomness of the model's output
        max_tokens=max_tokens, # the maximum number of tokens the model can ouptut 
    )
    return response.choices[0].message["content"]

# 3. Definición del mensaje del sistema

delimiter = "####"
system_message = f"""
Se le proporcionarán consultas de servicio al cliente. \
La consulta de servicio al cliente estará delimitada con caracteres \
{delimiter}.
Clasifique cada consulta en una categoría principal \
y una categoría secundaria.
Proporcione su resultado en formato json con las claves \
: primaria y secundaria.

Categorías principales: Facturación, Soporte técnico, \
Administración de cuentas o Consulta general.

Categorías secundarias de facturación:
Cancelar suscripción o actualizar
Agregar un método de pago
Explicación del cargo
Disputar un cargo

Categorías secundarias de Soporte técnico:
Solución de problemas generales
Compatibilidad de dispositivos
Actualizaciones de software

Categorías secundarias de Administración de cuentas:
Restablecer contraseña
Actualizar información personal
Cerrar cuenta
Seguridad de la cuenta

Categorías secundarias de Consulta general:
Información del producto
Precios
Comentarios
Hable con un humano
"""

user_message = "Hola, crea mi factura, con mi nombre, Allison."

# Creación de la lista de mensajes
messages = [
    {'role': 'system', 'content': system_message},
    {'role': 'user', 'content': f"{delimiter}{user_message}{delimiter}"}
]

# Obtener la respuesta del modelo
response = get_completion_from_messages(messages)

# Imprimir la respuesta clasificada
print(response)