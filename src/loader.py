"""
Загрузчик данных для Healthcare Dataset
ИЗМЕНЕНО: объединены изменения из dev и feature/data-loader (Kaggle API)
"""
import pandas as pd
Загрузчик данных для Healthcare Dataset
<<<<<<< HEAD
ИЗМЕНЕНО В ВЕТКЕ DEV: источник данных изменён на Kaggle API
=======
ИЗМЕНЕНО В ВЕТКЕ FEATURE/DATA-LOADER: загрузка из Kaggle API
""""""
Загрузчик данных для Healthcare Dataset
>>>>>>> feature/data-loader
"""
import pandas as pd

def load_data(file_path="data/healthcare_dataset.csv"):
    """Загружает данные о пациентах."""
    try:
        df = pd.read_csv(file_path)
        print(f"Загружено {len(df)} записей")
        print(f"Колонки: {list(df.columns)}")
        print(f"\nПервые 3 записи:")
        print(df.head(3))
        return df
    except FileNotFoundError:
        print(f"Файл {file_path} не найден")
        return None

if __name__ == "__main__":
    df = load_data()
    if df is not None:
        print(f"\nСтатистика:")
        print(f"Пациентов: {len(df)}")
        print(f"Заболевания: {df['Medical Condition'].value_counts().to_dict()}")
