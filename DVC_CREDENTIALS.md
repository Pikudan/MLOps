# Настройка DVC Credentials для Yandex Object Storage

## Проблема: "unable location credentials" при dvc pull

Если при выполнении `dvc pull` возникает ошибка "unable location credentials", это означает, что нужны ключи доступа к Yandex Object Storage.

## Решение: Настройка credentials

### Способ 1: Через DVC config (рекомендуется)

```bash
# Настройка ключей доступа (сохраняются локально, не коммитятся)
dvc remote modify --local yandex_storage access_key_id YOUR_ACCESS_KEY_ID
dvc remote modify --local yandex_storage secret_access_key YOUR_SECRET_ACCESS_KEY

# Проверка
cat .dvc/config.local
```

### Способ 2: Через переменные окружения

```bash
export AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=YOUR_SECRET_ACCESS_KEY

# Или для Yandex:
export YC_ACCESS_KEY_ID=YOUR_ACCESS_KEY_ID
export YC_SECRET_ACCESS_KEY=YOUR_SECRET_ACCESS_KEY
```

## Получение ключей доступа

1. Войдите в [Yandex Cloud Console](https://console.cloud.yandex.ru/)
2. Перейдите в **Object Storage** → выберите bucket `dvc-storage-tlm`
3. Перейдите в **Service Accounts**
4. Создайте новый Service Account или используйте существующий
5. Создайте **Static Access Key**
6. Скопируйте:
   - **Access Key ID**
   - **Secret Access Key**

## Проверка работы

```bash
# После настройки credentials
dvc pull training/classification/datasets/tomato.dvc
```

Если всё настроено правильно, данные должны загрузиться без ошибок.
