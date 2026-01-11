# 🍅 Tomato Lives Matter - ML-powered Agricultural Assistant

## 📋 Оглавление

### MLOps Инфраструктура
- [DVC: Версионирование данных](#-dvc-версионирование-данных)
- [MLflow: Трекинг экспериментов](#-mlflow-трекинг-экспериментов)
- [Docker: Офлайн-инференс](#-docker-офлайн-инференс)
- [TorchServe: Онлайн REST API](#-torchserve-онлайн-rest-api)

### Быстрый старт с лучшей моделью
```bash
# Клонирование и установка
git clone https://github.com/Pikudan/MLOps.git
cd MLOps
pip install -r requirements-mlops.txt

# Получение лучшей модели через DVC
dvc pull training/models/tomato_large.dvc

# Тестирование модели
python training/classification/scripts/test_inference.py \
    --model-dir training/models/tomato_large \
    --test-dir training/classification/datasets/tomato/test \
    --output outputs/test_predictions.csv
```

### Проект
- [Бизнес-цель проекта](#-бизнес-цель-проекта)
- [Целевые метрики для продакшена](#-целевые-метрики-для-продакшена)
- [Набор данных](#набор-данных)
- [План экспериментов](#-план-экспериментов)
- [Архитектура системы](#️-архитектура-системы)
- [Установка и запуск](#-установка-и-запуск)
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

#### Классификация болезней томатов (SimpleCNN)
| Метрика | Текущий результат | Целевое значение | Критическое значение |
|---------|-------------------|------------------|---------------------|
| **Accuracy** | **0.7917** (79.17%) | ≥ 0.9 | ≥ 0.7 ✅ |
| **F1-Score (macro avg)** | **0.7362** | ≥ 0.9 | ≥ 0.7 ✅ |
| **Precision (macro avg)** | **0.8017** | ≥ 0.9 | ≥ 0.7 ✅ |
| **Recall (macro avg)** | **0.7209** | ≥ 0.9 | ≥ 0.7 ✅ |

**Лучшая модель**: `simple_cnn_large` (hidden_dim=128, dropout=0.4, lr=0.0003)
- Сохранена в: `training/models/tomato_large/`
- Тестовый датасет: 3582 изображения, 10 классов
- Результаты: `outputs/test_metrics_large.json`, `outputs/test_predictions_large.csv`

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

| Тип | Путь | Описание | Версионирование |
|-----|------|----------|-----------------|
| **Датасет** | `training/classification/datasets/tomato/` | 6436 изображений болезней томатов | `training/classification/datasets/tomato.dvc` |
| **Модели (baseline)** | `training/models/tomato/` | Обученные веса SimpleCNN | Output стадии `train` в `dvc.yaml` |
| **Лучшая модель** | `training/models/tomato_large/` | Best model (simple_cnn_large, 79.17% accuracy) | `training/models/tomato_large.dvc` |
| **DVC файлы** | `*.dvc` | Ссылки на версионированные данные | В Git |
| **Remote** | Yandex Object Storage | `s3://dvc-storage-tlm` | Конфигурация в `.dvc/config` |

### Быстрый старт

```bash
# Клонирование и восстановление данных
git clone https://github.com/Pikudan/MLOps.git
cd MLOps
pip install -r requirements-mlops.txt

# Скачивание данных из DVC storage
dvc pull

# Получение лучшей модели для тестирования
dvc pull training/models/tomato_large.dvc

# Воспроизведение полного пайплайна
dvc repro
```

### Получение конкретных моделей

```bash
# Получить только датасет
dvc pull training/classification/datasets/tomato.dvc

# Получить только лучшую модель (для тестирования)
dvc pull training/models/tomato_large.dvc

# Получить все версионированные данные
dvc pull
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

### Yandex Object Storage Remote

Данные хранятся в Yandex Object Storage (S3-совместимое хранилище):

```bash
# Remote уже настроен в .dvc/config:
# url = s3://dvc-storage-tlm
# endpointurl = https://storage.yandexcloud.net
# region = ru-central1

# Скачивание данных (публичный доступ для чтения)
dvc pull

# Для push нужны ключи доступа в .dvc/config.local:
# dvc remote modify --local yandex_storage access_key_id YOUR_KEY
# dvc remote modify --local yandex_storage secret_access_key YOUR_SECRET
dvc push
```

### Альтернатива: Локальное хранилище

```bash
# Для локальной разработки можно использовать локальный remote
dvc remote default local_storage
dvc push  # Сохранит в /tmp/dvc-storage
```

### Версионирование моделей

Лучшая модель (`tomato_large`) версионируется через DVC:

```bash
# Просмотр информации о модели
cat training/models/tomato_large.dvc

# Получение модели (если отсутствует)
dvc pull training/models/tomato_large.dvc

# Проверка статуса модели
dvc status training/models/tomato_large.dvc

# Обновление модели в remote storage (требует ключи доступа)
dvc push training/models/tomato_large.dvc
```

**Характеристики лучшей модели:**
- **Архитектура**: SimpleCNN (hidden_dim=128, dropout=0.4)
- **Размер**: 1.2 MB
- **Test Accuracy**: 79.17%
- **DVC хеш**: `e9c66c4eda006a2459cb576ccb0036b2`

### Переключение версий

```bash
# Переключиться на предыдущую версию данных и модели
git checkout HEAD~1
dvc checkout

# Вернуться к актуальной версии
git checkout main
dvc checkout

# Воспроизвести пайплайн для конкретной версии
git checkout <commit-hash>
dvc checkout
dvc repro  # Пересоздаст все outputs согласно dvc.yaml
```

**Важно:** При переключении версий DVC автоматически восстанавливает соответствующую версию данных и модели из remote storage.

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

#### Локальный MLflow UI

```bash
# Запуск MLflow UI (локальное хранилище)
cd MLOps
mlflow ui --port 5000

# Откройте http://localhost:5000
```

#### Подключение к удалённому MLflow серверу

```bash
# Установка переменной окружения для удалённого сервера
export MLFLOW_TRACKING_URI=http://mlflow-server:5000
# или
export MLFLOW_TRACKING_URI=postgresql://user:pass@host:5432/mlflowdb

# Запуск обучения (логи будут отправляться на удалённый сервер)
python -m training.classification.train training/classification/configs/tomato.yaml
```

**Где смотреть результаты:**
- Локально: `mlruns/` директория в корне проекта
- Удалённо: UI доступен по адресу `MLFLOW_TRACKING_URI`

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

### Подготовка модели

Перед сборкой Docker-образа убедитесь, что модель загружена через DVC:

```bash
# Получить лучшую модель из DVC storage
dvc pull training/models/tomato_large.dvc

# Или получить все данные
dvc pull
```

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

**Использование лучшей модели:**

```bash
# Использовать лучшую модель (tomato_large) для инференса
docker run -v $(pwd)/data:/data ml-app:v1 \
    --input_path /data/input \
    --output_path /data/output/preds.csv \
    --model_dir training/models/tomato_large
```

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

### Что делает скрипт predict.py

Скрипт `src/predict.py` выполняет офлайн-инференс модели классификации болезней томатов:

1. **Загружает модель** из `training/models/tomato/` (PyTorch state_dict)
2. **Читает изображения** из `--input_path` (файл или директория)
3. **Применяет предобработку**: resize до 224x224, нормализация ImageNet
4. **Выполняет предсказания** через модель
5. **Сохраняет результаты** в CSV с колонками: `filename`, `predicted_class`, `confidence`, `class_index`

**Поддерживаемые форматы:**
- Вход: JPG, JPEG, PNG (RGB изображения)
- Выход: CSV файл с предсказаниями

### Dockerfile структура

```dockerfile
FROM python:3.10-slim
# Установка системных зависимостей (gcc, libglib2.0-0)
# Установка Python зависимостей из requirements-mlops.txt
# CPU-only PyTorch для меньшего размера образа (< 1 GB)
# Копирует src/predict.py и training/classification/src/
# Копирует модель training/models/tomato/
# ENTRYPOINT: python -m src.predict
```

**Примечание:** Модель копируется в образ при сборке. Для использования актуальной версии можно выполнить `dvc pull` внутри контейнера или использовать volume mount.

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

### Примеры REST-запросов

#### Health Check

```bash
curl http://localhost:8080/ping
# Response: {"status": "Healthy"}
```

#### Инференс изображения

```bash
# Простой запрос (бинарные данные)
curl -X POST http://localhost:8080/predictions/tomato-disease \
    -T sample_image.jpg

# С указанием Content-Type
curl -X POST http://localhost:8080/predictions/tomato-disease \
    -H "Content-Type: image/jpeg" \
    --data-binary @sample_image.jpg

# Используя Python requests
python -c "
import requests
with open('sample_image.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8080/predictions/tomato-disease',
        data=f,
        headers={'Content-Type': 'image/jpeg'}
    )
print(response.json())
"
```

#### Управление моделями

```bash
# Список всех моделей
curl http://localhost:8081/models

# Информация о конкретной модели
curl http://localhost:8081/models/tomato-disease

# Загрузка новой версии модели
curl -X POST http://localhost:8081/models?url=file:///path/to/model.mar
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

Файл `torchserve/config.properties` содержит параметры конфигурации TorchServe:

| Параметр | Значение | Описание |
|----------|----------|----------|
| `inference_address` | `http://127.0.0.1:8080` | Порт для REST API инференса |
| `management_address` | `http://127.0.0.1:8081` | Порт для управления моделями |
| `metrics_address` | `http://127.0.0.1:8082` | Порт для метрик Prometheus |
| `grpc_inference_port` | `17070` | Порт для gRPC инференса |
| `grpc_management_port` | `17071` | Порт для gRPC управления |
| `default_workers_per_model` | `1` | Количество воркеров на модель |
| `job_queue_size` | `10` | Размер очереди запросов |
| `disable_token_authorization` | `true` | Отключение авторизации (для разработки) |
| `enable_metrics_api` | `true` | Включение API метрик |

**Изменение конфигурации:**
```bash
# Отредактировать torchserve/config.properties
# Перезапустить контейнер
docker restart torchserve
```

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

### Обучение нескольких моделей для сравнения

Для обучения нескольких моделей с разными гиперпараметрами используйте скрипт `train_multiple_models.py`:

```bash
python training/classification/scripts/train_multiple_models.py
```

Скрипт обучит 4 модели с разными конфигурациями:
- `simple_cnn_small`: hidden_dim=32, dropout=0.2, lr=0.001
- `simple_cnn_medium`: hidden_dim=64, dropout=0.3, lr=0.0005
- `simple_cnn_large`: hidden_dim=128, dropout=0.4, lr=0.0003
- `simple_cnn_deep`: hidden_dim=64, dropout=0.5, lr=0.0001, epochs=15

Все модели логируются в MLflow эксперимент `Multiclass-Model-Comparison`.

### Тестирование лучшей модели на тестовом датасете

После обучения нескольких моделей, лучшая модель (по метрикам валидации) сохранена в `training/models/tomato_large/` и версионируется через DVC.

#### Получение модели через DVC

Если модель отсутствует локально (например, после клонирования репозитория):

```bash
# Получить лучшую модель из DVC storage
dvc pull training/models/tomato_large.dvc

# Проверить, что модель загружена
ls -lh training/models/tomato_large/
# Должны быть файлы:
# - config.json
# - pytorch_model.bin (1.2 MB)
```

Модель автоматически загрузится из Yandex Object Storage при выполнении `dvc pull`.

#### Оценка модели (метрики)

Для получения детальных метрик на тестовом датасете:

```bash
python training/classification/scripts/evaluate.py \
    --model-dir training/models/tomato_large \
    --test-dir training/classification/datasets/tomato/test \
    --output outputs/test_metrics_large.json \
    --image-size 224 \
    --batch-size 32
```

Результаты сохраняются в JSON файл с метриками:
- Accuracy, Precision, Recall, F1-Score (macro и weighted)
- Per-class метрики
- Confusion matrix

#### Инференс с сохранением предсказаний

Для получения предсказаний на всех тестовых изображениях с сохранением в CSV:

```bash
python training/classification/scripts/test_inference.py \
    --model-dir training/models/tomato_large \
    --test-dir training/classification/datasets/tomato/test \
    --output outputs/test_predictions_large.csv \
    --image-size 224 \
    --batch-size 32
```

Скрипт создаст:
- `outputs/test_predictions_large.csv` - CSV файл с предсказаниями для каждого изображения
- `outputs/test_predictions_large_summary.txt` - Сводка с точностью по классам

**Результаты лучшей модели (simple_cnn_large) на тестовом датасете:**
- **Test Accuracy: 79.17%** (2836 / 3582 правильных предсказаний)
- **F1-Score (macro): 0.7362**
- **Precision (macro): 0.8017**
- **Recall (macro): 0.7209**

**Точность по классам:**
- `healthy`: 97.92% (336 samples)
- `tomato_yellow_leaf_curl_virus`: 90.66% (1103 samples)
- `bacterial_spot`: 88.34% (463 samples)
- `tomato_mosaic_virus`: 85.90% (78 samples)
- `spider_mites_two_spotted_spider_mite`: 80.00% (340 samples)
- `target_spot`: 70.82% (257 samples)
- `late_blight`: 70.73% (369 samples)
- `septoria_leaf_spot`: 66.03% (312 samples)
- `leaf_mold`: 45.00% (140 samples)
- `early_blight`: 25.54% (184 samples)

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

