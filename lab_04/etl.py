import os
import random
import time

def load_data():
    """Симуляция загрузки данных пациентов"""
    data = [{"patient_id": i, "blood_pressure": random.randint(90, 180), 
             "glucose": random.uniform(70, 200), "age": random.randint(18, 90)} 
            for i in range(100)]
    return data

def process_data(data):
    """Симуляция обработки данных"""
    processed = []
    for row in data:
        row["risk_score"] = (row["blood_pressure"] / 100) + (row["glucose"] / 200)
        processed.append(row)
    return processed

if __name__ == "__main__":
    print("Starting ETL process...")
    raw_data = load_data()
    print(f"Loaded {len(raw_data)} records")
    processed_data = process_data(raw_data)
    print(f"Processed {len(processed_data)} records")
    print("ETL completed successfully!")
