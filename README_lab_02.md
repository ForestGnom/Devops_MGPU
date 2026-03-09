# Лабораторная работа №2. Упаковка многокомпонентного аналитического приложения с помощью Docker и Docker Compose

**Вариант 30** — Здравоохранение / Оценка удовлетворенности пациентов  
**Техническое задание** — Масштабирование: 2 реплики приложения и балансировщик Nginx

## Информация о студенте
- **ФИО:** Трухачев Никита Алексеевич
- **Группа:** БД-251м
- **Вариант:** 30 (Здравоохранение)

## Сруктура проекта: 
├── app

│   ├── dashboard.py

│   ├── Dockerfile

│   ├── loader.py

│   └── requirements.txt

├── data

│   └── healthcare_dataset.csv

├── docker-compose.yml

├── nginx

│   └── nginx.conf

## Скриншоты выполенения проекта:
## Создание Dockerfile
На данном этапе был создан оптимизированный Dockerfile с соблюдением всех best practices:
- Использован базовый образ `python:3.10-slim` (конкретная версия)
- Создан непривилегированный пользователь `appuser` с UID 1000
- Кэширование слоёв: `COPY requirements.txt` выполняется до копирования основного кода
- Очистка кэша после установки зависимостей
<img width="974" height="769" alt="image" src="https://github.com/user-attachments/assets/aa3f9d48-ec6e-4941-a278-f630e4f03180" />

## Создание файла .end c паролями и портами
Файл `.env` содержит чувствительные данные (пароли, имена пользователей, порты) и не должен попадать в репозиторий. В нём определены:
- `POSTGRES_DB=healthcare` — название базы данных
- `POSTGRES_USER=healthcare_user` — пользователь БД
- `POSTGRES_PASSWORD=healthcare_password` — пароль (в реальном проекте используется сложный пароль)
- `POSTGRES_HOST=db` — имя хоста (совпадает с именем сервиса в docker-compose)
- `POSTGRES_PORT=5432` — стандартный порт PostgreSQL
- `STREAMLIT_PORT=8501` — порт для Streamlit приложения
<img width="974" height="390" alt="image" src="https://github.com/user-attachments/assets/a8289b04-d44e-4192-bb80-aa936eb16859" />

## Создание файла docker-compose.yml
Основной файл оркестрации, описывающий все сервисы проекта:
- **db** — PostgreSQL 16-alpine с healthcheck
- **loader** — одноразовый ETL-контейнер для загрузки данных
- **app** — основное приложение с 2 репликами (согласно варианту 30)
- **nginx** — балансировщик нагрузки на порту 80

Ключевые настройки:
- `depends_on` с условиями `service_healthy` и `service_completed_successfully`
- Именованный том `postgres_data` для сохранения данных БД
- Сеть `backend-network` для изоляции сервисов
- Масштабирование `replicas: 2` для сервиса app
<img width="974" height="667" alt="image" src="https://github.com/user-attachments/assets/7df2bb27-de90-4442-afa4-157c813f3bb0" />

## Создание файла Nginx.conf для запуска 2-х реплик приложения (deploy: replicas: 2) и балансировщика 
Конфигурация Nginx обеспечивает распределение нагрузки между двумя репликами приложения:
- Upstream блок `streamlit_backend` содержит два сервера `app:8501`
- Проксирование всех запросов с порта 80 на реплики
- Настройка заголовков для корректной работы WebSocket (необходимо для Streamlit)
<img width="974" height="529" alt="image" src="https://github.com/user-attachments/assets/ca005b1a-de97-4dfe-884c-5b005e5c95c0" />

## Запуск Docker контейнеров
```bash
docker compose up -d --build
```
Выполняет:
- Сборку образов для сервисов app и loader
- Запуск всех контейнеров в фоновом режиме
- Автоматическое создание сети и томов
Процесс сборки включает установку зависимостей из requirements.txt и копирование исходного кода.
<img width="974" height="689" alt="image" src="https://github.com/user-attachments/assets/df83cee8-9700-4dff-a83a-44a2853cbc83" />
<img width="974" height="491" alt="image" src="https://github.com/user-attachments/assets/05df9249-2d6c-43fc-8d69-9384d99a2106" />

## Открытие приложения в браузере http://localhost:80:
Веб-интерфейс доступен по адресу http://localhost:80. Приложение состоит из двух вкладок:
Вкладка "Заполнить анкету" — форма для сбора данных об удовлетворенности пациентов:
- Поле для ввода ФИО
- Слайдер для оценки от 1 до 10
- Текстовое поле для комментария
- Кнопка отправки
<img width="974" height="389" alt="image" src="https://github.com/user-attachments/assets/6b409826-3374-4a39-84e7-92edf75b41d7" />
Вкладка "Результаты" — отображение собранных данных:
- Метрики: общее количество опрошенных, средняя оценка
- Таблица с результатами всех опросов
<img width="974" height="366" alt="image" src="https://github.com/user-attachments/assets/7919230f-0cb1-414d-98d6-596ac8e28295" />

## Проверка логов:
```bash
docker compose logs -f
```
Позволяет в реальном времени отслеживать работу всех контейнеров:
Логи загрузчика (loader):
- Успешное чтение 55501 записей из CSV-файла
- Завершение работы с кодом 0 (успешно)
<img width="974" height="788" alt="image" src="https://github.com/user-attachments/assets/95217912-91ba-4619-a81e-7152fc96752e" />
<img width="974" height="611" alt="image" src="https://github.com/user-attachments/assets/724e9999-0a67-4e42-b053-aab03f2fc890" />

## Завершение работы
```bash
# Остановка и удаление контейнеров (данные БД сохранятся в томе)
docker compose down

# Полная очистка (включая том с данными)
docker compose down -v
```
<img width="974" height="183" alt="image" src="https://github.com/user-attachments/assets/2eda105d-0062-4c53-ad23-e465067b4799" />
<img width="974" height="234" alt="image" src="https://github.com/user-attachments/assets/678930bc-c2f2-4b95-b4ce-515cb5edbcb7" />







