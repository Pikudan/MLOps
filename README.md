# 🍅 Tomato Lives Matter - ML-powered Agricultural Assistant

## 📋 Оглавление
- [Бизнес-цель проекта](#бизнес-цель-проекта)
- [Целевые метрики для продакшена](#целевые-метрики-для-продакшена)
- [DVC: Версионирование данных](#dvc-версионирование-данных)
- [MLflow: Трекинг экспериментов](#mlflow-трекинг-экспериментов)
- [Docker: Инференс](#docker-инференс)
- [Набор данных](#набор-данных)
- [План экспериментов](#план-экспериментов)
- [Архитектура системы](#архитектура-системы)
- [Установка и запуск](#установка-и-запуск)
- [Использование API](#использование-api)
- [Структура проекта](#структура-проекта)
- [Обучение модели](#обучение-модели)
- [Тесты и CI/CD](#тесты-и-cicd)
- [YOLO Детекция](#yolo-детекция)

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

## 📦 DVC: Версионирование данных

Проект использует [DVC (Data Version Control)](https://dvc.org/) для версионирования данных и моделей.

### Где лежат данные/модели

| Тип | Путь | Описание |
|-----|------|----------|
| **Датасет** | `training/classification/datasets/tomato/` | 6436 изображений болезней томатов |
| **Модели** | `training/models/tomato/` | Обученные веса SimpleCNN |
| **DVC файлы** | `*.dvc` | Ссылки на версионированные данные |
| **Remote** | Google Drive / локальный | Удалённое хранилище данных |

### Быстрый старт

```bash
# Клонирование и восстановление данных
git clone https://github.com/Pikudan/MLOps.git
cd MLOps
pip install -r requirements-mlops.txt

# Скачивание данных из DVC storage
dvc pull

# Воспроизведение полного пайплайна
dvc repro
```

### DVC Пайплайн

Пайплайн определён в `dvc.yaml` и содержит 3 стадии:

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│ prepare  │────▶│  train   │────▶│ evaluate │
└──────────┘     └──────────┘     └──────────┘
   Проверка        Обучение         Оценка
   данных          модели           метрик
```

| Стадия | Команда | Выходы |
|--------|---------|--------|
| `prepare` | `python scripts/prepare.py` | `data_summary.json` |
| `train` | `python -m training.classification.train` | `training/models/tomato/` |
| `evaluate` | `python scripts/evaluate.py` | `metrics.json` |

### Настройка Google Drive Remote

```bash
# 1. Создайте папку в Google Drive и скопируйте её ID из URL
# URL: https://drive.google.com/drive/folders/FOLDER_ID

# 2. Добавьте remote
dvc remote add -d gdrive gdrive://YOUR_FOLDER_ID

# 3. Push данных (потребуется OAuth авторизация)
dvc push
```

### Переключение версий

```bash
# Переключиться на предыдущую версию данных
git checkout HEAD~1
dvc checkout

# Вернуться к актуальной версии
git checkout main
dvc checkout
```

---

## 📊 MLflow: Трекинг экспериментов

Проект интегрирован с [MLflow](https://mlflow.org/) для отслеживания экспериментов.

### Что логируется

| Тип | Данные |
|-----|--------|
| **Параметры** | seed, learning_rate, batch_size, epochs, hidden_dim, dropout, ... |
| **Метрики** | train_loss, train_accuracy, val_loss, val_accuracy (на каждой эпохе) |
| **Артефакты** | model (PyTorch), config.yaml, dvc.lock |
| **Теги** | dvc_data_hash, git_commit |

### Просмотр результатов

```bash
# Запуск MLflow UI
cd MLOps
mlflow ui --port 5000

# Откройте http://localhost:5000
```

### Запуск обучения с MLflow

```bash
# Стандартный запуск (логи в локальную папку mlruns/)
python -m training.classification.train training/classification/configs/tomato.yaml

# С указанием имени эксперимента
python -m training.classification.train training/classification/configs/tomato.yaml \
    --experiment-name my-experiment \
    --run-name run-001

# С удалённым MLflow сервером
export MLFLOW_TRACKING_URI=http://mlflow-server:5000
python -m training.classification.train training/classification/configs/tomato.yaml
```

### Структура MLflow

```
mlruns/
└── <experiment_id>/
    └── <run_id>/
        ├── artifacts/
        │   ├── model/           # PyTorch модель
        │   ├── config/          # Конфиг обучения
        │   └── dvc/             # dvc.lock для воспроизводимости
        ├── metrics/             # Метрики по эпохам
        ├── params/              # Гиперпараметры
        └── tags/                # dvc_data_hash, git_commit
```

### Связь DVC и MLflow

При каждом запуске обучения автоматически логируется:
- `dvc_data_hash` — хеш версии данных из DVC
- `dvc.lock` — файл для воспроизведения точной версии данных

Это позволяет восстановить точную версию данных для любого эксперимента:
```bash
# Найти dvc.lock в артефактах MLflow run
# Скопировать его в проект и выполнить:
dvc checkout
```

---

## 🐳 Docker: Офлайн-инференс

Docker-образ для офлайн-инференса модели классификации болезней томатов.

### Сборка образа

```bash
# Сборка образа
docker build -t ml-app:v1 .

# Проверка размера (должен быть < 1 GB)
docker images ml-app:v1
```

### Запуск инференса

```bash
# Создать директории для данных
mkdir -p data/input data/output

# Скопировать изображения в data/input
cp path/to/your/images/*.jpg data/input/

# Запуск контейнера
docker run -v $(pwd)/data:/data ml-app:v1 \
    --input_path /data/input \
    --output_path /data/output/preds.csv

# Просмотр результатов
cat data/output/preds.csv
```

### Параметры скрипта predict.py

| Параметр | Описание | По умолчанию |
|----------|----------|--------------|
| `--input_path` | Путь к изображению или директории | (обязательный) |
| `--output_path` | Путь к выходному CSV файлу | (обязательный) |
| `--model_dir` | Путь к директории с моделью | `training/models/tomato` |
| `--image_size` | Размер изображения для предобработки | 224 |
| `--batch_size` | Размер батча для инференса | 32 |
| `--device` | Устройство (cpu/cuda) | cpu |

### Формат входных/выходных данных

**Вход:** 
- Одиночное изображение (JPG, PNG)
- Директория с изображениями

**Выход (CSV):**
```csv
filename,predicted_class,confidence,class_index
image1.jpg,healthy,0.9542,2
image2.jpg,late_blight,0.8721,3
```

### Пример с volume mapping

```bash
# С моделью извне контейнера
docker run \
    -v $(pwd)/data:/data \
    -v $(pwd)/custom_model:/app/training/models/tomato \
    ml-app:v1 \
    --input_path /data/input \
    --output_path /data/preds.csv
```

### Dockerfile структура

```dockerfile
FROM python:3.10-slim
# CPU-only PyTorch для меньшего размера образа
# Копирует src/predict.py и training/classification/src/
# ENTRYPOINT: python -m src.predict
```

---

## 🚀 TorchServe: Онлайн REST API

Docker-контейнер с TorchServe для онлайн-инференса через REST API.

### Структура

```
torchserve/
├── handler.py         # Кастомный обработчик (пред/постобработка)
├── export_model.py    # Экспорт модели в TorchScript
├── build_mar.sh       # Скрипт сборки MAR архива
├── config.properties  # Конфигурация TorchServe
├── Dockerfile         # Docker образ на базе pytorch/torchserve
└── model-store/       # Директория для MAR файлов
    └── tomato-disease.mar
```

### Сборка MAR архива

```bash
# 1. Экспорт модели в TorchScript
python torchserve/export_model.py \
    --model-dir training/models/tomato \
    --output torchserve/model.pt

# 2. Создание MAR архива
torch-model-archiver \
    --model-name tomato-disease \
    --version 1.0 \
    --serialized-file torchserve/model.pt \
    --handler torchserve/handler.py \
    --export-path torchserve/model-store

# Или использовать готовый скрипт:
./torchserve/build_mar.sh
```

### Сборка и запуск Docker-контейнера

```bash
# Сборка образа
docker build -t mymodel-serve:v1 -f torchserve/Dockerfile .

# Запуск контейнера
docker run -d \
    --name torchserve \
    -p 8080:8080 \
    -p 8081:8081 \
    -p 8082:8082 \
    mymodel-serve:v1

# Проверка статуса
docker logs torchserve
curl http://localhost:8080/ping
```

### REST API Endpoints

| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/ping` | GET | Health check |
| `/predictions/tomato-disease` | POST | Инференс изображения |
| `/models` | GET | Список загруженных моделей |
| `/models/tomato-disease` | GET | Информация о модели |

### Примеры запросов

```bash
# Health check
curl http://localhost:8080/ping
# Response: {"status": "Healthy"}

# Инференс изображения (бинарные данные)
curl -X POST http://localhost:8080/predictions/tomato-disease \
    -T sample_image.jpg

# Инференс с указанием Content-Type
curl -X POST http://localhost:8080/predictions/tomato-disease \
    -H "Content-Type: image/jpeg" \
    --data-binary @sample_image.jpg
```

### Формат ответа

```json
{
    "predicted_class": "late_blight",
    "confidence": 0.9234,
    "top_predictions": [
        {"class": "late_blight", "probability": 0.9234},
        {"class": "early_blight", "probability": 0.0521},
        {"class": "healthy", "probability": 0.0143}
    ]
}
```

### Конфигурация сервиса

Файл `torchserve/config.properties`:

| Параметр | Значение | Описание |
|----------|----------|----------|
| `inference_address` | `0.0.0.0:8080` | Порт для инференса |
| `management_address` | `0.0.0.0:8081` | Порт для управления |
| `metrics_address` | `0.0.0.0:8082` | Порт для метрик |
| `default_workers_per_model` | 1 | Количество воркеров |
| `job_queue_size` | 100 | Размер очереди запросов |

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

### Phase 1: Baseline Models (In Progress 🔄)

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

- [ ] Подбор learning rate и batch size


#### Эксперимент 2.2: Улучшение классификации болезней
**Цель**: Достичь Accuracy ≥ 0.92

- [ ] Сравнение архитектур (ResNet50, EfficientNet, ViT)


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

#### Эксперимент 4.1: Continuous Training Pipeline
**Цель**: Автоматическое переобучение на новых данных

#### Эксперимент 4.2: Monitoring & Drift Detection
**Цель**: Отслеживание качества модели в продакшене


---

## 🏗️ Архитектура системы

```
┌──────────────────────────────────────────────────────────────────┐
│                        User Interface Layer                      │
├──────────────────────────────────────────────────────────────────┤
│                       Farmer Telegram Bot                        │
│                                                                  │
└──────────┬──────────────────────┬───────────────────────┬────────┘
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
git clone https://github.com/Pikudan/MLOps.git
cd MLOps
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
│   └── firebase/                      # Firebase интеграция
│
├── tomato_detected_training.ipynb     # Обучение детекции
├── tomato_detected_inference.ipynb    # Инференс детекции
└── tomato_diseases.ipynb              # Обучение классификации болезней
```

---

## Обучение модели

Новый модуль обучения расположен в каталоге `training/` и включает конфиги, исходный код и тесты.

### Быстрый старт (используется `torchvision.datasets.FakeData`)

```bash
cd training
python train.py configs/default.yaml --epochs 2 --batch-size 16
```

Скрипт выполняет полный пайплайн:
- чтение параметров из YAML-конфига;
- загрузка/генерация данных и базовая статистика;
- обучение модели `SimpleCNN` с логированием (`training/logs/training.log`);
- сохранение обученной модели в формате, совместимом с Hugging Face (`training/models/latest/`).

### Конфигурация

Файл `training/configs/default.yaml` содержит параметры обучения:
- `data`: тип датасета (`fake` или `imagefolder`), размер изображений, аугментации;
- `model`: архитектура и гиперпараметры CNN;
- `optim`: lr, weight decay, число эпох, размер батча, устройство;
- `logging`: уровень логирования и директория;
- `save`: путь для сохранения модели.

Для реальных данных обновите поля `data.dataset`, `data.train_dir`, `data.val_dir` и `model.num_classes`.

---

## Тесты и CI/CD

- Юнит-тесты для классификации расположены в `training/classification/tests/` и покрывают предобработку данных, конфигурации и тренировочный пайплайн.
- Запуск локально:

  ```bash
  cd training
  PYTHONPATH=./classification/src pytest classification/tests
  ```

- Автоматический запуск тестов настроен через GitHub Actions (`.github/workflows/tests.yml`).
  При каждом push / PR устанавливаются зависимости из `training/classification/requirements.txt`,
  запускается `pytest` для классификации и выполняется проверка YOLO-конфига в режиме `--dry-run`.

## YOLO Детекция

Для детекции/сегментации томатов с помощью Ultralytics YOLO создан отдельный модуль `training/detection/yolo/`.

- Основной конфиг: `training/detection/yolo/configs/tomato_detect.yaml` (обновите путь к датасету в `training/detection/yolo/datasets/tomato.yaml`).
- Запуск обучения:
  ```bash
  python training/detection/yolo/scripts/train_yolo.py training/detection/yolo/configs/tomato_detect.yaml
  ```
- Проверка конфигурации без обучения: добавьте `--dry-run` (используется в CI).
- Экспорт модели (ONNX/TorchScript):
  ```bash
  python training/detection/yolo/scripts/export_yolo.py training/models/yolo/weights.pt --formats onnx torchscript
  ```
- Подробности и инструкции см. в `training/detection/yolo/README.md`.

