# tosot-local-web

Локальный веб-пульт для кондиционеров Tosot / Gree с Wi-Fi: без облака и без приложения TOSOT+.
Построен на библиотеке [greeclimate](https://github.com/cmroche/greeclimate). Проверен на Tosot Lyra X (T09H-SLyW), Wi-Fi модуль U-WB05RT13, прошивка 1.28.

## Запуск

```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000
```

Открыть `http://<ip-сервера>:8000`. Сервер должен быть в той же сети, что и кондиционер (обнаружение идёт по UDP-броадкасту, порт 7000).

## Docker (Linux-хост)

```sh
docker compose up -d --build
```

Нужен `network_mode: host`, иначе броадкаст не дойдёт до кондиционера. На Docker Desktop для Mac это не работает, запускайте без Docker.

## Безопасность

Авторизации в пульте нет. Не выставляйте его в интернет без прокси с токеном или VPN. Доступ к API позволяет управлять кондиционером.

## Совет

Не обновляйте прошивку Wi-Fi модуля кондиционера: после обновления локальное управление может перестать работать.
