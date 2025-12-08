import google.generativeai as genai

genai.configure(api_key="AIzaSyA9wz0aUJSf7-cocsXAJT1fpKu9lAMb24k")

models = genai.list_models()

for m in models:
    print(m.name)
