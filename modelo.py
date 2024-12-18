import os
import openai
from dotenv import load_dotenv, find_dotenv
import mysql.connector
from mysql.connector import Error

# Carga las variables de entorno del archivo .env
_ = load_dotenv(find_dotenv())

# Asigna la clave API desde las variables de entorno
openai.api_key = os.environ['OPENAI_API_KEY']

# Moderación en la API
def moderate_content(text):
    moderation_response = openai.Moderation.create(input=text)
    flagged = moderation_response["results"][0]["flagged"]
    return flagged

# Conexión base de datos
def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host="localhost", 
            user="root",     
            password=os.environ['DB_PASSWORD'],
            database=os.environ['DB'],
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None

# Consulta información del paciente y su historial clínico
def query_patient_history(tipo_documento, numero_documento):
    connection = connect_to_db()
    if not connection:
        return "No se pudo conectar a la base de datos.", None
    try:
        cursor = connection.cursor(dictionary=True)
        # Consulta información del paciente
        query_patient = """
        SELECT * 
        FROM Pacientes 
        WHERE TipoDocumento = %s AND NumeroDocumento = %s
        """
        cursor.execute(query_patient, (tipo_documento, numero_documento))
        patient = cursor.fetchone()
        
        if not patient:
            cursor.close()
            connection.close()
            return "No se encontró un paciente con ese tipo y número de documento.", None
        
        # Consulta historial clínico
        query_history = """
        SELECT AntecedentesPersonales, AntecedentesFamiliares, NotasGenerales
        FROM HistoriaClinica 
        WHERE ID_Paciente = %s
        """
        cursor.execute(query_history, (patient['ID_Paciente'],))
        history = cursor.fetchall()
        
        cursor.close()
        connection.close()
        return patient, history
    except Error as e:
        return f"Error al realizar la consulta: {e}", None

# Obtener respuesta del modelo
def get_completion_from_messages(messages, 
                                 model="gpt-3.5-turbo", 
                                 temperature=0, 
                                 max_tokens=100):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message["content"]

# Definición del mensaje del sistema
system_message = """
Eres un asistente inteligente especializado en medicina y bases de datos.
Proporcionas respuestas sobre los datos almacenados en el sistema hospitalario y ofreces información clara y precisa sobre temas médicos, 
ofreces consejos generales de salud y bienestar, explicas conceptos médicos, 
y respondes preguntas sobre enfermedades, síntomas, tratamientos y prevención. 
Siempre aclaras que tu consejo no sustituye la opinión de un médico profesional. 
Solo ofreces orientación y educación médica de forma responsable.
"""

# Función para validar la entrada del usuario (prevención de inyección de prompts)
def validate_user_input(user_message):
    forbidden_patterns = ["{", "}", "[", "]", "<", ">", ";", "/*", "*/", ":", "=", "(", ")"]
    for pattern in forbidden_patterns:
        if pattern in user_message.lower():
            return False  # Si encuentra un patrón prohibido, retorna False
    return True  # Si el mensaje es seguro, retorna True


while True:
    user_status = input("¿Eres un usuario registrado? Escribe 1 para Sí, 2 para No (o 'salir' para terminar): ")
    if user_status.lower() == 'salir':
        print("¡Hasta luego!")
        break
    
    if user_status == '1':
        # Solicitar tipo y número de documento
        tipo_documento = input("Escribe el tipo de documento (CC, TI, CE): ")
        numero_documento = int(input("Escribe el número de documento: "))

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

            # Generar un mensaje para el modelo basado en el historial
            history_summary = "El paciente no tiene enfermedades registradas."
            if history:
                diseases = [f"{h['AntecedentesFamiliares']} (Notas Generales: {h['NotasGenerales']}) (Antecedentes Familiares: {h['AntecedentesFamiliares']})" for h in history]
                history_summary = "Enfermedades registradas: " + "; ".join(diseases)

            # Construir mensaje para el asistente
            messages = [
                {'role': 'system', 'content': system_message},
                {'role': 'user', 'content': f"El paciente con tipo de documento {tipo_documento} y número {numero_documento} tiene los siguientes datos: {patient_info}. {history_summary}. Proporciona consejos personalizados basados en esta información y la consulta: {user_message}"}
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
