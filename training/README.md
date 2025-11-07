## Training Module

Этот модуль объединяет два независимых направления:

- `classification/` — пайплайн обучения классификации болезней (PyTorch + SimpleCNN).
- `detection/` — пайплайн детекции/сегментации (Ultralytics YOLO).

Структура каталога:

```
training/
├── classification/
│   ├── configs/        # Конфиги классификации
│   ├── datasets/       # Подготовленные наборы данных
│   ├── scripts/        # Скрипты подготовки/обработки
│   ├── src/            # Исходный код тренировочного пайплайна
│   ├── tests/          # Автотесты классификации
│   └── train.py        # CLI для обучения
├── detection/
│   └── yolo/           # Модуль для обучения YOLO (конфиги, скрипты, тесты)
├── logs/               # Общие логи
├── models/             # Сохранённые веса
└── requirements.txt    # Связка зависимостей (делегирует в classification/requirements.txt)
```

### Классификация

```
cd training
python -m training.classification.train training/classification/configs/default.yaml
```

Перед запуском убедитесь, что указаны корректные пути к данным и классу датасета (`training/classification/datasets/...`).

Ключевые компоненты классификации:

- `src/data.py` — построение трансформаций и датасетов, проверка структуры `ImageFolder`.
- `src/trainer.py` — обучение с валидацией батчей (размерности, диапазоны, совпадение меток).
- `src/utils.py` — функции для постобработки предсказаний с проверкой вероятностей.
- `src/validation.py` — общий набор проверок (батчи, вероятности, структуру данных).
- `scripts/prepare_tomato_dataset.py` — подготовка датасета томатов из PlantVillage.

### Проверки и тесты

Юнит-тесты покрывают предобработку, пайплайн обучения и постобработку результатов:

```
cd training
PYTHONPATH=./classification/src pytest classification/tests
```

Что проверяется:

- корректность структуры и формата данных (`test_data.py`);
- валидация батчей и реакции тренера на ошибочные входы (`test_trainer.py`);
- обработка логитов и вероятностей для API (`test_postprocess.py`).

Эти же тесты запускаются в CI через GitHub Actions (см. `.github/workflows/tests.yml`).

### Детекция/Сегментация YOLO

Инструкции находятся в `training/detection/yolo/README.md`.

