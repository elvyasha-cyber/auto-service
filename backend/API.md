# Данные backend для фронтенда

Сайт и API открываются через Nginx на порту 443: `https://IP/`. Префикса `/api` нет. Порт backend снаружи не публикуется. Пути `/docs`, `/redoc` и `/openapi.json` отвечают 403.

Заголовок для закрытых запросов: `Authorization: Bearer <access_token>`. Токен берётся из ответа входа и хранится в браузере. В ответы пароль не попадает, только хеш остаётся в таблице `admins`.

## Вход мастера

`GET /auth/check` — без токена.

Ответ: `{ "has_admin": true }`. Пока `false`, на `/admin` видна кнопка «Зарегистрироваться».

`POST /auth/register` — без токена, только пока администраторов нет.

```json
{ "login": "master", "password": "secret1" }
```

Логин 2–64 символа без пробелов. Пароль не короче 6 символов.

`POST /auth/login` — те же два поля.

Ответ регистрации и входа:

```json
{
  "access_token": "jwt",
  "token_type": "bearer",
  "admin": { "id": 1, "login": "master", "created_at": "2026-10-28T09:00:00Z" }
}
```

`GET /auth/me` — с токеном. Ответ: объект `admin` без пароля.

Ошибки: `401` «Нужен вход» или «Неверный логин или пароль», `403` «Регистрация закрыта».

## Услуги, таблица `admin_data`

В уроке эта таблица названа `admin_settings`. В проекте путь и таблица — `admin_data`.

`GET /admin-data` — без токена. Ответ — массив, его читает и главная форма, и панель мастера.

```json
[
  { "id": 13, "service_name": "замена колес", "budget_min": 15000, "budget_max": 25000 }
]
```

`POST /admin-data`, `PUT /admin-data/{id}`, `DELETE /admin-data/{id}` — только с токеном.

Тело создания и сохранения:

```json
{ "service_name": "замена колес", "budget_min": 15000, "budget_max": 25000 }
```

`budget_min` и `budget_max` — целые числа. Верхняя граница не меньше нижней, иначе `422`.

`POST` и `PUT` возвращают ту же строку с `id`. `DELETE` возвращает `{ "deleted": 13 }`.

## Заявка клиента, таблица `leads`

`POST /leads` — без токена. Все поля — строки, пустая строка допустима. Бюджет одной строкой, не двумя числами.

```json
{
  "first_name": "",
  "last_name": "",
  "middle_name": "",
  "business_info": "",
  "budget": "от 15 000 ₽ до 25 000 ₽",
  "contact_method": "",
  "phone": "",
  "email": "",
  "telegram": "",
  "whatsapp": "",
  "max_contact": "",
  "comment": "",
  "business_niche": "",
  "company_size": "",
  "task_volume": "",
  "client_role": "",
  "business_size": "",
  "need_volume": "",
  "deadline": "",
  "task_type": "",
  "product": "",
  "convenient_time": ""
}
```

Ответ — та же заявка плюс `id`.

`GET /leads` — массив заявок. В уроке этот список назван `/api/applications/`. У нас префикса `/api` нет, таблица называется `leads`.

`GET /leads/queue` — та же очередь для панели мастера, уже разобранная. Горячие сверху, холодные снизу. У каждой заявки есть `temperature` (`горячая`, `тёплая`, `холодная`), `reasons`, `department`, `personal_manager`, `spend_time`. Этих полей в таблице нет: программа смотрит срок, бюджет, роль, размер компании, объём, нишу и тип задачи.

`GET /leads/{id}` — одна. `PUT /leads/{id}` — те же поля, можно прислать только изменённые. `DELETE /leads/{id}` — `{ "deleted": 1 }`. Вместе с заявкой удаляются её метрики.

## Метрики заявки, таблица `lead_metrics`

Одна строка на заявку. Связь по `lead_id`. Это не посекундная карта курсора из урока.

`POST /lead-metrics` — без токена. Заявка с таким `lead_id` уже должна существовать.

```json
{
  "lead_id": 1,
  "time_on_page": 42,
  "buttons_clicked": "отправить заявку",
  "cursor_pauses": "бюджет 120,340",
  "return_count": 0
}
```

`time_on_page` и `return_count` — целые числа, секунды и число повторных визитов. Два текстовых поля — строки. Ответ — эти поля и `lead_id`.

`GET /lead-metrics` — массив. `GET /lead-metrics/{lead_id}` — одна строка. `PUT` и `DELETE` идут по `lead_id`, не по отдельному id метрики.

## Движения на главной, таблица `behavior_metrics`

К заявке не привязано. Главная страница шлёт одну запись в секунду, пока вкладка открыта.

`POST /behavior-metrics` — без токена. В уроке этот адрес записан как `/api/behavior-metrics/`. У нас префикса `/api` нет.

```json
{
  "application_id": 0,
  "time_on_page": 12,
  "buttons_clicked": "отправить заявку × 1",
  "cursor_positions": "420,310",
  "return_frequency": 0
}
```

`application_id` принимается и не сохраняется. `time_on_page` — секунды. `buttons_clicked` — какие кнопки и сколько раз. `cursor_positions` — одна точка «x,y» за эту секунду. `return_frequency` по заданию остаётся 0.

Ответ — строка таблицы с `id` и `created_at`, без `application_id`.

`GET /behavior-metrics?skip=0&limit=100` — список этих строк.

`GET /behavior-metrics/summary` — сводка для окна в панели мастера. Три промежутка: сутки, 7 дней, 30 дней. У каждого визита берётся самое долгое `time_on_page`, из этих чисел считаются среднее и максимум. `points` — кружки карты: `x`, `y`, `count`. Точка `0,0` в карту не входит: так страница отмечает, что мышь ещё не двигали.
