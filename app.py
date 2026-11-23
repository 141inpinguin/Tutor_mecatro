import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

st.set_page_config(page_title="Tutor Mecatrónica IA", page_icon="⚙️", layout="centered")
st.title("⚙️ Evaluador y Tutor de Ingeniería Mecatrónica")

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
STORE_ID = st.secrets["STORE_ID"]

SYSTEM_PROMPT = """
Eres un profesor experto en Ingeniería Mecatrónica (control, electrónica, mecánica, robótica, termodinámica y programación).
Tu objetivo es evaluar y explicar preguntas de examen (teóricas y prácticas) con precisión absoluta.

Sigue este protocolo obligatorio en cada respuesta:
1. CLARIFICACIÓN: Si la pregunta está redactada de forma confusa o ambigua, empieza explicando qué concepto o cálculo está pidiendo realmente el reactivo.
2. FUNDAMENTACIÓN (RAG): Busca las fórmulas, teoremas o criterios en los libros adjuntos y cita el libro o concepto utilizado. No inventes teoría fuera del material.
3. CÁLCULO VERIFICADO (PYTHON): Para cualquier ejercicio numérico, despeje, matriz, transformada o circuito, USA OBLIGATORIAMENTE la herramienta de ejecución de código Python para calcular el resultado exacto. Verifica siempre la coherencia de unidades (SI / Inglés) y conversiones (radianes vs grados).
4. EXPLICACIÓN PASO A PASO: Muestra el desarrollo claro desde la fórmula base hasta el resultado final. Si hay opciones múltiples, explica por qué la correcta es esa y cuál es el error típico detrás de las opciones incorrectas.
"""

imagen_subida = st.file_uploader("Sube una foto del diagrama, circuito o ejercicio (opcional)", type=["png", "jpg", "jpeg"])
pregunta = st.text_area("Escribe o pega aquí la pregunta del examen:", height=150)

if st.button("Evaluar y Explicar", type="primary"):
    if not pregunta and not imagen_subida:
        st.warning("Por favor escribe una pregunta o sube una imagen del ejercicio.")
    else:
        with st.spinner("Consultando libros y verificando cálculos en Python..."):
            contenido = []
            if imagen_subida:
                contenido.append(Image.open(imagen_subida))
            if pregunta:
                contenido.append(pregunta)

            response = client.models.generate_content(
                model="gemini-2.5-pro",
                contents=contenido,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.0,
                    tools=[
                        types.Tool(
                            file_search=types.FileSearch(
                                file_search_store_names=[STORE_ID]
                            )
                        ),
                        {"code_execution": {}}
                    ]
                )
            )
            
            st.markdown("### 📝 Explicación Detallada")
            st.markdown(response.text)
