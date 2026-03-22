# Лабораторная работа 4. Автоматизация ETL-скрипта с помощью CI/CD.

**Выполнил:** Трухачев Никита Алексеевич 

**Группа:** БД251-м

**Вариант:** 30 (Здравоохранение)  
**Техническое задание:** 	Запустить контейнер, сделать curl localhost:port/health. Если 200 OK — успех.

---

## 1. Цель работы
Настроить автоматический конвейер (Pipeline) непрерывной интеграции для ETL-компонента. Научиться обеспечивать качество кода и автоматическую сборку Docker-образов при каждом изменении в репозитории с помощью Jenkins.

---

## 2. Технический стек и окружение
- **ОС:** Ubuntu 24.04 LTS
- **Контейнеризация:** Docker
- **CI/CD инструмент:** Jenkins (запущенный в Docker)
- **Язык:** Python 3.10
- **Тестирование:** Smoke Test (health check)

---

## 3. Архитектура решения

```mermaid
graph TD
    classDef jenkins fill:#e1f5fe,stroke:#0277bd,stroke-width:2px;
    classDef docker fill:#fff3e0,stroke:#ef6c00,stroke-width:2px;
    classDef test fill:#f1f8e9,stroke:#558b2f,stroke-width:2px;

    subgraph Local_Environment ["Локальная среда"]
        GIT["Git Repository<br/>~/lab_04"]
        JENKINS["Jenkins Server<br/>http://localhost:8080"]
        DOCKER["Docker Daemon"]
    end

    subgraph Pipeline ["CI Pipeline"]
        CHECKOUT["Stage: Checkout<br/>Проверка файлов"]
        BUILD["Stage: Build Image<br/>docker build"]
        SMOKE["Stage: Smoke Test<br/>curl /health"]
        CLEANUP["Post: Clean Up<br/>docker rm/rmi"]
    end

    GIT -->|SCM| JENKINS
    JENKINS -->|выполняет| CHECKOUT
    CHECKOUT --> BUILD
    BUILD -->|docker build| DOCKER
    BUILD --> SMOKE
    SMOKE -->|curl http://localhost/health| TEST
    SMOKE --> CLEANUP

    class JENKINS,GIT jenkins;
    class DOCKER docker;
    class CHECKOUT,BUILD,SMOKE,CLEANUP test;
```
## 4. Выполнение работы

### 4.1 Запуск Jenkins в Docker
Для развертывания CI/CD сервера был использован Jenkins в контейнере Docker.
Создан файл docker-compose.yml с пробросом Docker-сокета хоста, что позволяет Jenkins выполнять команды Docker изнутри контейнера. 
После запуска контейнера был получен первичный пароль администратора, установлены рекомендованные плагины и создан учетная запись администратора. 
Jenkins стал доступен по адресу http://localhost:8080.

**Создание docker-compose.yml:**
<img width="974" height="335" alt="image" src="https://github.com/user-attachments/assets/9995f95d-4808-406d-94ea-8b8ad5521ea0" />

**Запуск Jenkins и получение пароля администратора:**
<img width="974" height="335" alt="image" src="https://github.com/user-attachments/assets/fa4d931b-70df-40fd-ad14-f51f675ea163" />
<img width="974" height="544" alt="image" src="https://github.com/user-attachments/assets/7052bead-535d-43b9-8abf-b97480489337" />
<img width="974" height="646" alt="image" src="https://github.com/user-attachments/assets/e4c8c04a-da3c-48b0-9ea6-69eda1dcde5c" />

### 4.2 Структура Git-репозитория
В локальном репозитории ~/lab_04 размещены файлы проекта: ETL-скрипт (etl.py), HTTP-сервер с эндпоинтом /health (health_server.py), 
инструкция для сборки Docker-образа (Dockerfile), зависимости Python (requirements.txt) и основной файл пайплайна (Jenkinsfile).
Все файлы были добавлены в Git и закоммичены.

**Создание проекта:**
<img width="906" height="400" alt="image" src="https://github.com/user-attachments/assets/3a7465d0-9119-47db-a6e0-f73ebc2246d8" />

**Файлы проекта:**

etl.py - ETL-скрипт обработки данных пациентов
<img width="974" height="482" alt="image" src="https://github.com/user-attachments/assets/3cd10955-9283-4001-b5a7-137b6daba9de" />

health_server.py - HTTP-сервер с эндпоинтом /health
<img width="974" height="515" alt="image" src="https://github.com/user-attachments/assets/e3879c1f-a2fd-4a90-a23a-c6d0421ff4a1" />

Dockerfile - Инструкция для сборки образа
<img width="974" height="363" alt="image" src="https://github.com/user-attachments/assets/b63a7fda-64bc-40f5-b51c-7340979c128a" />

Jenkinsfile - Описание CI/CD пайплайна
<img width="974" height="653" alt="image" src="https://github.com/user-attachments/assets/b06582f6-638a-4b2b-af19-6e8dea25e258" />
<img width="974" height="658" alt="image" src="https://github.com/user-attachments/assets/ae16a97f-5707-41c5-a345-3af839a08477" />

