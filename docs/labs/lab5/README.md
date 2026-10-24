# Лабораторная работа 5: прототип GremlinDrive

Работа продолжает исходные ЛР1-2 команды и SRS ЛР3 (392a849). Преемственность описана в [CONTINUITY.md](../CONTINUITY.md). Палитра #2E9E62, Inter, навигация и базовые UC сохранены; для кнопок выбран тёмный зелёный #1F7A4B.

[Отчёт](lab5-report.pdf), [текст](REPORT.md), [прототип](prototype/index.html), [стиль](prototype/styleguide.html).

Публичный прототип: https://fpmi-hci-2026.github.io/GremlinDrive/labs/lab5/prototype/. Параметры: mobile=1, theme=brand|contrast|emerald, screen=files&folder=course. Локальный запуск из docs/labs: `python3 -m http.server 8056`. Тестовый вход: student@example.test / gremlin2026. Реальной авторизации и передачи файлов нет, в localStorage остаются демонстрационные метаданные.

Поддерживаются очередь, папки, поиск, участники и роли, пароль гостевой ссылки, версии, корзина, квота, аудит, уведомления и офлайн-состояние. Восстановление создаёт новую версию. «Общие папки» и публичные ссылки разделены. Мобильные вкладки: Файлы / Общие / + / Уведомления / Профиль.

Оценки 15 профилей смоделированы, не получены от людей. data/semantic.csv содержит 1350 значений и явное происхождение. Генератор scripts/model_study.py обновляет обе работы; prepare_assets.py собирает снимки, write_reports.py - текст, build_reports.py - PDF. Нужны matplotlib, Pillow, ReportLab и Liberation Serif. Шрифт Inter приложен с лицензией.

В assets находятся 6 веб-ширин, 5 мобильных размеров и 3 палитры на двух платформах. Снимки сделаны при прямом изменении viewport IAB. Проверка: `python3 ../lab6/scripts/verify.py`.
