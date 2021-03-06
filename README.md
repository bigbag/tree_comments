## Описание задачи:

Необходимо разработать систему хранения комментариев, которая позволит хранить неограниченное число веток уомментариев, неограниченной вложенности.

#### Требования:
* комментарий имеет дату создания и дату редактирования
* комментарий связан с пользователем (user)
* коментарий имеет связь с ресурсом на котором он будет оставлен - блог, страница (entity)
* комментарий можно редактированть (менять только текст)
* комментарий можно удалять, но только если у него нет потомков
* можно добавить комментарий на любой уровень вложенности
* можно выбрать отдельную ветку комментариев начиная с указанного корневого
* можно выбрать все комментарии первого уровня связанные с entity
* можно выбрать историю комментариев каждого user, ограничивая если есть необходимость интервалом дат

Ограничения по времени - основные операции должны выполняться не более чем за 1 с.

#### Особенности:
* нет необходимости поиска вверх
* нет необходимости перемешать ветки комментариев
* нет необходимости удалять ветки комментариев, только терминальные узлы
* количество операций на чтение будет на порядок больше чем операций записи, но и записи не будут редкими

Так же необходимо иметь возможность выбрать верхний слой узлов для каждой сущности.
Нет необходимости в перемещении

По условию количество чтений дерева на порядок превышает количество записей,
но и то и другое имеет ограничение на время выполнения.

## Решение задачи:</h2>

#### Возможное алгоритмы:
* Adjacency List, AL («список смежности»)
* Materialized Path, MP («материализованный путь»)
* Nested Sets, NS («вложенные множества»)
* Closure Table, CT («таблица связей»)

Решение было построено на основе Closure Table, с сохранением ближайшего предка (nearest_ancestor_id) и уровня вложенности (level).
##### Плюсы:
* быстрая выборка потомков первого уровня
* быстрая выборка потомков с сохранением структуры
* быстрое добавление
* быстрое удаление
* сохранение целостности данных

##### Минусы:
* дублирование данных
* таблица связей в худшем случае имеет размер N^2, где N размер оригинальной таблицы

Для реализации был выбран Python 3.5 (aiohttp, aiomysql, alembic) и MySQL 5.6.19

## АПИ:

### User:

##### 1) Получение списка всех пользователей

Тип запроса: GET

URL: '/user/'

##### 2) Получение информации о пользователе по user_id

Тип запроса: GET

URL: '/user/{user_id}'

##### 3) Добавление пользователя

Тип запроса: POST

URL: '/user/'

Поля:
* 'name' - имя пользователя, обязательное уникальное

##### 4) Удаление пользователя по user_id

Тип запроса: DELETE

URL: '/user/{user_id}'

##### 5) Выгрузка всех комментариев пользователя в формате xml

Тип запроса: GET

URL: '/user/{user_id}/comments/'

### Entity:

##### 1) Получение списка всех сущностей, которые можно комментировать

Тип запроса: GET

URL: '/entity/'

##### 2) Получение информации о сущности по entity_id

Тип запроса: GET

URL: '/entity/{entity_id}'

##### 3) Добавление сущности

Тип запроса: POST

URL: '/entity/'

Поля:
* 'name' - название сущности, обязательное
* 'type' - тип сущности, обязательное
Сочетание name + type является уникальным

##### 4) Удаление сущности по entity_id

Тип запроса: DELETE

URL: '/entity/{entity_id}'

### Comment:

##### 1) Получение списка всех комментариев, первого уровня для заданной entity_id, которые можно комментировать

Тип запроса: GET

URL: '/comment/'

Поля:
* 'entity_id' - id сущности, обязательное
* 'page' - номер страницы выдачи

При выборке за раз отдается ограниченное количество результатов.

##### 2) Получение информации о комментария по comment_id

Тип запроса: GET

URL: '/comment/{comment_id}'

##### 3) Добавление комментария

Тип запроса: POST

URL: '/comment/'

Поля:
* 'entity_id' - id сущности, обязательное
* 'user_id' - id пользователя, обязательное
* 'text' - текст комментария, обязательное
* 'ancestor_id' - id предка

Сущность к которой привязан потомок должна совпадать с ущностью из запроса на создание.

##### 4) Удаление комментария у которого нет потомков, по comment_id

Тип запроса: DELETE

URL: '/comment/{comment_id}'

##### 5) Выборка дерева комментариев

Тип запроса: GET

URL: '/comment/search'

Поля:
* 'entity_id' - id сущности
* 'comment_id' - id комментария

##### 6) Обновление комментария по comment_id

Тип запроса: PUT

URL: '/comment/{comment_id}'

Поля:
* 'text' - текст комментария, обязательное
