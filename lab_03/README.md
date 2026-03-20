# Лабораторная работа 3. Развертывание простого приложения в Kubernetes.

**Выполнил:** Трухачев Никита Алексеевич 

**Группа:** БД251-м

**Вариант:** 30 (Здравоохранение / Patient Dashboard)  

**Техническое задание (K8s Specific):** Реализовать HPA (Horizontal Pod Autoscaler) манифест (CPU target 50%).

---

## 1. Цель работы
Получить практические навыки оркестрации контейнеризированных приложений в среде Kubernetes. Выполнить миграцию архитектуры из Docker Compose в K8s, настроить управление конфигурациями (ConfigMaps/Secrets), обеспечить персистентность данных (PVC), настроить проверки жизнеспособности (Probes) и реализовать горизонтальное автомасштабирование (HPA).

---

## 2. Технический стек и окружение
- **ОС:** Ubuntu 24.04 LTS
- **Контейнеризация:** Docker
- **Оркестрация:** Minikube (Driver: Docker), Kubernetes (kubectl)
- **База данных:** PostgreSQL 15 (Alpine)
- **Аналитическая среда:** Jupyter Notebook (scipy-notebook)
- **Библиотеки:** `psycopg2-binary`, `pandas`, `seaborn`, `matplotlib`, `sqlalchemy`

---

## 3. Архитектура решения
```mermaid
graph TD
    %% Определение цветов
    classDef config fill:#f9f9f9,stroke:#333,stroke-width:1px;
    classDef db fill:#e1f5fe,stroke:#0277bd,stroke-width:2px;
    classDef app fill:#fff3e0,stroke:#ef6c00,stroke-width:2px;
    classDef batch fill:#f1f8e9,stroke:#558b2f,stroke-width:2px;
    classDef autoscale fill:#fce4ec,stroke:#c2185b,stroke-width:2px;
    classDef user fill:#ffebee,stroke:#c62828,stroke-width:2px;

    subgraph K8s_Cluster ["K8s Cluster (Minikube)"]
        
        subgraph Configs ["Конфигурация"]
            SEC["Secret<br/>db-secret"]
            CM["ConfigMap<br/>app-config"]
            PVC["PersistentVolumeClaim<br/>postgres-pvc"]
        end

        subgraph Database ["Слой данных"]
            DB_POD("PostgreSQL Pod<br/>db-deployment")
            DB_SVC{"DB Service<br/>ClusterIP:5432"}
        end

        subgraph Analytics ["Слой аналитики"]
            HPA["HorizontalPodAutoscaler<br/>CPU target: 50%"]
            APP_POD1("Jupyter Pod 1")
            APP_POD2("Jupyter Pod 2")
            APP_POD3("Jupyter Pod 3")
            APP_SVC{"App Service<br/>NodePort:30088"}
        end

        subgraph Data ["Загрузка данных"]
            JOB("Loader Job<br/>data-loader-job")
        end

        %% Связи конфигурации
        SEC -.-> DB_POD:::config
        SEC -.-> APP_POD1:::config
        SEC -.-> APP_POD2:::config
        SEC -.-> APP_POD3:::config
        CM -.-> DB_POD:::config
        CM -.-> APP_POD1:::config
        CM -.-> APP_POD2:::config
        CM -.-> APP_POD3:::config
        PVC --- DB_POD:::db

        %% Связи БД
        DB_POD --- DB_SVC:::db
        DB_SVC --- JOB
        DB_SVC --- APP_POD1
        DB_SVC --- APP_POD2
        DB_SVC --- APP_POD3

        %% HPA управляет масштабированием
        HPA -->|scale up/down| APP_POD1
        HPA -->|scale up/down| APP_POD2
        HPA -->|scale up/down| APP_POD3

        %% Загрузка данных
        JOB -->|Writes data| DB_SVC:::batch

        %% Доступ к приложению
        APP_POD1 --- APP_SVC:::app
        APP_POD2 --- APP_SVC:::app
        APP_POD3 --- APP_SVC:::app
    end

    %% Внешний пользователь
    User(("Аналитик<br/>(Patient Dashboard)")) -->|Port 30088| APP_SVC:::user

    %% Применение стилей
    class SEC,CM,PVC config;
    class DB_POD,DB_SVC db;
    class APP_POD1,APP_POD2,APP_POD3,APP_SVC app;
    class JOB batch;
    class HPA autoscale;
    class User user;
```

## 4. Выполнение работы

### Этап 1. Подготовка кластера и образов

#### Запуск Minikube
```bash
minikube start --driver=docker
minikube status
```
<img width="974" height="703" alt="image" src="https://github.com/user-attachments/assets/4dd1bcc8-f246-4906-80fa-8244cc50ce65" />

#### Настройка окружения
```bash
eval $(minikube docker-env)
kubectl get nodes
```

