# Порівняння товарів за посиланнями

Веб-застосунок для парсингу товарів з декількох сайтів та їх порівняння.

## Можливості

✅ Вставити посилання на декілька сайтів  
✅ Автоматичний парсинг товарів  
✅ Порівняння товарів за назвою та артикулом  
✅ Групування схожих товарів  
✅ Вивід у таблиці з колонками: Артикул, Назва, Модель  
✅ Зручний інтерфейс  

*Поточна архітектура:* логіка парсингу винесена в плагіни (адаптери) для кожного магазину, які автоматично підхоплюються реєстром та вибираються за доменом URL. Референсним сайтом є `prohockey.com.ua`, всі інші URL порівнюються з його каталогом.

## Встановлення

### 1. Встановіть Python 3.7+
https://www.python.org/downloads/

### 2. Відкрийте термінал у папці проєкту

```bash
cd C:\Users\user\Desktop\"Managment2--main
```

### 3. Створіть віртуальне оточення

```bash
python -m venv venv
```

### 4. Активуйте віртуальне оточення

**У Windows:**
```bash
venv\Scripts\activate
```

**У macOS/Linux:**
```bash
source venv/bin/activate
```

### 5. Встановіть залежності

```bash
pip install -r requirements.txt
```

### Корисні поради

- Рекомендовано оновити `pip` перед встановленням залежностей:
```powershell
python -m pip install --upgrade pip
```
- Завжди використовуйте `python -m pip` щоб впевнено працювати з тим самим інтерпретатором:
```powershell
python -m pip install -r requirements.txt
```
- Активація в PowerShell може вимагати дозволу виконання скриптів:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
venv\Scripts\Activate.ps1
```
- Скрипт парсеру також доступний окремо: щоб запустити CLI-скрейпер без веб-інтерфейсу:
```powershell
python parser.py
```
- CORS вже додано у `app.py` (через `flask-cors`), тому фронтенд має працювати при запуску `python app.py`.

## Запуск застосунку

```bash
python app.py
```

Доступно на http://localhost:5000. Головна сторінка тепер читає ТІЛЬКИ БД (жодного прямого скрапінгу) й дозволяє обрати reference/target магазини, категорії та переглянути товари. Для запуску синхронізацій, редагування мапінгів і перегляду історії використовуйте `/service`.

## Адмінський UI

- `/` — користувацька сторінка. Всі дані зчитуються з `stores/categories/products` таблиць. Якщо записи застарілі, користувач бачить підказку перейти на сервісну панель.
- `/service` — операційна панель з трьома вкладками: Категорії (синхронізація та запуск скрапу), Мапінги (CRUD для category_mappings) та Історія (таблиця scrape_runs з пагінацією та REST-полінгом `/api/scrape-status`).

### Класифікація API-ендпоінтів

#### DB-first (основний флоу)

| Метод | Шлях | Опис |
|---|---|---|
| `GET` | `/api/stores` | Список магазинів з БД. **Тільки читання** — ніколи не запускає синхронізацію. |
| `GET` | `/api/stores/<id>/categories` | Категорії магазину з БД. |
| `GET` | `/api/categories/<id>/products` | Товари категорії з БД. |
| `GET` | `/api/categories/<id>/mapped-target-categories` | Замаплені цільові категорії для обраної reference-категорії (з метаданими маппінгу). |
| `GET` | `/api/adapters` | Список зареєстрованих адаптерів. |
| `GET` | `/api/categories` | Категорії reference-магазину з БД. |
| `POST` | `/api/comparison` | Порівняння за маппінгами (дані з БД). `reference_category_id` обов'язковий, `target_category_id` — опціональний. |

#### Service / admin

| Метод | Шлях | Опис |
|---|---|---|
| `POST` | `/api/admin/stores/sync` | Синхронізує registry → БД. Захищений `ENABLE_ADMIN_SYNC`. |
| `POST` | `/api/stores/<id>/categories/sync` | Скрапить категорії і зберігає в БД. |
| `POST` | `/api/categories/<id>/products/sync` | Скрапить товари категорії і зберігає в БД. |
| `GET` | `/api/category-mappings` | Список маппінгів категорій. |
| `POST` | `/api/category-mappings` | Створити маппінг. Пара категорій незмінна після створення. |
| `PUT` | `/api/category-mappings/<id>` | Змінити лише метадані (`match_type`, `confidence`). |
| `DELETE` | `/api/category-mappings/<id>` | Видалити маппінг. |
| `POST` | `/api/category-mappings/auto-link` | Авто-маппінг: автоматично створює `category_mappings` за точним збігом `normalized_name`. |
| `GET` | `/api/scrape-runs` | Історія запусків. |
| `GET` | `/api/scrape-runs/<id>` | Деталі конкретного запуску. |
| `GET` | `/api/scrape-status` | Поточні/останні запуски (полінг для service page). |
| `GET` | `/api/adapters/<name>/categories` | Категорії конкретного адаптера (з живим запитом). |

#### Legacy / internal / debug

Ці ендпоінти залишені для зворотної сумісності і внутрішнього тестування.
**Не є частиною основного флоу** і можуть бути видалені в наступних версіях.

| Метод | Шлях | Опис |
|---|---|---|
| `GET` | `/api/reference-products` | Живий скрапінг reference-адаптера по категорії. |
| `POST` | `/api/check` | Живий скрапінг довільних URL для порівняння. |
| `POST` | `/api/parse-example` | Розбір HTML-фрагменту таблиці. Debug-хелпер. |

> **Видалено:** `POST /api/scrape` — раніше повертав 501, тепер видалений повністю.

### Адмінська синхронізація магазинів

- `/api/stores` читає тільки з бази (`StoreService.sync_with_registry` більше не викликається всередині GET-запитів).
- Сторінку `/service` доповнено кнопкою для ручного запиту `POST /api/admin/stores/sync`, який ітерує registry, оновлює записи та повертає вже збережені магазини.
- Поведінка ручної синхронізації керується конфіг-флагом `ENABLE_ADMIN_SYNC` (за замовчуванням `True`). Якщо він `False`, адмінський endpoint повертає 404 і UI ховає контрол для синхронізації.

### `scrape_run.metadata_json`

`Fail`/`success` метадані тепер містять діагностичні лічильники та обмежений список прикладів помилок:

- `skipped_invalid_products` — загальна кількість товарів, які не було збережено (причинами можуть бути відсутня назва, URL та ін.).
- `skipped_missing_url` — підмножина, де причиною було відсутнє або пусте `product_url`.
- `validation_error_counts` — мапа вигляду `reason -> count` для швидкого отримання частот помилок.
- `validation_errors_sample` — обмежений (10 записів) список прикладів, що містить `type`, `message` та додаткові поля (`product_name`, `product_url`, `source_url`, `adapter_name`, `category_id`, `category_name`).

Детальний лог протоколює`reason`, `adapter_name`, `store_id`, `category_id`, `product_name` та `source_url` через сислог `warning`.

## Mapping-driven порівняння

Порівняння категорій побудоване навколо **`category_mappings`** — таблиці зв'язків між reference і target категоріями.

### Ключові правила

- Порівняння **дозволено лише для замаплених пар** категорій.  
  Якщо для вибраної reference-категорії немає жодного маппінгу — кнопка «Порівняти» заблокована, а API повертає `400`.
- Маппінги підтримують **one-to-many** і **many-to-many**:  
  одна reference-категорія може мати кілька target-категорій (і навпаки).
- Дані порівняння читаються **виключно з БД** — без живого скрапінгу.

### Сценарій використання

1. Синхронізуйте категорії на `/service` → вкладка «Категорії».
2. Створіть маппінги вручну (кнопка «Створити мапінг») або автоматично (кнопка «⚡ Авто-маппінг за назвою»).
3. Відкрийте `/` → виберіть reference-магазин і категорію.
4. У правому списку з'являться лише замаплені target-категорії.
5. Натисніть «Порівняти категорії».

### `POST /api/comparison`

**Запит:**
```json
{
  "reference_category_id": 1,
  "target_category_id": 5
}
```
`target_category_id` — **опціональний**. Якщо опущений — порівняння відбувається з усіма замапленими target-категоріями для даної reference-категорії.

**Відповідь:**
```json
{
  "reference_category": {"id": 1, "name": "Ковзани", "store_name": "RefShop", "is_reference": true},
  "mapped_target_categories": [
    {"target_category_id": 5, "name": "Ковзани", "match_type": "exact", "confidence": 1.0}
  ],
  "comparisons": [
    {
      "target_category": {"id": 5, "name": "Ковзани", "store_name": "TargetShop", "is_reference": false},
      "summary": {
        "reference_total": 12, "target_total": 10,
        "matched": 8, "only_in_reference": 4, "only_in_target": 2, "ambiguous": 0
      },
      "matches": [
        {"reference_product": {...}, "target_product": {...}, "score": 95.0, "match_source": "stored"}
      ],
      "ambiguous": [],
      "only_in_reference": [...],
      "only_in_target": [...]
    }
  ]
}
```

**Помилки (400):**
- `reference_category_id` не знайдено або не є reference store
- `target_category_id` вказано, але пара не існує в `category_mappings`
- `target_category_id` не вказано і маппінгів немає ("Для цієї категорії ще не створено меппінг")

### `GET /api/categories/<id>/mapped-target-categories`

Повертає список target-категорій, замаплених до обраної reference-категорії:

```json
{
  "reference_category_id": 1,
  "mapped_target_categories": [
    {
      "target_category_id": 5,
      "name": "Ковзани",
      "normalized_name": "kovzany",
      "store_id": 2,
      "store_name": "TargetShop",
      "match_type": "exact",
      "confidence": 1.0,
      "mapping_id": 3
    }
  ]
}
```

Використовується головною сторінкою для фільтрації target-категорій після вибору reference-категорії.

### `POST /api/category-mappings/auto-link`

Автоматично створює `category_mappings` на основі **точного збігу `normalized_name`** між reference і target категоріями:

**Запит:**
```json
{"reference_store_id": 1, "target_store_id": 2}
```

**Відповідь:**
```json
{
  "created": [
    {
      "reference_category_id": 1, "reference_category_name": "Ковзани",
      "target_category_id": 5, "target_category_name": "Ковзани",
      "match_type": "exact", "confidence": 1.0
    }
  ],
  "skipped_existing": [
    {"reference_category_id": 2, "target_category_id": 7}
  ],
  "summary": {"created": 1, "skipped_existing": 1, "skipped_no_norm": 0}
}
```

- **Не створює дублікатів** — якщо маппінг вже існує, пара потрапляє в `skipped_existing`.
- `skipped_no_norm` — кількість reference-категорій без `normalized_name`.
- Кнопка **«⚡ Авто-маппінг за назвою»** на `/service` → «Мапінги» виконує цей запит.

### Сортування матчів у відповіді `/api/comparison`

| `match_source` | Значення |
|---|---|
| `stored` | Збережений `ProductMapping` (підтверджено вручну або через confirm-match). |
| `heuristic` | Підібрано евристичним алгоритмом на основі нормалізованої назви. |

Stored matches мають пріоритет — продукти, покриті `ProductMapping`, не потрапляють до heuristic-matching.

## База даних та міграції

- ORM: SQLAlchemy 2.x, SQLite за замовчуванням (`sqlite:///pricewatch.db`), легка міграція на PostgreSQL через `DATABASE_URL`.
- Ініціалізація: при старті створюються таблиці, крім випадків `FLASK_ENV=production` або `DB_SKIP_CREATE_ALL=1`.
- Налаштування через ENV/Flask config:
  - `DATABASE_URL` — рядок підключення (наприклад, `postgresql+psycopg2://user:pass@host/db` або in-memory для тестів `sqlite+pysqlite:///:memory:`).
  - `DB_DEBUG_SQL` — `1/true` вмикає SQL echo.
  - `DB_SKIP_CREATE_ALL` — пропускає автосоздання таблиць.
  - `FLASK_ENV=production` — також пропускає автосоздання таблиць.

