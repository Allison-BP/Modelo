import openai

def moderate_content(text):
    moderation_response = openai.Moderation.create(input=text)
    flagged = moderation_response["results"][0]["flagged"]
    return flagged