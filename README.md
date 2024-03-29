# Обновление статусов участников

Скрипт позволяет обновлять статус заявки участников из списка.

# Параметры

Первый параметр — название csv-файла (с расширением) файла (должен находиться в одной папке с файлом main.py)

Второй параметр — флаг, 0 - изменяет статус у всех тикетов с данным uid и 1 - изменяет статус только у последнего по дате

Третий параметр — номер yes/no колонки

Четвертый параметр — флаг, 0 - пропускает первый ряд, 1 - обрабатывает все без пропуска

# Запуск

1) Поместить .csv-файл в корневую папку

2) Получить токен на https://oauth.yandex.ru и поместить его в credentials.py вместе с organization id (https://tracker.yandex.ru/settings?from=head-menu)

3) Запустить с нужными параметрами

4) В log.txt будет содержаться список uid-ов с ошибками и в logp.txt - список корректно обновленных

# Возможные ошибки

Поиск тикета завершился с ошибкой - 101

Тикет с данным uid не найден - 404

Список переходов не получен - 102

Переход не выполнен - 103

Данный переход не найден для данного статуса - 104

# Записи в log

В зависимости от второго параметра. Для 0:

log - (uid, Порядковый номер среди тикетов с этим uid, Количество тикетов с этим uid, Код ошибки)

logp - (uid, Порядковый номер среди тикетов с этим uid, Количество тикетов с этим uid, 0 - тикет уже имел нужный статус или 1 - статус был изменен)

Для 1:

log - (uid, Код ошибки)

logp - (uid, 0 - тикет уже имел нужный статус или 1 - статус был изменен)