### Alembic

```bash
export DATABASE_URL=sqlite:///pricewatch.db   # або свій URL
PYTHONPATH=. alembic upgrade head
```

Щоб створити нову міграцію після змін у `pricewatch/db/models.py`:

```bash
PYTHONPATH=. alembic revision --autogenerate -m "short description"
```

Далі застосуйте `PYTHONPATH=. alembic upgrade head`.

### Приклад сценарію

`examples/db_usage.py` показує: створення магазинів, запуск scrape_run, upsert категорій/товарів, запис історії цін і створення маппінгів. Запуск:

```bash
python examples/db_usage.py
```

## Тести

Запуск всіх тестів з кореня проєкту (рекомендується):

```bash
PYTHONPATH=. pytest -q
```

Показати детальний звіт по тестах:

```bash
PYTHONPATH=. pytest
```

Запустити конкретний файл або набір тестів:

```bash
PYTHONPATH=. pytest pricewatch/tests/test_hockeyworld_pagination.py -q
# або
PYTHONPATH=. pytest tests/test_check.py -q
```

Запуск тестів у певних папках:

```bash
PYTHONPATH=. pytest pricewatch/tests tests
```

Зупинитись при першій помилці:

```bash
PYTHONPATH=. pytest -x
```

Паралельний запуск (потрібен pytest-xdist):

