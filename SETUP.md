# 🚀 Инструкция по настройке проекта

## Шаг 1: Настройка конфигурационных файлов

### 1.1 Bot Tokens

Для каждого бота создайте файл `config.py` на основе `config.example.py`:

```bash

cp farm/config.example.py farm/config.py


### 1.2 Firebase Credentials

Для каждого бота, использующего Firebase, добавьте `serviceAccountKey.json`:

1. Перейдите в [Firebase Console](https://console.firebase.google.com/)
2. Выберите ваш проект
3. Перейдите в Settings → Service Accounts
4. Нажмите "Generate New Private Key"
5. Сохраните файл как:
   - `farm/firebase/serviceAccountKey.json`
   - `agro_bot/serviceAccountKey.json`
   - `review/firebase/serviceAccountKey.json`

### 1.3 Firebase Config

Создайте файлы `firebase_config.yaml` в соответствующих директориях:

**farm/firebase/firebase_config.yaml**:
```yaml
databaseURL: "https://YOUR-PROJECT.firebaseio.com"
storageBucket: "YOUR-PROJECT.appspot.com"
```

## Шаг 2: Обучить свои модели
- `tomato_detected_training.ipynb` - обучение детекции
- `tomato_diseases.ipynb` - обучение классификации болезней

## Шаг 3: Запуск сервисов

### Локальный запуск

**FastAPI ML Service:**
```bash
cd devops
python -m app.app
# или
uvicorn app.app:app --host 0.0.0.0 --port 8000 --reload
```

**Farm Bot:**
```bash
cd farm
python main.py
```
