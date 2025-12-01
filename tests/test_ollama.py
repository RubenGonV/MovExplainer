import ollama

client = ollama.Client()
model = "mistral"

prompt = "Hola, ¿puedes decirme qué día es hoy?"
resp = client.generate(model=model, prompt=prompt)

print("Respuesta del modelo:")
print(resp.response)
