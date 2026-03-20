import psycopg2, os, random, time

print("Waiting for DB to be fully ready...")
time.sleep(5)

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"), port=os.getenv("DB_PORT", "5432"),
    dbname=os.getenv("POSTGRES_DB"), user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD")
)
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS patient_data (id SERIAL PRIMARY KEY, age INT, bmi FLOAT, blood_pressure INT, glucose FLOAT);")

for _ in range(1000):
    age = random.randint(18, 90)
    bmi = round(random.uniform(18.5, 40.0), 1)
    bp = random.randint(90, 180)
    glucose = round(random.uniform(70.0, 200.0), 1)
    cur.execute("INSERT INTO patient_data (age, bmi, blood_pressure, glucose) VALUES (%s, %s, %s, %s)", (age, bmi, bp, glucose))

conn.commit()
print("Patient data loaded successfully!")
cur.close()
conn.close()
