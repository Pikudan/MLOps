# YOLO Training Module

Модуль содержит все необходимые артефакты для обучения моделей YOLO (Ultralytics) на данных по детекции/сегментации томатов.

## Структура

```
training/detection/yolo/
├── configs/           # YAML-конфиги обучения
├── datasets/          # Описание датасетов в формате Ultralytics
├── scripts/           # CLI-скрипты для обучения и экспорта
└── tests/             # Автотесты (валидация конфигов)
```

## Быстрый старт

1. Обновите `training/detection/yolo/datasets/tomato.yaml`, указав абсолютный путь к датасету.
2. Установите зависимости:
   ```bash
   pip install -r training/requirements.txt
   ```
3. Запустите обучение:
   ```bash
   python training/detection/yolo/scripts/train_yolo.py training/detection/yolo/configs/tomato_detect.yaml
   ```

Флаг `--dry-run` позволяет проверить конфигурацию без запуска обучения (используется в CI).

## Экспорт модели

```bash
python training/detection/yolo/scripts/export_yolo.py training/models/yolo/weights.pt --formats onnx torchscript
```

## Тесты

```bash
cd training
pytest detection/yolo/tests
```

