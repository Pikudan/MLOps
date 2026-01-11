# Настройка DVC Credentials для Yandex Object Storage

## Проблема: "unable location credentials" при dvc pull

Если при выполнении `dvc pull` возникает ошибка "unable location credentials", это означает, что нужны ключи доступа к Yandex Object Storage.

## Решение: Настройка credentials

### Способ 1: Через DVC config (рекомендуется)

**Публичные ключи для чтения (role: viewer):**

Для получения публичных ключей доступа (role: viewer, только чтение) обратитесь к владельцу репозитория или настройте свои ключи в Yandex Cloud Console.

```bash
# Настройка ключей доступа (замените на реальные ключи)
dvc remote modify --local yandex_storage access_key_id YOUR_ACCESS_KEY_ID
dvc remote modify --local yandex_storage secret_access_key YOUR_SECRET_ACCESS_KEY

# Проверка
cat .dvc/config.local
```

**Примечание:** Ключи с ролью `viewer` (только чтение) подходят для `dvc pull`. Для `dvc push` нужны ключи с правами на запись.

### Способ 2: Через переменные окружения

```bash
# Установить переменные окружения (замените на реальные ключи)
export AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=YOUR_SECRET_ACCESS_KEY

# Или для Yandex:
export YC_ACCESS_KEY_ID=YOUR_ACCESS_KEY_ID
export YC_SECRET_ACCESS_KEY=YOUR_SECRET_ACCESS_KEY
```

**Публичные ключи для чтения:** Обратитесь к владельцу репозитория для получения публичных ключей (role: viewer) или создайте свои в Yandex Cloud Console.

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
