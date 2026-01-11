# Настройка DVC Credentials для Yandex Object Storage

## Проблема: "unable location credentials" при dvc pull

Если при выполнении `dvc pull` возникает ошибка "unable location credentials", это означает, что нужны ключи доступа к Yandex Object Storage.

## Решение: Настройка credentials

Для получения публичных ключей доступа (role: viewer, только чтение) обратитесь к владельцу репозитория или настройте свои ключи в Yandex Cloud Console.

```bash
dvc remote modify --local yandex_storage access_key_id YOUR_ACCESS_KEY_ID
dvc remote modify --local yandex_storage secret_access_key YOUR_SECRET_ACCESS_KEY
```
