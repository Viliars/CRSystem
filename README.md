# CRSystem
Community Recommendation System

Определяем понятия:

Эффективная функция - это функция, основанная на коде VKscript, и способная содержать в себе до 25 запросов.

Ограничение по кол-ву запросов:

С ключом пользователя до 3 запросов в секунду

С ключом сообщества до 20 запросов в секунду

Введем переменные:
Left Right - левая правая граница итерации по сообществам

Считаем время выкачки таблицы: сообщество -> колво подписчиков

172 741 352 / 20 / 25(эффективная функция) / 60 / 60 / 24 = 4 дня
