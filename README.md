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

1. **Відкрийте браузер** і перейдіть на http://localhost:5000
2. **Виберіть категорію** з випадаючого списку (sticks-sr, skates-sr і т.п.).
   - Парсер намагається знайти відповідну сторінку цієї категорії як на prohockey.com.ua,
     так і на перевірюваних зовнішніх сайтах. Якщо посилання не містить
     категорії, скрипт обітеться до головної сторінки і спробує виявити потрібний
     розділ за ключовим словом.
   - Вказаний фільтр також використовується для відсіювання товарів: із результатів
     будуть утримані тільки ті позиції, де назва або посилання містять ключову
     фразу. Якщо не вказано, всі знайдені позиції перевіряться.
3. **Введіть посилання на інші магазини** у полі вводу (можна кілька URL).
4. Якщо потрібно, натисніть **"Додати ще посилання"**.
5. **Натисніть кнопку "Перевірити відсутні"**.
6. **Почекайте**, поки скрипт виконає запити; поруч з формою зʼявиться статистика та
   таблиця результатів. Таблиця містить товари, яких **немає на prohockey.com.ua**,
   з колонками ціна/валюта, джерело, посилання та статус.

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

## Приклади посилань для парсингу

- https://example.com/shop
- shop.example.com/products
- https://goods.example.com/catalog
- example.com/items

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
