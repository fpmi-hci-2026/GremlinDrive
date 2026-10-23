# Маршруты и конечные точки API

Базовый путь - /api/v1. Спецификация OpenAPI 3.1 хранится в openapi.json. HTTP-методы отражают работу с ресурсом: GET читает, POST создаёт ресурс или объект операции, PUT заменяет настройки, PATCH меняет отдельные поля, DELETE отзывает доступ или перемещает файл в корзину.

Для взаимодействия веб- и мобильного клиента выбран REST/JSON через HTTPS. Прямой доступ клиентов к общей БД связывал бы их со схемой и обходил бы проверки прав. Обмен файлами остаётся пользовательской функцией, а не способом синхронизации серверных таблиц. Длительные задачи загрузки, проверки и уведомлений в целевой архитектуре передаются worker через очередь Redis; для LLM предусмотрен MCP-адаптер.

Коллекции файлов поддерживают q, status, limit от 1 до 100 и offset. UUID передаются строками. Размер хранится в байтах. Временные метки в mock представлены Unix seconds; целевой контракт должен сохранять согласованное представление времени во всех клиентах.

Для лабораторной есть два разных сервиса. Prism на порту 4010 симулирует весь контракт из 52 операций. FastAPI на порту 8044 реализует 21 операцию с состоянием SQLite. Поле x-implementation в спецификации показывает границу. Промышленная регистрация, TOTP, передача частей файла, LDAP и push в этот прототип не входят.