### 4.3 Jenkinsfile (Pipeline Script)
Файл Jenkinsfile описывает Declarative Pipeline, состоящий из трех основных стадий: проверка файлов в workspace, 
сборка Docker-образа с тегом healthcare-etl:${BUILD_NUMBER} и smoke test с проверкой доступности эндпоинта /health. 
В блоке post реализована обязательная очистка ресурсов (остановка и удаление контейнера, удаление образа) после завершения пайплайна независимо от результата.
<img width="974" height="548" alt="image" src="https://github.com/user-attachments/assets/cdd62a16-95d3-4569-885d-4531d92ab4f8" />
<img width="974" height="478" alt="image" src="https://github.com/user-attachments/assets/9233cdbf-cca1-4334-8b2a-319ef0f98482" />

### 4.4 Создание Jenkins Job
В веб-интерфейсе Jenkins была создана задача (Job) типа Pipeline с именем healthcare-etl-pipeline. 
В настройках задачи выбран тип "Pipeline script", в поле Script вставлено содержимое Jenkinsfile. 
После сохранения конфигурации Job стала доступна для ручного запуска через интерфейс Jenkins.
**Параметры Job:**
- Имя: healthcare-etl-pipeline
- Тип: Pipeline
- Definition: Pipeline script (вставлен код из 4.3)
<img width="974" height="493" alt="image" src="https://github.com/user-attachments/assets/59ccfc94-6195-42c1-994f-c835e03f9eb0" />

### 4.5 Демонстрация Quality Gate (Smoke Test)
Для демонстрации работы Quality Gate были выполнены два запуска пайплайна. 
Первый — успешный, при котором контейнер был запущен, эндпоинт /health вернул ожидаемый ответ "healthy", и пайплайн завершился с зеленым статусом. 
Второй — провальный, при котором проверка выполнялась на несуществующий эндпоинт /health_bad, что привело к ошибке и красному статусу сборки. 
Это подтверждает корректную работу smoke test как Quality Gate.

#### 4.5.1 Успешный запуск
Пайплайн выполнил все стадии, smoke test прошел успешно.
<img width="974" height="807" alt="image" src="https://github.com/user-attachments/assets/e73da921-4ebb-4e8d-8537-62e5cfa2a204" />
<img width="980" height="770" alt="image" src="https://github.com/user-attachments/assets/36ec6e4e-9014-4560-bbab-a11bb6fb9436" />

Согласно техническому заданию варианта 30, в качестве Quality Gate был реализован Smoke Test — проверка работоспособности контейнера после сборки.

**Алгоритм проверки:**
1. Запуск контейнера в фоновом режиме: docker run -d --name health-test -p 8083:80 healthcare-etl:${BUILD_NUMBER}
2. Ожидание старта сервиса: sleep 3
3. Выполнение HTTP-запроса к эндпоинту /health: curl -s http://localhost/health
4. Проверка ответа: если в ответе содержится строка "healthy" (что соответствует HTTP 200 OK), тест считается пройденным

**Результаты проверки:**
- Успешный запуск (сборка №12): эндпоинт /health доступен, контейнер отвечает статусом 200 OK, пайплайн завершается с зеленым статусом


#### 4.5.2 Провальный запуск (демонстрация Quality Gate)
Для демонстрации работы Quality Gate был изменен эндпоинт с /health на /health_bad. Пайплайн упал на стадии Smoke Test.
Изменение пайплайна:
<img width="953" height="574" alt="image" src="https://github.com/user-attachments/assets/9ad4839e-2a7e-47de-b990-692a74ea32a3" />
<img width="993" height="590" alt="image" src="https://github.com/user-attachments/assets/2ec31b3e-eba4-4be8-8df1-451b5f889087" />

Вывод ошибки в консоли: 
<img width="966" height="777" alt="image" src="https://github.com/user-attachments/assets/ac40d389-742a-461d-95e2-6863cb986199" />

**Результаты проверки:**
- Провальный запуск (сборка №13): эндпоинт /health_bad не существует, проверка завершается с ошибкой, пайплайн падает


### 4.6 Сборка Docker-образа
В процессе выполнения пайплайна на стадии Build Docker Image был собран Docker-образ на основе официального образа nginx:alpine. 
В образ был добавлен файл /health с содержимым {"status":"healthy"}. 
После успешной сборки образ с тегом healthcare-etl:${BUILD_NUMBER} отображался в списке локальных Docker-образов, что подтверждает корректность конфигурации сборки.

**Лог сборки:**
<img width="252" height="109" alt="image" src="https://github.com/user-attachments/assets/6d4cecc9-d377-46b0-b0cc-b5e660cb28b0" />

**Образ виден в системе**
<img width="1072" height="118" alt="image" src="https://github.com/user-attachments/assets/dc3c6436-8191-4d8e-854b-c91ef59879cc" />

## 6. Выводы
В ходе выполнения лабораторной работы был настроен автоматический конвейер CI/CD с использованием Jenkins в Docker. Реализованы следующие компоненты:
1. Jenkins сервер — запущен локально, доступен через веб-интерфейс
2. Pipeline — содержит 3 стадии:
  - Проверка файлов в workspace
  - Сборка Docker-образа
  - Smoke Test (health check)
3. Quality Gate — проверка /health эндпоинта; при недоступности пайплайн завершается с ошибкой
4. Очистка ресурсов — после каждого запуска контейнеры и образы удаляются
