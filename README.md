# 🍅 Tomato Lives Matter - ML-powered Agricultural Assistant

## 📋 Оглавление
- [Бизнес-цель проекта](#бизнес-цель-проекта)
- [Целевые метрики для продакшена](#целевые-метрики-для-продакшена)
- [Набор данных](#набор-данных)
- [План экспериментов](#план-экспериментов)
- [Архитектура системы](#архитектура-системы)
- [Установка и запуск](#установка-и-запуск)
- [Использование API](#использование-api)
- [Структура проекта](#структура-проекта)

---

## 🎯 Бизнес-цель проекта

Автоматизация процессов диагностики и мониторинга состояния сельскохозяйственных культур для повышения эффективности работы агрономов и фермеров через:
 
 Квартальные цели (не боимся, все бесплатное или работает или не даже не запуститься)
1. **Автоматическую детекцию растений** на фотографиях с полей
2. **Диагностику болезней растений** на ранних стадиях
3. **Интеграцию с Telegram-ботами** для удобного взаимодействия с фермером
Цели на год (после получения аудитории из Sims)
4. **Общение через Telegram-ботам** для взаимодействия инфры с клиентом
5. **Управление задачами и календарем** сельскохозяйственных работ

### Целевая аудитория:
- **Фермеры из Sims 4** 
- **Люди из симуляторов фермера**

### Ожидаемый эффект:
- Выявление болезней растений
- Подсчет количества урожая в пикселях
---

## 📊 Целевые метрики для продакшена

### Performance Metrics (Производительность)

| Метрика | Целевое значение | Критическое значение |
|---------|------------------|---------------------|
| **Среднее время отклика API** | ≤ 1000 мс | ≤ 10000 мс |
| **Время инференса модели (детекция)** | ≤ 1000 мс | ≤ 10000 мс |
| **Время инференса модели (болезни)** | ≤ 1000 мс | ≤ 1000 мс |
| **Throughput** | ≥ 10 req/sec | ≥ 5 req/sec |

### Reliability Metrics (Надежность)

| Метрика | Целевое значение | Критическое значение |
|---------|------------------|---------------------|
| **Доля неуспешных запросов** | ≤5% | ≤ 10% |

### Resource Metrics (Ресурсы)

| Метрика | Целевое значение | Критическое значение |
|---------|------------------|---------------------|
| **Использование RAM** | ≤ 10 GB | ≤ 32 GB |
| **GPU Memory (опционально)** | ≤ 5 GB | ≤ 15 GB |

### ML Model Quality Metrics (Качество моделей)

#### Детекция растений (YOLOv8)
| Метрика | Томаты | Капуста | Критическое значение |
|---------|--------|---------|---------------------|
| **mAP@0.5** | ≥ 0.7 | ≥ 0.7 | ≥ 0.5 |
| **Precision** | ≥ 0.7 | ≥ 0.7 | ≥ 0.5 |
| **Recall** | ≥ 0.7 | ≥ 0.7 | ≥ 0.5 |

#### Классификация болезней томатов (ResNet50)
| Метрика | Целевое значение | Критическое значение |
|---------|------------------|---------------------|
| **Accuracy** | ≥ 0.9| ≥ 0.8 |
| **F1-Score (macro avg)** | ≥ 0.9 | ≥ 0.8 |
| **Precision (macro avg)** | ≥ 0.9 | ≥ 0.8 |
| **Recall (macro avg)** | ≥ 0.9 | ≥ 0.8 |
| **AUC-ROC** | ≥ 0.9 | ≥ 0.9 |

### Business Metrics (Бизнес-метрики)

| Метрика | Целевое значение |
|---------|------------------|
| **User satisfaction (Telegram bot rating)** | ≥ 4.5/5.0 |
| **Average response time to farmer** | ≤ 5 минут |
| **Task completion rate** | ≥ 50% |

---

## Набор данных

### 1. Детекция растений (Object Detection & Segmentation)

#### Томаты
- **Размер датасета**: Custom dataset
- **Классы**: `tomato`
- **Формат аннотаций**: YOLO format (txt files)
- **Размер изображений**: 640x640 px

#### Капуста
- **Размер датасета**: Custom dataset
- **Классы**: `cabbage`
- **Формат аннотаций**: YOLO format
- **Размер изображений**: 416x416 px

**Источники данных**: 
- Roboflow

### 2. Классификация болезней томатов (Disease Classification)

- **Задача**: Multi-label binary classification
- **Количество классов**: 7 бинарных классов болезней листьев томатов
- **Архитектура**: ResNet50 (Transfer Learning)
- **Размер изображений**: 224x224 px (standard ResNet input)
- **Предобработка**: ImageNet normalization

**Классы болезней**:
1. Bacterial Spot
2. Early Blight
3. Late Blight
4. Leaf Mold
5. Septoria Leaf Spot
6. Spider Mites
7. Target Spot
8. Healthy (контрольный класс)

**Dataset source**: [Dropbox link](https://www.dropbox.com/scl/fo/3plo5qmx1o2sq7rrvds2c/h?rlkey=eupcg0up7ezxasdaabs4ywole&dl=1)


---

## 🔬 План экспериментов

### Phase 1: Baseline Models (In Progress 🔄))

#### Эксперимент 1.1: Object Detection - Томаты
- [x] **Модель**: YOLOv8m-seg
- [x] **Размер изображения**: 640x640

#### Эксперимент 1.2: Object Detection - Капуста
- [x] **Модель**: YOLOv8n-seg
- [x] **Размер изображения**: 416x416

#### Эксперимент 1.3: Disease Classification
- [x] **Модель**: ResNet50 (pretrained on ImageNet)
- [x] **Task**: 7-class binary classification
- [x] **Logging**: W&B (Weights & Biases)
- [x] **Metrics**: Precision, Recall, AUC, F1-Score

**Результаты baseline**: Документированы в `tomato_detected_training.ipynb` и `tomato_diseases.ipynb`

---

### Phase 2: Model Optimization (Planned 📅)

#### Эксперимент 2.1: Гиперпараметры для детекции
**Цель**: Улучшение mAP на 2-3% при сохранении скорости инференса

#### Эксперимент 2.3: Улучшение классификации болезней
**Цель**: Достичь Accuracy ≥ 0.92

---

### Phase 3: Production Optimization (Planned 📅)

#### Эксперимент 3.1: Model Compression & Quantization
**Цель**: Уменьшить latency на 30-40% без потери качества

- [ ] **Post-Training Quantization**:
  - INT8 quantization (ONNX/TensorRT)
  - Dynamic quantization (PyTorch)
  - Float16 precision


---

### Phase 4: MLOps & Monitoring (Planned 📅)


#### Эксперимент 4.2: Continuous Training Pipeline
**Цель**: Автоматическое переобучение на новых данных


#### Эксперимент 4.3: A/B Testing Framework
**Цель**: Безопасное внедрение новых версий моделей


---

## 🏗️ Архитектура системы

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface Layer                      │
├─────────────────────┬───────────────────────┬───────────────────┤
│  Farmer Telegram Bot│ Agronomist Bot (агро) │  Review Bot       │
│  (@farm_bot)        │  (@agro_bot)          │  (@review_bot)    │
└──────────┬──────────┴───────────┬───────────┴──────────┬────────┘
           │                      │                       │
           └──────────────────────┼───────────────────────┘
                                  │
                    ┌─────────────▼──────────────┐
                    │   FastAPI ML Service       │
                    │   (devops/app/app.py)      │
                    │                            │
                    │  - OAuth2 Authentication   │
                    │  - File Upload Endpoint    │
                    │  - Model Routing           │
                    └─────────────┬──────────────┘
                                  │
                    ┌─────────────▼──────────────┐
                    │   ML Model Layer           │
                    │   (devops/ml/model.py)     │
                    ├────────────────────────────┤
                    │  YOLOv8m-seg (Tomato)     │
                    │  YOLOv8n-seg (Cabbage)    │
                    │  ResNet50 (Disease)       │
                    └─────────────┬──────────────┘
                                  │
                    ┌─────────────▼──────────────┐
                    │   Data Storage Layer       │
                    ├────────────────────────────┤
                    │  Firebase Firestore        │
                    │  - User data               │
                    │  - Task calendar           │
                    │  - Chat history            │
                    │  - Problem tracking        │
                    │                            │
                    │  Firebase Storage          │
                    │  - Uploaded images         │
                    │  - Model predictions       │
                    └────────────────────────────┘
```

### Компоненты системы:

1. **FastAPI ML Service** (`devops/`)
   - REST API для ML-инференса
   - OAuth2 аутентификация
   - Поддержка двух задач: `detect`, `disease`
   - Роутинг между моделями

2. **Telegram Bots**:
   - **Farm Bot** - интерфейс для фермеров

3. **ML Models**:
   - YOLOv8 Segmentation для детекции
   - ResNet50 для классификации болезней

4. **Database**:
   - Firebase Firestore (NoSQL)
   - Firebase Storage (файлы)

---

## 🚀 Установка и запуск

### Требования
```
Python 3.10+
Docker & Docker Compose
CUDA 11.8+ (опционально, для GPU)
```

### Локальная установка

#### 1. Клонирование репозитория
```bash
git clone https://github.com/yourusername/tomato-lives-matter.git
cd tomato-lives-matter
```

#### 2. ML Service (FastAPI)
```bash
cd devops
pip install -r requirements.txt

# Загрузка весов моделей (убедитесь, что файлы .pt находятся в ml/)
# - yolov8m-seg-tomato.pt
# - yolov8n-seg-cabbage.pt

# Запуск сервера
python -m app.app
# или через uvicorn
uvicorn app.app:app --host 0.0.0.0 --port 8000 --reload
```

#### 3. Telegram Bots

**Farm Bot:**
```bash
cd farm
pip install -r requirements.txt

# Настройка конфигурации
# Добавьте BOT_TOKEN в config.py
# Добавьте serviceAccountKey.json для Firebase

python main.py
```
### Docker Compose

```bash
# Запуск всех сервисов
docker-compose -f devops/compose-dev.yaml up -d

# Логи
docker-compose logs -f

# Остановка
docker-compose down
```

---

## Использование API

### Authentication

```bash
# Получение токена
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=assert"

# Response:
# {
#   "access_token": "admin",
#   "token_type": "bearer"
# }
```

### Endpoints

#### 1. Health Check
```bash
GET /
Response: {"message": "Welcome to Agrlink!"}
```

#### 2. API Info
```bash
GET /readme
Response: {
  "task": "detect or disease",
  "plant": "tomato or cabbage"
}
```

#### 3. Upload Image for Inference

**Детекция томатов:**
```bash
curl -X POST "http://localhost:8000/file/upload-file?task=detect&plant=tomato" \
  -H "Authorization: Bearer admin" \
  -F "file=@/path/to/tomato.jpg"
```

**Response:**
```json
{
  "request": {
    "task": "detect",
    "plant": "tomato"
  },
  "result": [
    {
      "name": "tomato",
      "class": 0,
      "confidence": "94%",
      "box": {
        "x1": 125.3,
        "x2": 340.7,
        "y1": 89.2,
        "y2": 298.5
      }
    }
  ]
}
```

**Детекция капусты:**
```bash
curl -X POST "http://localhost:8000/file/upload-file?task=detect&plant=cabbage" \
  -H "Authorization: Bearer admin" \
  -F "file=@/path/to/cabbage.jpg"
```

**Диагностика болезней:**
```bash
curl -X POST "http://localhost:8000/file/upload-file?task=disease&plant=tomato" \
  -H "Authorization: Bearer admin" \
  -F "file=@/path/to/diseased_leaf.jpg"
```

### Python Client Example

```python
import requests
from pathlib import Path

# Аутентификация
auth_response = requests.post(
    "http://localhost:8000/token",
    data={"username": "admin", "password": "assert"}
)
token = auth_response.json()["access_token"]

# Загрузка изображения
headers = {"Authorization": f"Bearer {token}"}
files = {"file": open("tomato.jpg", "rb")}
params = {"task": "detect", "plant": "tomato"}

response = requests.post(
    "http://localhost:8000/file/upload-file",
    headers=headers,
    files=files,
    params=params
)

print(response.json())
```

---

## Структура проекта

```
tomato_lives_matter/
├── README.md                          # Этот файл
├── .gitignore                         # Git ignore файл
│
├── devops/                            # ML Service (FastAPI)
│   ├── app/
│   │   ├── __init__.py
│   │   └── app.py                     # FastAPI приложение
│   ├── ml/
│   │   ├── model.py                   # ML inference логика
│   │   ├── args-yolov8m-seg-tomato.yaml
│   │   ├── args-yolov8m-seg-cabbage.yaml
│   │   ├── yolov8m-seg-tomato.pt     # Веса модели (не в git)
│   │   └── yolov8n-seg-cabbage.pt    # Веса модели (не в git)
│   ├── Dockerfile
│   ├── compose-dev.yaml
│   ├── config.yaml                    # Конфигурация моделей
│   ├── requirements.txt
│   ├── setup.py
│   ├── tomato.jpg                     # Тестовые изображения
│   └── cabbage.jpg
│
├── farm/                              # Telegram Bot для фермеров
│   ├── firebase/                      # Firebase интеграция
│   │   ├── firebase.py
│   │   ├── firebase_config.yaml
│   │   ├── firebase_config_cron.yaml
│   │   ├── requirements_firebase.txt
│   │   └── serviceAccountKey.json    # (не в git)
│   ├── main.py                        # Entry point
│   ├── router.py                      # Message routing
│   ├── handlers.py                    # Message handlers
│   ├── states.py                      # FSM states
│   ├── config.py                      # Bot token
│   ├── kb.py                          # Keyboards
│   ├── text.py                        # Text templates
│   ├── text_message.py                # Message formatting
│   ├── notification.py                # Notifications & Cron
│   ├── crop_calendar.py               # Calendar handlers
│   ├── add_record.py                  # Add record flow
│   ├── new_problem.py                 # New problem flow
│   ├── exciting_problem.py            # Existing problems
│   ├── rating_grade.py                # Feedback system
│   ├── collection_editer.py           # Firebase utils
│   ├── bd_and_DataFrame.py            # Data processing
│   ├── pagination_info.py             # Pagination logic
│   ├── check_datetime.py              # Date validation
│   ├── check_farmer.py                # User verification
│   ├── farmer2agronom.py              # Mapping logic
│   ├── count_message.py               # Message counter
│   ├── command_menu.py                # Bot menu
│   ├── restart.py                     # Restart handler
│   ├── Dockerfile
│   ├── requirements.txt
│   └── Readme.md
│
├── agro_bot/                          # Telegram Bot для агрономов
│   ├── main.py
│   ├── router.py
│   ├── config.py
│   ├── chat_handler.py                # Chat functionality
│   ├── event_registry.py              # Event registration
│   ├── event_details.py               # Event details view
│   ├── event_modifier.py              # Event modification
│   ├── event_remover.py               # Event removal
│   ├── command_menu.py
│   ├── notification.py
│   ├── pagination_info.py
│   ├── pagination_kb.py
│   ├── states.py
│   ├── text_message.py
│   ├── unauthorized_handler.py
│   ├── restart.py
│   ├── serviceAccountKey.json        # (не в git)
│   ├── requirements.txt
│   └── Readme.md
│
├── review/                            # Telegram Bot для проверки
│   ├── firebase/
│   │   ├── firebase.py
│   │   ├── firebase_config.yaml
│   │   ├── firebase_config_cron.yaml
│   │   ├── requirements_firebase.txt
│   │   └── serviceAccountKey.json    # (не в git)
│   ├── main.py
│   ├── router.py
│   ├── handlers.py
│   ├── states.py
│   ├── config.py
│   ├── kb_df.py                       # Keyboard builders
│   ├── text.py
│   ├── text_message.py
│   ├── notification.py
│   ├── calendar_swipe.py              # Calendar navigation
│   ├── respond.py                     # Response handlers
│   ├── confirm.py                     # Confirmation flow
│   ├── refusal.py                     # Refusal flow
│   ├── collection_editer.py
│   ├── pagination_info.py
│   ├── check_agronomist.py            # User verification
│   ├── command_menu.py
│   ├── restart.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── Readme.md
│
├── tomato_detected_training.ipynb     # Обучение детекции
├── tomato_detected_inference.ipynb    # Инференс детекции
└── tomato_diseases.ipynb              # Обучение классификации болезней
```

