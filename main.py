import os
import openai
from dotenv import load_dotenv, find_dotenv
from mysql.connector import Error
from openai_utils.assistant import get_completion_from_messages
from openai_utils.moderation import moderate_content
from utils.validation import validate_user_input
from database.queries import query_patient_history


# Carga las variables de entorno del archivo .env
_ = load_dotenv(find_dotenv())
openai.api_key = os.environ['OPENAI_API_KEY']

# Prompt asistente

system_message = """
Eres un asistente inteligente especializado en medicina y bases de datos.
Proporcionas respuestas sobre los datos almacenados en el sistema hospitalario y ofreces información clara y precisa sobre temas médicos, 
ofreces consejos generales de salud y bienestar, explicas conceptos médicos, 
y respondes preguntas sobre enfermedades, síntomas, tratamientos y prevención. 
Siempre aclaras que tu consejo no sustituye la opinión de un médico profesional. 
Solo ofreces orientación y educación médica de forma responsable.
Cuando respondas, por favor proporciona tu razonamiento paso a paso para llegar a la conclusión.
"""

def main():
    while True:
        user_status = input("¿Eres un usuario registrado? Escribe 1 para Sí, 2 para No (o 'salir' para terminar): ")
        if user_status.lower() == 'salir':
            print("¡Hasta luego!")
            break

        if user_status == '1':
            # Solicitar tipo y número de documento
            tipo_documento = input("Escribe el tipo de documento (CC, TI, CE): ")
            try:
                numero_documento = int(input("Escribe el número de documento: "))
            except ValueError:
                print("El número de documento debe ser un valor numérico.")
                continue

            # Consultar información del paciente
            patient_info, history = query_patient_history(tipo_documento, numero_documento)
            if isinstance(patient_info, str):
                print("\nResultado:")
                print(patient_info)
                continue

            print("\n¡Información validada! Ahora puedes realizar consultas.")

            while True:
                user_message = input("Escribe tu consulta o 'volver' para regresar al menú principal: ")
                if user_message.lower() == 'volver':
                    break

                if not validate_user_input(user_message):
                    print("Tu consulta contiene caracteres no permitidos. Por favor, modifícala.")
                    continue

                # Generar un mensaje para el modelo basado en el historial
                history_summary = "El paciente no tiene enfermedades registradas."
                if history:
                    diseases = [
                        f"AntecedentesPersonales: {h['AntecedentesPersonales']}, "
                        f"AntecedentesFamiliares: {h['AntecedentesFamiliares']}, "
                        f"NotasGenerales: {h['NotasGenerales']}"
                        for h in history
                    ]
                    history_summary = "Enfermedades registradas: " + "; ".join(diseases)

                # Construir mensaje para el asistente
                messages = [
                    {'role': 'system', 'content': system_message},
                    {'role': 'user', 'content': f"El paciente con tipo de documento {tipo_documento} y número {numero_documento} tiene los siguientes datos: {patient_info}. {history_summary}. Proporciona consejos personalizados basados en esta información y la consulta: {user_message}. Recuerda detallar tu razonamiento paso a paso."}
                ]

                response = get_completion_from_messages(messages)
                if moderate_content(response):
                    print("La respuesta generada contiene contenido inapropiado. Intenta una consulta diferente.")
                    continue

                print("\nAsistente:")
                print(response)

        elif user_status == '2':
            print("\nPuedes realizar consultas generales.")
            while True:
                user_message = input("Escribe tu consulta o 'volver' para regresar al menú principal: ")
                if user_message.lower() == 'volver':
                    break

                if not validate_user_input(user_message):
                    print("Tu consulta contiene caracteres no permitidos. Por favor, modifícala.")
                    continue

                if moderate_content(user_message):
                    print("Tu consulta contiene lenguaje inapropiado. Por favor, modifícala.")
                    continue

                # Consultas generales
                messages = [
                    {'role': 'system', 'content': system_message},
                    {'role': 'user', 'content': user_message}
                ]
                response = get_completion_from_messages(messages)
                print("\nAsistente:")
                print(response)
        else:
            print("Opción no válida. Intenta nuevamente.")

if __name__ == "__main__":
    main()