# loggeroProject
Система логирования

***
Сервис централизованного логирования работающий по REST API и websocket. 

Особенности: 

 :heavy_check_mark: Авторизация с использованием JWT токена; \
 :heavy_check_mark: Ведение журналов логов по проектам; \
 :heavy_check_mark: Выдача токенов логирования; \
 :heavy_check_mark: Отправка логов по websocket. 
 
Используемые технологии:
-----------------------------------
<li> FastAPI </li>
<li> Pydantic </li>
<li> Mongodb (Motor) </li>
<li> Pytest </li>

Установка:
----------------------------------

1) Клонировать директорию
2) Создать виртуальное окружение:
```
python -m venv venv
```

3) Активировать виртуальное окружение

на windows:
```.\venv\scripts\activate``` 

на линукс:
```source venv/bin/activate```


4) Установить зависимости:
```
pip install -e .
```

5) Запустить программу: 
```
python start_server.py
```

 
 
