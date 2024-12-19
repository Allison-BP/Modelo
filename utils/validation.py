# Función para validar la entrada del usuario (prevención de inyección de prompts)
def validate_user_input(user_message):
    forbidden_patterns = ["{", "}", "[", "]", "<", ">", ";", "/*", "*/", ":", "=", "(", ")"]
    for pattern in forbidden_patterns:
        if pattern in user_message.lower():
            return False  # Si encuentra un patrón prohibido, retorna False
    return True  # Si el mensaje es seguro, retorna True