| Метод | Маршрут | UC | Источник | Проверка |
|---|---|---|---|---|
| GET | `/health` | UC-19 | FR-30 | stateful-mock |
| GET | `/api/v1/me` | UC-02 | FR-02,FR-30 | stateful-mock |
| GET | `/api/v1/me/quota` | UC-14 | FR-18 | stateful-mock |
| GET | `/api/v1/files` | UC-06 | FR-09 | stateful-mock |
| GET | `/api/v1/files/{file_id}` | UC-06 | FR-08 | stateful-mock |
| PATCH | `/api/v1/files/{file_id}` | UC-04 | FR-05 | stateful-mock |
| DELETE | `/api/v1/files/{file_id}` | UC-07 | FR-10 | stateful-mock |
| POST | `/api/v1/files/{file_id}/restorations` | UC-07 | FR-10 | stateful-mock |
| GET | `/api/v1/files/{file_id}/versions` | UC-08 | FR-11 | stateful-mock |
| GET | `/api/v1/folders` | UC-04 | FR-05 | stateful-mock |
| POST | `/api/v1/folders` | UC-04 | FR-05 | stateful-mock |
| GET | `/api/v1/share-links` | UC-09 | FR-14 | stateful-mock |
| POST | `/api/v1/share-links` | UC-09 | FR-12 | stateful-mock |
| DELETE | `/api/v1/share-links/{share_id}` | UC-09 | FR-14 | stateful-mock |
| POST | `/api/v1/public/shares/{token}/access` | UC-10 | FR-13 | stateful-mock |
| GET | `/api/v1/public/shares/{token}/content` | UC-10 | FR-13 | stateful-mock |
| POST | `/api/v1/access-requests` | UC-14 | FR-18 | stateful-mock |
| GET | `/api/v1/admin/access-requests` | UC-14 | FR-19 | stateful-mock |
| POST | `/api/v1/admin/access-requests/{request_id}/decisions` | UC-14 | FR-19 | stateful-mock |
| PUT | `/api/v1/admin/users/{user_id}/quota` | UC-15 | FR-21 | stateful-mock |
| GET | `/api/v1/admin/audit-records` | UC-16 | FR-23 | stateful-mock |
| POST | `/api/v1/auth/registrations` | UC-01 | FR-01 | contract-mock |
| POST | `/api/v1/auth/email-confirmations` | UC-01 | FR-01 | contract-mock |
| POST | `/api/v1/auth/sessions` | UC-02 | FR-02,FR-04 | contract-mock |
| DELETE | `/api/v1/auth/sessions/current` | UC-02 | FR-02 | contract-mock |
| POST | `/api/v1/auth/password-resets` | UC-02 | FR-02 | contract-mock |
| POST | `/api/v1/auth/totp/enrollments` | UC-03 | FR-03 | contract-mock |
| POST | `/api/v1/auth/totp/verifications` | UC-03 | FR-03 | contract-mock |
| POST | `/api/v1/uploads` | UC-05 | FR-06,FR-27 | contract-mock |
| GET | `/api/v1/uploads/{upload_id}` | UC-05 | FR-06 | contract-mock |
| DELETE | `/api/v1/uploads/{upload_id}` | UC-05 | FR-06 | contract-mock |
| PUT | `/api/v1/uploads/{upload_id}/parts/{part_no}` | UC-05 | FR-06 | contract-mock |
| POST | `/api/v1/uploads/{upload_id}/completions` | UC-05 | FR-06,FR-07 | contract-mock |
| GET | `/api/v1/files/{file_id}/content` | UC-06 | FR-08,FR-26 | contract-mock |
| GET | `/api/v1/files/{file_id}/previews` | UC-06 | FR-08 | contract-mock |
| POST | `/api/v1/files/{file_id}/version-restorations` | UC-08 | FR-11 | contract-mock |
| POST | `/api/v1/folders/{folder_id}/invitations` | UC-11 | FR-15 | contract-mock |
| POST | `/api/v1/invitations/{invitation_id}/acceptances` | UC-11 | FR-15 | contract-mock |
| GET | `/api/v1/folders/{folder_id}/members` | UC-12 | FR-16 | contract-mock |
| PUT | `/api/v1/folders/{folder_id}/members/{user_id}` | UC-12 | FR-16 | contract-mock |
| DELETE | `/api/v1/folders/{folder_id}/members/{user_id}` | UC-12 | FR-16 | contract-mock |
| GET | `/api/v1/files/{file_id}/comments` | UC-13 | FR-17 | contract-mock |
| POST | `/api/v1/files/{file_id}/comments` | UC-13 | FR-17 | contract-mock |
| GET | `/api/v1/notifications` | UC-13 | FR-25 | contract-mock |
| PATCH | `/api/v1/notifications/{notification_id}` | UC-13 | FR-25 | contract-mock |
| POST | `/api/v1/devices` | UC-17 | FR-25,FR-27 | contract-mock |
| GET | `/api/v1/sync/changes` | UC-17 | FR-26 | contract-mock |
| GET | `/api/v1/admin/users` | UC-15 | FR-20 | contract-mock |
| PATCH | `/api/v1/admin/users/{user_id}` | UC-15 | FR-20 | contract-mock |
| PUT | `/api/v1/admin/users/{user_id}/roles` | UC-15 | FR-21 | contract-mock |
| POST | `/api/v1/admin/ldap-synchronizations` | UC-18 | FR-22 | contract-mock |
| POST | `/api/v1/admin/reports` | UC-16 | FR-23,FR-24,FR-29 | contract-mock |

## Пример запроса

```http
POST /api/v1/share-links HTTP/1.1
Authorization: Bearer lab-owner-token
Content-Type: application/json

{
  "file_id": "20000000-0000-4000-8000-000000000001",
  "password": "laboratory123",
  "expires_in_days": 7,
  "access_level": "download"
}
```

Успешный ответ имеет статус 201 и содержит id, file_id, token, url, expires_at и access_level. Пароль в ответ не включается.

## Коды ответов

| Код | Значение |
|---|---|
| 200 | Чтение или изменение выполнено |
| 201 | Создан ресурс или результат операции |
| 401 | Нет действующей сессии либо неверен пароль ссылки |
| 403 | Пользователь определён, но действие ему не разрешено |
| 404 | Объект не найден или публичная ссылка недействительна |
| 409 | Конфликт состояния, повторное решение или неподходящая квота |
| 413 | Часть файла превышает допустимый размер |
| 422 | Запрос не соответствует схеме |
| 429 | Превышен лимит попыток проверки пароля |
| 507 | Не хватает квоты для загрузки |

Все POST, PUT и PATCH с данными имеют схему тела и пример. POST restorations без тела создаёт операцию восстановления. Для списка и деталей заданы схемы ответов.
