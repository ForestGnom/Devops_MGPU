"""
Web-опросник для оценки удовлетворенности пациентов (упрощенная версия)
Вариант 30: Здравоохранение
"""
import streamlit as st
import pandas as pd
from datetime import datetime

# Настройка страницы
st.set_page_config(page_title="Опросник пациентов", layout="wide")
st.title("Здравоохранение - Оценка удовлетворенности пациентов")

# Инициализация данных
if 'responses' not in st.session_state:
    st.session_state.responses = []

# Две вкладки
tab1, tab2 = st.tabs(["Заполнить анкету", "Результаты"])

# Вкладка 1: Анкета
with tab1:
    st.header("Анкета пациента")
    
    with st.form("patient_form"):
        name = st.text_input("ФИО пациента")
        satisfaction = st.slider("Оценка удовлетворенности (1-10)", 1, 10, 8)
        comment = st.text_area("Комментарий")
        
        submitted = st.form_submit_button("Отправить")
        
        if submitted:
            st.session_state.responses.append({
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'name': name,
                'satisfaction': satisfaction,
                'comment': comment
            })
            st.success("Спасибо за участие в опросе!")

# Вкладка 2: Результаты
with tab2:
    st.header("Результаты опросов")
    
    if len(st.session_state.responses) == 0:
        st.info("Нет данных. Заполните анкету.")
    else:
        df = pd.DataFrame(st.session_state.responses)
        st.metric("Всего опрошенных", len(df))
        st.metric("Средняя оценка", f"{df['satisfaction'].mean():.1f}/10")
        st.dataframe(df)
