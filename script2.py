import streamlit as st
import json
import random
import time
import os
from datetime import datetime, timedelta
import altair as alt
import pandas as pd

# Configuración de página
st.set_page_config(
    page_title="PySpark Study Guide",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para mejorar la interfaz
def load_custom_css():
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #FF6B6B 0%, #4ECDC4 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .question-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #4ECDC4;
        margin: 1rem 0;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .progress-bar {
        background: #e9ecef;
        border-radius: 10px;
        overflow: hidden;
        height: 20px;
        margin: 1rem 0;
    }
    .progress-fill {
        background: linear-gradient(90deg, #4ECDC4 0%, #44A08D 100%);
        height: 100%;
        transition: width 0.3s ease;
    }
    .sidebar-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Cargar preguntas con manejo de errores
@st.cache_data
def load_questions(path='response.json'):
    """Carga preguntas del archivo JSON con manejo de errores"""
    try:
        #COMENTAR ESTAS LÍNEAS SI NO TIENES EL ARCHIVO response.json
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        else:
            return create_sample_questions()
        
        #USAR PREGUNTAS DE EJEMPLO PARA TESTING
        #return create_sample_questions()
        
    except (json.JSONDecodeError, FileNotFoundError) as e:
        st.error(f"Error cargando preguntas: {e}")
        return create_sample_questions()

def create_sample_questions():
    """Crea preguntas de ejemplo basadas en tu estructura real"""
    return [
        {
            "id": 1,
            "type": "multiple_choice",
            "question": "¿Cuál es la principal diferencia entre un RDD y un DataFrame en Spark?",
            "options": [
                "A. Los RDDs soportan SQL, los DataFrames no",
                "B. Los DataFrames tienen optimización a nivel de ejecución (Catalyst), los RDDs no",
                "C. Los RDDs son inmutables, los DataFrames no",
                "D. Los DataFrames no pueden agruparse"
            ],
            "answer": "B",
            "concept": "El optimizador Catalyst y el gestor de ejecución Tungsten permiten optimizaciones en DataFrames que no existen en RDDs."
        },
        {
            "id": "2a",
            "type": "coding",
            "question": "Dado un DataFrame `df`, escribe la instrucción de PySpark (una sola línea) para mostrar los primeros 10 registros.",
            "answer": "df.show(10)",
            "concept": "Las acciones en Spark como `show()` forzan la evaluación perezosa."
        },
        {
            "id": "2b",
            "type": "conceptual",
            "question": "Explica qué es lazy evaluation en Spark y menciona al menos dos beneficios.",
            "keywords": ["retarda", "transformaciones", "acción", "optimización", "planificación", "evita cálculos innecesarios"],
            "concept": "Lazy evaluation retrasa la ejecución de transformaciones hasta que se solicita un resultado (acción), permitiendo optimizar todo el pipeline y evitar cálculos redundantes."
        },
        {
            "id": 3,
            "type": "multiple_choice",
            "question": "¿Cuál de las siguientes NO es una transformación en Spark?",
            "options": [
                "A. filter()",
                "B. map()",
                "C. collect()",
                "D. groupBy()"
            ],
            "answer": "C",
            "concept": "collect() es una acción, no una transformación. Las transformaciones son lazy, las acciones fuerzan la ejecución."
        },
        {
            "id": 4,
            "type": "coding",
            "question": "Escribe el código para filtrar registros donde la columna 'age' sea mayor a 30 en un DataFrame llamado 'df'.",
            "answer": "df.filter(df.age > 30)",
            "concept": "El método filter() permite aplicar condiciones booleanas a los DataFrames."
        },
        {
            "id": 5,
            "type": "conceptual",
            "question": "¿Qué es el particionamiento en Spark y por qué es importante para el rendimiento?",
            "keywords": ["división", "datos", "paralelo", "nodos", "distribución", "rendimiento", "shuffle", "localidad"],
            "concept": "El particionamiento divide los datos en chunks que se procesan en paralelo, minimizando el movimiento de datos entre nodos."
        }
    ]

# Evaluar respuestas conceptuales mejorado
def evaluate_conceptual(response, keywords, threshold=0.3):
    """Evalúa respuestas conceptuales basado en palabras clave encontradas"""
    if not response or not keywords:
        return False
    
    response_lower = response.lower()
    matches = sum(1 for kw in keywords if kw.lower() in response_lower)
    
    # Mostrar información de debug en sidebar para ayudar al usuario
    if 'debug_mode' in st.session_state and st.session_state.debug_mode:
        st.sidebar.markdown(f"**🔍 Debug Info:**")
        st.sidebar.markdown(f"Palabras encontradas: {matches}/{len(keywords)}")
        st.sidebar.markdown(f"Palabras clave: {', '.join(keywords)}")
    
    # Criterio: al menos 30% de las palabras clave deben estar presentes
    score = matches / len(keywords)
    return score >= threshold

# Análisis de rendimiento
def analyze_performance(session_data):
    """Analiza el rendimiento del usuario"""
    if not session_data:
        return {}
    
    total_questions = len(session_data)
    correct_answers = sum(1 for q in session_data if q.get('correct', False))
    accuracy = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    
    # Análisis por categoría
    categories = {}
    difficulties = {}
    
    for q in session_data:
        cat = q.get('category', 'Unknown')
        diff = q.get('difficulty', 'medium')
        
        if cat not in categories:
            categories[cat] = {'total': 0, 'correct': 0}
        if diff not in difficulties:
            difficulties[diff] = {'total': 0, 'correct': 0}
            
        categories[cat]['total'] += 1
        difficulties[diff]['total'] += 1
        
        if q.get('correct', False):
            categories[cat]['correct'] += 1
            difficulties[diff]['correct'] += 1
    
    return {
        'accuracy': accuracy,
        'total_questions': total_questions,
        'correct_answers': correct_answers,
        'categories': categories,
        'difficulties': difficulties
    }

# Mostrar estadísticas con gráficos usando Altair
def show_performance_charts(performance_data):
    """Muestra gráficos de rendimiento usando Altair"""
    if not performance_data:
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Rendimiento por Categoría")
        if performance_data.get('categories'):
            cat_data = []
            for cat, data in performance_data['categories'].items():
                accuracy = (data['correct'] / data['total']) * 100 if data['total'] > 0 else 0
                cat_data.append({
                    'Categoría': cat, 
                    'Precisión (%)': accuracy, 
                    'Total': data['total']
                })
            
            if cat_data:
                df_cat = pd.DataFrame(cat_data)
                
                # Gráfico de barras con Altair
                chart = alt.Chart(df_cat).mark_bar().add_selection(
                    alt.selection_interval()
                ).encode(
                    x=alt.X('Categoría:N', title='Categoría'),
                    y=alt.Y('Precisión (%):Q', title='Precisión (%)', scale=alt.Scale(domain=[0, 100])),
                    color=alt.Color('Precisión (%):Q', 
                                  scale=alt.Scale(scheme='viridis'), 
                                  legend=alt.Legend(title="Precisión %")),
                    tooltip=['Categoría:N', 'Precisión (%):Q', 'Total:Q']
                ).properties(
                    width=300,
                    height=250,
                    title="Precisión por Categoría"
                ).interactive()
                
                st.altair_chart(chart, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Rendimiento por Dificultad")
        if performance_data.get('difficulties'):
            diff_data = []
            for diff, data in performance_data['difficulties'].items():
                accuracy = (data['correct'] / data['total']) * 100 if data['total'] > 0 else 0
                diff_data.append({
                    'Dificultad': diff.title(), 
                    'Precisión (%)': accuracy,
                    'Total': data['total']
                })
            
            if diff_data:
                df_diff = pd.DataFrame(diff_data)
                
                # Gráfico de dona/pie con Altair
                base = alt.Chart(df_diff).add_selection(
                    alt.selection_interval()
                )
                
                pie = base.mark_arc(innerRadius=50, outerRadius=90).encode(
                    theta=alt.Theta('Precisión (%):Q'),
                    color=alt.Color('Dificultad:N', 
                                  scale=alt.Scale(scheme='category10'),
                                  legend=alt.Legend(title="Dificultad")),
                    tooltip=['Dificultad:N', 'Precisión (%):Q', 'Total:Q']
                ).properties(
                    width=300,
                    height=250,
                    title="Distribución por Dificultad"
                ).resolve_scale(
                    color='independent'
                )
                
                st.altair_chart(pie, use_container_width=True)

# Inicializar estado de sesión
def initialize_session_state():
    """Inicializa todas las variables de estado de sesión"""
    defaults = {
        'started': False,
        'finished': False,
        'questions': [],
        'score': 0,
        'current': 0,
        'start_time': time.time(),
        'session_data': [],
        'study_mode': 'quiz',
        'show_hints': True,
        'difficulty_filter': 'all',
        'category_filter': 'all'
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Sidebar con configuraciones
def render_sidebar(total_questions):
    """Renderiza la barra lateral con configuraciones"""
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.header("⚙️ Configuración")
    
    # Número de preguntas
    max_q = len(total_questions)
    num_q = st.sidebar.number_input(
        "📝 Número de preguntas:", 
        min_value=1, 
        max_value=max_q, 
        value=min(10, max_q),
        help="Selecciona cuántas preguntas quieres en esta ronda"
    )
    
    # Opciones adicionales
    st.sidebar.markdown("---")
    show_hints = st.sidebar.checkbox("💡 Mostrar conceptos", value=True)
    
    # Modo debug para preguntas conceptuales
    debug_mode = st.sidebar.checkbox("🔍 Modo debug (conceptuales)", value=False, 
                                   help="Muestra información sobre evaluación de palabras clave")
    st.session_state.debug_mode = debug_mode
    
    study_mode = st.sidebar.selectbox(
        "📚 Modo de estudio:",
        ["quiz", "review", "timed"],
        help="Quiz: Evaluación normal, Review: Ver respuestas, Timed: Contrarreloj"
    )
    
    # Configuración para preguntas conceptuales
    st.sidebar.markdown("### 🎯 Evaluación Conceptual")
    threshold = st.sidebar.slider(
        "Umbral de palabras clave (%)",
        min_value=20,
        max_value=80,
        value=30,
        step=10,
        help="Porcentaje mínimo de palabras clave requeridas para respuestas conceptuales"
    ) / 100
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    return num_q, show_hints, study_mode, threshold

# Filtrar preguntas
def filter_questions(questions, category_filter, difficulty_filter):
    """Filtra preguntas según criterios seleccionados"""
    filtered = questions
    
    if category_filter != 'all':
        filtered = [q for q in filtered if q.get('category') == category_filter]
    
    if difficulty_filter != 'all':
        filtered = [q for q in filtered if q.get('difficulty') == difficulty_filter]
    
    return filtered

# Renderizar pregunta
def render_question(q, question_num, total_questions, show_hints):
    """Renderiza una pregunta individual"""
    st.markdown(f'<div class="question-card">', unsafe_allow_html=True)
    
    # Header de pregunta
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### 📋 Pregunta {question_num}/{total_questions}")
    with col2:
        # Mostrar tipo de pregunta
        type_emoji = {"multiple_choice": "🔘", "coding": "💻", "conceptual": "🧠"}
        st.markdown(f"**Tipo:** {type_emoji.get(q.get('type', 'conceptual'), '❓')} {q.get('type', 'conceptual').replace('_', ' ').title()}")
    
    st.markdown(f"**{q['question']}**")
    
    # Mostrar concepto si está habilitado
    if show_hints and q.get('concept'):
        with st.expander("💡 Concepto relacionado"):
            st.info(q['concept'])
    
    # Mostrar palabras clave para preguntas conceptuales (solo en modo debug)
    if q['type'] == 'conceptual' and q.get('keywords') and st.session_state.get('debug_mode', False):
        with st.expander("🔍 Palabras clave (modo debug)"):
            st.write(f"**Palabras clave esperadas:** {', '.join(q['keywords'])}")
            st.write(f"**Umbral actual:** {st.session_state.get('threshold', 0.3)*100:.0f}%")
    
    user_answer = None
    submit_button = False
    
    # Renderizar según tipo de pregunta
    if q['type'] == 'multiple_choice':
        user_answer = st.radio(
            "Selecciona tu respuesta:",
            q['options'],
            key=f"opt_{st.session_state.current}"
        )
        submit_button = st.button("✅ Enviar Respuesta", key=f"submit_{st.session_state.current}")
        if submit_button:
            user_answer = user_answer[0] if user_answer else None
            
    elif q['type'] == 'coding':
        user_answer = st.text_area(
            "Escribe tu código:",
            height=100,
            key=f"code_{st.session_state.current}",
            help="Escribe una línea de código PySpark"
        )
        submit_button = st.button("✅ Enviar Código", key=f"submit_{st.session_state.current}")
        
    else:  # conceptual
        user_answer = st.text_area(
            "Explica tu respuesta:",
            height=120,
            key=f"concept_{st.session_state.current}",
            help="Incluye las palabras clave relevantes en tu explicación"
        )
        submit_button = st.button("✅ Enviar Explicación", key=f"submit_{st.session_state.current}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    return user_answer, submit_button

# Procesar respuesta
def process_answer(q, user_answer, threshold=0.3):
    """Procesa y evalúa la respuesta del usuario"""
    if not user_answer:
        return False, "⚠️ Por favor proporciona una respuesta"
    
    correct = False
    feedback = ""
    
    if q['type'] == 'multiple_choice':
        correct = user_answer.upper() == q['answer'].upper()
        # Encontrar la opción correcta completa
        correct_option = next((opt for opt in q['options'] if opt.startswith(q['answer'])), q['answer'])
        feedback = f"**Respuesta correcta:** {correct_option}"
        
    elif q['type'] == 'coding':
        # Evaluación más flexible para código
        user_clean = user_answer.strip().replace(' ', '').lower()
        answer_clean = q['answer'].strip().replace(' ', '').lower()
        # Verificar coincidencia exacta o si la respuesta esperada está contenida
        correct = user_clean == answer_clean or answer_clean in user_clean
        feedback = f"**Respuesta esperada:** `{q['answer']}`"
        
    else:  # conceptual
        correct = evaluate_conceptual(user_answer, q.get('keywords', []), threshold)
        keywords_found = sum(1 for kw in q.get('keywords', []) if kw.lower() in user_answer.lower())
        total_keywords = len(q.get('keywords', []))
        feedback = f"**Palabras clave encontradas:** {keywords_found}/{total_keywords} ({keywords_found/total_keywords*100:.0f}%)"
        if not correct:
            feedback += f"\n**Palabras clave esperadas:** {', '.join(q.get('keywords', []))}"
    
    return correct, feedback

# Aplicación principal
def main():
    # Cargar CSS personalizado
    load_custom_css()
    
    # Inicializar estado
    initialize_session_state()
    
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>⚡ PySpark Study Guide</h1>
        <p>Prepárate para tu entrevista técnica con ejercicios interactivos</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Cargar preguntas
    total_questions = load_questions()
    
    if not total_questions:
        st.error("❌ No se pudieron cargar las preguntas. Usando preguntas de ejemplo.")
        return
    
    # Sidebar
    num_q, show_hints, study_mode, threshold = render_sidebar(total_questions)
    
    # Actualizar configuraciones en session state
    st.session_state.show_hints = show_hints
    st.session_state.study_mode = study_mode
    st.session_state.threshold = threshold
    
    # Para esta versión, no filtramos por categoría/dificultad ya que no están en la estructura original
    filtered_questions = total_questions
    
    if not filtered_questions:
        st.warning("⚠️ No hay preguntas que coincidan con los filtros seleccionados.")
        return
    
    # Mostrar estadísticas en sidebar
    if st.session_state.started:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📊 Progreso Actual")
        
        progress = (st.session_state.current / len(st.session_state.questions)) * 100
        st.sidebar.markdown(f"""
        <div class="stat-card">
            <h4>Puntuación: {st.session_state.score}/{len(st.session_state.questions)}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        elapsed = int(time.time() - st.session_state.start_time)
        minutes, seconds = divmod(elapsed, 60)
        st.sidebar.markdown(f"⏱️ Tiempo: {minutes:02d}:{seconds:02d}")
        
        st.sidebar.progress(progress / 100)
        st.sidebar.text(f"Pregunta {st.session_state.current + 1} de {len(st.session_state.questions)}")
    
    # Botones de control en sidebar
    st.sidebar.markdown("---")
    col1, col2 = st.sidebar.columns(2)
    
    # Botón principal
    if not st.session_state.started:
        if st.button("🚀 Iniciar Cuestionario", type="primary"):
            selected_questions = random.sample(filtered_questions, min(num_q, len(filtered_questions)))
            st.session_state.started = True
            st.session_state.finished = False
            st.session_state.questions = selected_questions
            st.session_state.score = 0
            st.session_state.current = 0
            st.session_state.start_time = time.time()
            st.session_state.session_data = []
            st.rerun()
    
    # Controles adicionales
    if st.session_state.started and not st.session_state.finished:
        if st.sidebar.button("⏹️ Finalizar Cuestionario"):
            st.session_state.finished = True
            st.rerun()
    
    if st.sidebar.button("🔄 Reiniciar Todo"):
        for key in ['started', 'finished', 'questions', 'score', 'current', 'start_time', 'session_data']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    
    # Contenido principal
    if st.session_state.started and not st.session_state.finished:
        # Verificar si se acabaron las preguntas
        if st.session_state.current >= len(st.session_state.questions):
            st.session_state.finished = True
            st.rerun()
        else:
            # Mostrar pregunta actual
            q = st.session_state.questions[st.session_state.current]
            user_answer, submit_button = render_question(
                q, 
                st.session_state.current + 1, 
                len(st.session_state.questions),
                st.session_state.show_hints
            )
            
            # Procesar envío
            if submit_button and user_answer:
                threshold = st.session_state.get('threshold', 0.3)
                correct, feedback = process_answer(q, user_answer, threshold)
                
                # Guardar datos de sesión
                session_record = {
                    'question': q['question'],
                    'user_answer': user_answer,
                    'correct': correct,
                    'category': q.get('category', 'Unknown'),
                    'difficulty': q.get('difficulty', 'medium'),
                    'type': q['type']
                }
                st.session_state.session_data.append(session_record)
                
                # Mostrar feedback
                if correct:
                    st.success("🎉 ¡Correcto! Excelente trabajo.")
                    st.session_state.score += 1
                else:
                    st.error("❌ Respuesta incorrecta. ¡Sigue intentando!")
                
                if feedback:
                    st.info(f"💡 {feedback}")
                
                if q.get('concept'):
                    st.markdown(f"**📚 Concepto:** {q['concept']}")
                
                # Avanzar automáticamente después de 3 segundos
                time.sleep(1)
                st.session_state.current += 1
                st.rerun()
    
    # Pantalla de resultados
    elif st.session_state.finished:
        st.markdown("## 🎊 ¡Cuestionario Completado!")
        
        # Estadísticas principales
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <h3>📊 Puntuación Final</h3>
                <h2>{st.session_state.score}/{len(st.session_state.questions)}</h2>
                <p>{(st.session_state.score/len(st.session_state.questions)*100):.1f}% de precisión</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            elapsed = int(time.time() - st.session_state.start_time)
            minutes, seconds = divmod(elapsed, 60)
            st.markdown(f"""
            <div class="stat-card">
                <h3>⏱️ Tiempo Total</h3>
                <h2>{minutes:02d}:{seconds:02d}</h2>
                <p>{elapsed/len(st.session_state.questions):.1f}s por pregunta</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            grade = "🥇 Excelente" if st.session_state.score/len(st.session_state.questions) >= 0.8 else \
                   "🥈 Muy Bien" if st.session_state.score/len(st.session_state.questions) >= 0.6 else \
                   "🥉 Bien" if st.session_state.score/len(st.session_state.questions) >= 0.4 else "📚 Sigue Estudiando"
            
            st.markdown(f"""
            <div class="stat-card">
                <h3>🏆 Evaluación</h3>
                <h2>{grade}</h2>
                <p>¡Sigue practicando!</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Análisis detallado
        if st.session_state.session_data:
            performance_data = analyze_performance(st.session_state.session_data)
            show_performance_charts(performance_data)
        
        # Recomendaciones
        st.markdown("### 💡 Recomendaciones para Mejorar")
        if st.session_state.score/len(st.session_state.questions) < 0.6:
            st.warning("""
            📚 **Sugerencias de estudio:**
            - Revisa los conceptos fundamentales de PySpark
            - Practica más ejercicios de programación
            - Estudia la documentación oficial de Spark
            """)
        else:
            st.success("""
            🎯 **¡Buen trabajo!**
            - Continúa practicando con preguntas más difíciles
            - Explora casos de uso avanzados
            - Prepárate para preguntas de optimización
            """)
        
        # Botón para nuevo cuestionario
        if st.button("🔄 Nuevo Cuestionario", type="primary"):
            for key in ['started', 'finished', 'questions', 'score', 'current', 'start_time', 'session_data']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    else:
        # Pantalla de inicio
        st.markdown("### 🎯 ¿Listo para comenzar?")
        st.info(f"""
        📋 **Preguntas disponibles:** {len(filtered_questions)}
        🔘 **Opción múltiple:** {sum(1 for q in filtered_questions if q.get('type') == 'multiple_choice')}
        💻 **Programación:** {sum(1 for q in filtered_questions if q.get('type') == 'coding')}
        🧠 **Conceptuales:** {sum(1 for q in filtered_questions if q.get('type') == 'conceptual')}
        """)
        
        # Preview de tipos de preguntas
        if filtered_questions:
            st.markdown("### 📚 Tipos de Preguntas Disponibles")
            question_types = {}
            for q in filtered_questions:
                qtype = q.get('type', 'unknown')
                if qtype not in question_types:
                    question_types[qtype] = 0
                question_types[qtype] += 1
            
            cols = st.columns(min(3, len(question_types)))
            type_emoji = {"multiple_choice": "🔘", "coding": "💻", "conceptual": "🧠"}
            
            for i, (qtype, count) in enumerate(question_types.items()):
                with cols[i % len(cols)]:
                    emoji = type_emoji.get(qtype, '❓')
                    display_name = qtype.replace('_', ' ').title()
                    st.metric(f"{emoji} {display_name}", f"{count} preguntas")

if __name__ == '__main__':
    main()
