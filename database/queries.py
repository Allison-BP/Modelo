from .connection import connect_to_db

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