#### Включение metrics-server для HPA
```bash
minikube addons enable metrics-server
kubectl get pods -n kube-system | grep metrics-server
```
<img width="974" height="388" alt="image" src="https://github.com/user-attachments/assets/f2874873-6673-456d-841a-fcadd193b2ab" />

#### Исходный код Docker-образов (Локальная сборка)
<img width="974" height="594" alt="image" src="https://github.com/user-attachments/assets/343d2fa2-c785-4af7-9af5-70db2bad9faf" />
<img width="974" height="495" alt="image" src="https://github.com/user-attachments/assets/f2b33d78-80bd-40e7-8739-d49ecee6fe25" />
<img width="974" height="270" alt="image" src="https://github.com/user-attachments/assets/8b2b7cd5-2d81-4ca8-85a8-dce90ecd097f" />


#### Сборка Docker-образов
```bash
docker build -t healthcare-app:v1 ./app
docker build -t healthcare-loader:v1 ./loader
```
<img width="974" height="594" alt="image" src="https://github.com/user-attachments/assets/a807dfb9-42b6-4a9a-8681-7b1eba534503" />
<img width="974" height="549" alt="image" src="https://github.com/user-attachments/assets/803570ff-580f-49ce-9bbc-2a24657e9947" />

### Этап 2. Управление конфигурацией и данными
#### Создание манифестов
**01-config.yaml (Secret + ConfigMap + PVC)**
<img width="974" height="618" alt="image" src="https://github.com/user-attachments/assets/840982e1-8308-4bfe-8b19-c3ce87ae5051" />

**02-db.yaml (Deployment + Service для БД)**
<img width="974" height="681" alt="image" src="https://github.com/user-attachments/assets/838d597e-198e-4563-a65d-71315386631d" />

**03-app.yaml (Deployment для приложения)**
<img width="974" height="605" alt="image" src="https://github.com/user-attachments/assets/db4b5f8d-ea80-446f-ae5e-9aec239bacb7" />

**04-service.yaml (Service для приложения)**
<img width="974" height="356" alt="image" src="https://github.com/user-attachments/assets/3df3348f-864b-4552-b2be-d6ffa0de1a77" />

**05-hpa.yaml (HPA - специфика варианта 30)**
<img width="974" height="356" alt="image" src="https://github.com/user-attachments/assets/755a7e24-32cd-40c9-bc12-41ada3df05b6" />

**06-job.yaml (Job для загрузки данных)**
<img width="974" height="482" alt="image" src="https://github.com/user-attachments/assets/f0d7f0ab-1e9c-4e46-b637-4814699eadd0" />

#### Применение манифестов
```bash
kubectl apply -f 01-config.yaml
kubectl apply -f 02-db.yaml
kubectl apply -f 03-app.yaml
kubectl apply -f 04-service.yaml
kubectl apply -f 05-hpa.yaml
kubectl apply -f 06-job.yaml
```
### Этап 3. Проверка работы компонентов
#### Доступ к приложению (Jupyter)

```bash
minikube service app-service --url
kubectl logs deployment/app-deployment | grep token
```
<img width="974" height="510" alt="image" src="https://github.com/user-attachments/assets/222b7d1e-1448-4d68-ae8a-8e98b45929e0" />

#### Выполнение аналитики в Jupyter
<img width="974" height="533" alt="image" src="https://github.com/user-attachments/assets/8d5a916c-9225-40f1-8c4b-109f87298488" />
<img width="974" height="431" alt="image" src="https://github.com/user-attachments/assets/eb3cb59f-499a-422c-bb19-fd9034f46c98" />

#### Результаты аналитики
<img width="974" height="550" alt="image" src="https://github.com/user-attachments/assets/1a4fb149-49bd-4057-85ed-59cd8ceb3e0c" />
<img width="974" height="544" alt="image" src="https://github.com/user-attachments/assets/1f893a26-4d46-483c-933e-9bf3bbd49e3b" />

## 4. Выводы
В ходе выполнения лабораторной работы были получены практические навыки оркестрации контейнеризированных приложений в среде Kubernetes. Выполнена миграция архитектуры из Docker Compose в K8s с реализацией следующих компонентов:
- Управление конфигурацией: Secret для хранения паролей (base64), ConfigMap для несекретных настроек
- Персистентное хранение: PVC для базы данных с подтверждением сохранности данных
- Жизненный цикл: InitContainer для проверки доступности БД, Liveness и Readiness Probes
- Специфика варианта 30: HorizontalPodAutoscaler с целевой загрузкой CPU 50%
- Загрузка данных: Job, который успешно загрузил 1000 тестовых записей
- Аналитика: Jupyter Notebook с визуализацией данных пациентов
Все компоненты успешно развернуты и функционируют в кластере Minikube.