```bash
pip install pytest-xdist
PYTHONPATH=. pytest -n auto
```

Очищення кешу тестів (папки з кешем можуть з'являтись у `tests/` або `pricewatch/tests`):

```bash
rm -rf tests/.cache
rm -rf pricewatch/tests/.cache
```

Поради:

- Важливо запускати тести з кореня проєкту і вказувати `PYTHONPATH=.` — це забезпечує коректний імпорт локального пакету `pricewatch` і модулів з `tests`.
- Перед запуском тестів активуйте віртуальне оточення та переконайтесь, що залежності встановлені:

```bash
source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

- Якщо тестові скрипти імпортують локальні утиліти (наприклад `test_utils`), переконайтесь, що ви запускаєте pytest з кореня проекту або додайте `sys.path` в тестових скриптах для сумісності.

## Як користуватися

1. **Запустіть застосунок** і відкрийте http://localhost:5000 у браузері.
2. **Головна сторінка (`/`)** — вибір reference-магазину, категорії та target-магазину.  
   Всі дані (магазини, категорії, товари) читаються **виключно з БД**. Жодного живого скрапінгу на головній сторінці не відбувається.
3. **Якщо БД порожня або застаріла**, скористайтеся сервісною панеллю:
   - Перейдіть на `/service`.
   - Вкладка **«Категорії»** — оберіть магазин → натисніть «Sync categories» для оновлення категорій з сайту, потім «Sync products» для оновлення товарів.
   - Вкладка **«Мапінги»** — CRUD для `category_mappings` (зв'язок ref-категорії ↔ target-категорії).
   - Вкладка **«Історія»** — таблиця `scrape_runs` з автооновленням статусу поточних запусків.
4. **Порівняння товарів** — після наповнення БД, на головній сторінці оберіть reference-категорію та target-категорію. Результат будується з даних у БД через `POST /api/comparison`.

## Структура проєкту

```
Managment2--main/
├── app.py                          # Flask сервер + init DB
├── parser.py                       # сумісний фасад
├── http_client.py                  # HTTP клієнт/обгортка
├── pricewatch/
│   ├── core/                       # ядро парсингу/нормалізації
│   ├── db/                         # SQLAlchemy моделі, конфіг, репозиторії, тести
│   └── shops/                      # адаптери магазинів
├── migrations/                     # Alembic env + versions/
├── examples/db_usage.py            # приклад роботи з БД
├── templates/                      # фронтенд
└── README.md
```

## Технології

- **Backend:** Flask, BeautifulSoup4 (Python)
- **Frontend:** HTML5, CSS3, JavaScript
- **Парсинг:** requests, lxml, beautifulsoup4
- **Порівняння:** difflib, python-levenshtein


## Усунення неполадок

### Помилка "ModuleNotFoundError"
Переконайтесь, що активовано віртуальне оточення і встановлено залежності:
```bash
pip install -r requirements.txt
```

### Порт 5000 зайнятий
Якщо порт зайнятий, змініть порт у `app.py`:

In `app.py` change the run call to use a different port, for example: app.run(debug=True, port=8000) (change 5000 to 8000).

### Сайт не парситься
Деякі сайти можуть блокувати парсинг. У такому випадку:
1. Перевірте, чи URL правильний
2. Перевірте підключення до інтернету
3. Спробуйте інший URL

## Примітки щодо парсингу

- Для більшості магазинів використовується загальний механізм із селекторами.
- Для специфічних сайтів доступні власні адаптери.
- Реєстр адаптерів створюється один раз під час запуску застосунку і повторно використовується.
- `parser.py` збережено як фасад для сумісності імпортів.

## Ліцензія

MIT

## Контакт

Якщо у вас є питання — відкрийте issue.

## Product DTO контракт (важно)

При синхронізації товарів сервис предпочитает явні значення з DTO по наступному правилу:

- `price` (числове значення) — переважне поле; якщо присутнє і валідне, використовується напряму.
- `price_raw` — використовується як запасний варіант, коли `price` не задане; розпізнавання витягує числову частину і валюту.
- `currency` — якщо вказана явно в DTO, має пріоритет над розпізнаною з `price_raw`.
- `source_url` — надається перевага для атрибута джерела; legacy-поля (`source_site`, `url`) використовуються лише як fallback.

Сервис підтримує і словникові об'єкти, і об'єктні DTO (SimpleNamespace-совместимі).


## Правила валидації маппінгів

Backend на етапі створення маппінга (`POST /api/category-mappings`) виконує доменні перевірки:

- `reference_category_id` повинен належати категорії в reference store (store.is_reference == True).
- `target_category_id` не повинен належати reference store.
- reference і target категорії не повинні належати одному і тому ж магазині.

При редагуванні маппінга (`PUT /api/category-mappings/<id>`) пара категорій незмінна — дозволено змінювати лише метадані (наприклад `match_type`, `confidence`).
