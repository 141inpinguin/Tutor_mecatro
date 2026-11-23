import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

st.set_page_config(page_title="Tutor Mecatrónica IA", page_icon="⚙️", layout="centered")
st.title("⚙️ Evaluador y Tutor de Ingeniería Mecatrónica")

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"].strip())
STORE_ID = st.secrets["STORE_ID"].strip()

SYSTEM_PROMPT = """
Eres un profesor experto en Ingeniería Mecatrónica (control, electrónica, mecánica, robótica, termodinámica y programación).
Tu objetivo es evaluar y explicar preguntas de examen (teóricas y prácticas) con precisión absoluta.

Sigue este protocolo obligatorio en cada respuesta:
1. CLARIFICACIÓN: Si la pregunta o imagen está confusa o ambigua, empieza explicando qué concepto o cálculo está pidiendo realmente el reactivo.
2. FUNDAMENTACIÓN (RAG): Usa las fórmulas, teoremas o criterios extraídos de los libros adjuntos y cita el libro o concepto utilizado.
3. CÁLCULO VERIFICADO (PYTHON): Para cualquier ejercicio numérico, despeje, matriz, transformada o circuito, USA OBLIGATORIAMENTE la herramienta de ejecución de código Python para calcular el resultado exacto. Verifica siempre la coherencia de unidades (SI / Inglés) y conversiones (radianes vs grados).
4. EXPLICACIÓN PASO A PASO: Muestra el desarrollo claro desde la fórmula base hasta el resultado final. Si hay opciones múltiples, explica por qué la correcta es esa y cuál es el error típico detrás de las opciones incorrectas.
"""

imagen_subida = st.file_uploader("Sube una foto del diagrama, circuito o ejercicio (opcional)", type=["png", "jpg", "jpeg"])
pregunta = st.text_area("Escribe o pega aquí la pregunta del examen:", height=150)

if st.button("Evaluar y Explicar", type="primary"):
    if not pregunta and not imagen_subida:
        st.warning("Por favor escribe una pregunta o sube una imagen del ejercicio.")
    else:
        try:
            with st.spinner("Paso 1/2: Analizando ejercicio y consultando tus libros..."):
                texto_consulta = pregunta if pregunta.strip() else "Analiza el diagrama o ejercicio de esta imagen e identifica los conceptos, fórmulas y teoremas de ingeniería mecatrónica necesarios para resolverlo."
                
                contenido_paso1 = []
                if imagen_subida:
                    contenido_paso1.append(Image.open(imagen_subida))
                contenido_paso1.append(texto_consulta)

                # Paso 1: Consulta a los libros (RAG)
                resp_libros = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=contenido_paso1,
                    config=types.GenerateContentConfig(
                        system_instruction="Eres un asistente de investigación en Ingeniería Mecatrónica. Busca en los libros adjuntos las fórmulas exactas, definiciones, tablas o criterios aplicables al problema y cítalos fielmente.",
                        temperature=0.0,
                        tools=[
                            types.Tool(
                                file_search=types.FileSearch(
                                    file_search_store_names=[STORE_ID]
                                )
                            )
                        ]
                    )
                )

            with st.spinner("Paso 2/2: Resolviendo y verificando cálculos en Python..."):
                contenido_paso2 = []
                if imagen_subida:
                    contenido_paso2.append(Image.open(imagen_subida))
                contenido_paso2.append(
                    f"PROBLEMA DEL EXAMEN:\n{texto_consulta}\n\n"
                    f"INFORMACIÓN ENCONTRADA EN LOS LIBROS DEL CURSO:\n{resp_libros.text}\n\n"
                    f"Resuelve el problema siguiendo estrictamente el protocolo, usando Python para verificar todos los cálculos."
                )

                # Paso 2: Razonamiento profundo + Ejecución de Python
                resp_final = client.models.generate_content(
                    model="gemini-2.5-pro",
                    contents=contenido_paso2,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        temperature=0.0,
                        tools=[{"code_execution": {}}]
                    )
                )

                st.markdown("### 📝 Explicación Detallada")
                st.markdown(resp_final.text)

        except Exception as e:
            st.error(f"Detalle exacto del error de Google: {e}")
