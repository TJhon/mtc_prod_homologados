from google import genai
from pydantic import BaseModel, Field
from dotenv import find_dotenv, load_dotenv
import os
import json

load_dotenv(find_dotenv())
api_free = os.environ.get('GEM_API')
MODEL = "gemini-2.0-flash" 

# Definir el modelo Pydantic
class ProductInfo(BaseModel):
    modelo_codigo: str = Field(description="Código del modelo del dispositivo")
    nombre_comercial: str = Field(description="Nombre comercial del producto, puede ser None y el null reemplaza por None")
    porcentaje_seguridad: float = Field(ge=0, le=100, description="Porcentaje de confianza de la respuesta, puede ser 0 y el maximo es 100, es decir en porcentaje")

def obtener_info_producto_from_text_analysis(brand, model, text_result):
    client = genai.Client(api_key=api_free)
    prompt = f"""
    Analiza el siguiente código de modelo de celular: la marca es {brand} y el modelo es {model} mediante un analisis de texto a las url y title de un buscador y obtuve la el TEXTO RESULTANTE.

    TEXTO RESULTANTE:
    {text_result}
    
    Responde ÚNICAMENTE con un objeto JSON válido (sin markdown, sin explicaciones adicionales) con esta estructura exacta, si hay mas de 1 modelo entonces coloca None y el porcentaje que sea 0:

    {{
        "modelo_codigo": "{brand} {model}",
        "nombre_comercial": "nombre del producto",
        "porcentaje_seguridad": porcentaje_seguridad
    }}
    """

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )
        # Limpiar la respuesta por si viene con markdown
    text = response.text.strip()
    if text.startswith("```json"):
        text = text.replace("```json", "").replace("```", "").strip()
    elif text.startswith("```"):
        text = text.replace("```", "").strip()
    
    # Parsear JSON y crear objeto Pydantic
    data = json.loads(text)
    return ProductInfo(**data)

def obtener_info_producto(modelo_codigo: str, model: str = "gemini-2.5-flash") -> ProductInfo:
    client = genai.Client(api_key=api_free)
    
    # Crear el prompt con instrucciones para JSON
    prompt = f"""
    Analiza el siguiente código de modelo de celular: '{modelo_codigo}' no trates de rellenar la informacion con datos ficticios si no estas seguro solo coloca 'None' y el porcentaje deberia ser 0.
    
    Responde ÚNICAMENTE con un objeto JSON válido (sin markdown, sin explicaciones adicionales) con esta estructura exacta, y usa una estructura rapidamente transformable a un diccionario de python: 

    {{
        "modelo_codigo": "{modelo_codigo}",
        "nombre_comercial": "nombre del producto",
        "porcentaje_seguridad": porcentaje_seguridad
    }}
    """
    
    response = client.models.generate_content(
        model=model,
        contents=prompt
    )
    
    # Limpiar la respuesta por si viene con markdown
    text = response.text.strip()
    print(text)
    if text.startswith("```json"):
        text = text.replace("```json", "").replace("```", "").strip()
    elif text.startswith("```"):
        text = text.replace("```", "").strip()
    
    # Parsear JSON y crear objeto Pydantic
    data = json.loads(text)
    return ProductInfo(**data)


# Ejemplo de uso
if __name__ == "__main__":
    # Puedes pasar el modelo como parámetro

    
    resultado = obtener_info_producto('xiaomi mdz-28-aa', model=MODEL)
    
    # Acceder como objeto
    # print("=== Acceso como objeto ===")
    print(f"Nombre comercial: {resultado.nombre_comercial}")
    print(f"Seguridad: {resultado.porcentaje_seguridad}%")
    
    # result = SearchEngine(brand='xiaomi', model='mdz-28-aa').run()

    resultado = obtener_info_producto_from_text_analysis('xiaomi', 'mdz-28-aa', text_result='xiaomi box tv s gen mdz 28 aa 2nd 4k ultra hd android black')
    print(resultado)
