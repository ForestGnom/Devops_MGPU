"""
Streamlit Dashboard для Healthcare Dataset
"""
import streamlit as st
import pandas as pd
import plotly.express as px

# Настройка страницы
st.set_page_config(page_title="Healthcare Dashboard", layout="wide")
st.title("Healthcare Analytics Dashboard")

# Загрузка данных
@st.cache_data
def load_data():
    df = pd.read_csv("data/healthcare_dataset.csv")
    return df

df = load_data()

# Боковая панель с фильтрами
st.sidebar.header("Фильтры")
gender = st.sidebar.multiselect("Пол", df['Gender'].unique(), default=df['Gender'].unique())
condition = st.sidebar.multiselect("Заболевание", df['Medical Condition'].unique(), default=df['Medical Condition'].unique())

# Фильтрация данных
filtered_df = df[df['Gender'].isin(gender) & df['Medical Condition'].isin(condition)]

# Метрики
col1, col2, col3, col4 = st.columns(4)
col1.metric("Всего пациентов", len(filtered_df))
col2.metric("Средний возраст", f"{filtered_df['Age'].mean():.1f}")
col3.metric("Средний счет", f"${filtered_df['Billing Amount'].mean():,.0f}")
col4.metric("Уникальных врачей", filtered_df['Doctor'].nunique())

# Графики
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Распределение по заболеваниям")
    fig = px.pie(filtered_df, names='Medical Condition', title='')
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("Средний счет по заболеваниям")
    billing = filtered_df.groupby('Medical Condition')['Billing Amount'].mean().reset_index()
    fig = px.bar(billing, x='Medical Condition', y='Billing Amount', title='')
    st.plotly_chart(fig, use_container_width=True)

# Таблица с данными
st.subheader("Данные пациентов")
st.dataframe(filtered_df[['Name', 'Age', 'Gender', 'Medical Condition', 'Billing Amount']].head(100))
