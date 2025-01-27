from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Cargar el modelo entrenado y el tokenizador
model = GPT2LMHeadModel.from_pretrained('./results')
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')

# Probar el modelo con una palabra
def generar_respuesta(texto):
    input_ids = tokenizer.encode(texto, return_tensors='pt')
    outputs = model.generate(input_ids, max_length=50, num_return_sequences=1)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# Probar con una palabra peligrosa
respuesta = generar_respuesta("bullying")
print(respuesta)
