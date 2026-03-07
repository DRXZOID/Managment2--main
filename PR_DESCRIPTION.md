PR: Cleanup — Product DTO, service UI, validation, logging, tests

Краткое описание
-----------------
Этот PR делает инкрементальную, но целенаправленную очистку и улучшения в проекте, не меняя архитектуру и интерфейсы (кроме небольших расширений API для удобства UI):

- Полностью поддержан согласованный Product DTO в `ProductSyncService`:
  - предпочитается числовое поле `price`, при его отсутствии парсится `price_raw`;
  - `currency` явно из DTO имеет приоритет над распознанным;
  - `source_url` предпочитается для источника, legacy-поля используются как fallback;
  - реализована централизованная функция нормализации DTO `_normalize_product_dto`.

- Улучшен UX страницы сервиса (`templates/service.html`):
  - заменены browser alert(...) на inline-статусы (`status-pill`);
  - исправлена метка кнопки "Скрести товари" -> "Синхронізувати товари";
  - после успешной синхронизации товаров UI обновляет:
    - блок текущих запусков (/api/scrape-status);
    - таблицу категорий для соответствующего магазина (включая новое поле `product_count`).

- Добавлен `product_count` к списку категорий API (`/api/stores/<id>/categories` и `/api/categories`), реализовано через агрегированный запрос в `category_repository.count_products_by_category`.

- Добавлена базовая валидация в `CategorySyncService`:
  - категории без `name` пропускаются;
  - подсчитываются и логируются skipped-invalid кейсы, записываются диагностические данные в `scrape_run.metadata_json` (skipped_invalid_categories, validation_error_counts, validation_errors_sample).

- Backend-валидация маппингов (`MappingService.create_category_mapping`):
  - `reference_category_id` должен принадлежать reference store;
  - `target_category_id` не должен принадлежать reference store;
  - reference и target не должны принадлежать одному магазину;
  - редактирование маппинга (`PUT`) меняет только metadata (match_type, confidence).

- Frontend: исправлен submit mapping; в режиме редактирования не отправляются `reference_category_id` и `target_category_id`.

- Логирование: заменены оставшиеся `print(...)` вызовы на `logger.*` в ключевых модулях (`app.py`, `http_client.py`, `demo_cache.py`).

- Тесты: добавлены/обновлены тесты для Product DTO и category sync; прогнан полный тест-ран (50 passed, 0 warnings).

Детальный план коммитов (рекомендуемая разбивка)
-----------------------------------------------
Я предлагаю разбить изменения на логичные коммиты (каждый коммит — отдельная логическая группа файлов):

1) feat(product-dto): normalize product DTO in ProductSyncService
   - files: pricewatch/services/product_sync_service.py
   - сообщение: "product: centralize product DTO normalization in ProductSyncService (prefer numeric 'price', fallback to 'price_raw', respect 'currency', prefer 'source_url')"

2) feat(category-count): add product_count to categories API
   - files: pricewatch/db/repositories/category_repository.py, app.py
   - сообщение: "api: include product_count per category in store categories endpoint (aggregated query)"

3) feat(category-sync): add lightweight validation and diagnostics
   - files: pricewatch/services/category_sync_service.py
   - сообщение: "service: skip invalid categories (missing name), log and record diagnostics in scrape_run.metadata_json"

4) feat(mapping-validation): backend mapping validation and immutable pair edit
   - files: pricewatch/services/mapping_service.py, app.py (payload handling)
   - сообщение: "mapping: validate category stores on create, keep pair immutable on edit"

5) feat(ui-service): service UI inline status and update after sync
   - files: templates/service.html
   - сообщение: "ui: replace alert() with inline status, refresh categories & scrape status after product sync; fix action label"

6) fix(logging): replace prints with logger
   - files: app.py, http_client.py, demo_cache.py
   - сообщение: "chore(logging): replace print() with structured logger calls"

7) tests: add/update tests for DTO, category sync
   - files: tests/test_product_dto.py, tests/test_category_sync_service.py, tests/test_category_mappings_api.py (tz fix)
   - сообщение: "test: add product DTO normalization tests; category sync validation tests; fix tz usage in mapping tests"

8) docs: update README with DTO and mapping rules
   - files: README.md
   - сообщение: "docs: document product DTO contract and mapping validation rules"

9) final: minor fixes and formatting
   - files: small adjustments (app.py minor typing fixes)
   - сообщение: "chore: minor typing fixes and tidy up"

Как подготовить локально аккуратные коммиты
------------------------------------------
Если хотите, чтобы коммиты были именно такие, выполните в репозитории последовательность (пример):

```bash
# создать ветку
git checkout -b feature/cleanup-dto-ui-validation

# 1) product DTO
git add pricewatch/services/product_sync_service.py
git commit -m "product: centralize product DTO normalization in ProductSyncService (prefer numeric 'price', fallback to 'price_raw', respect 'currency', prefer 'source_url')"

# 2) product_count API
git add pricewatch/db/repositories/category_repository.py app.py
git commit -m "api: include product_count per category in store categories endpoint (aggregated query)"

# 3) category sync validation
git add pricewatch/services/category_sync_service.py
git commit -m "service: skip invalid categories (missing name), log and record diagnostics in scrape_run.metadata_json"

# 4) mapping validation + frontend payload change
git add pricewatch/services/mapping_service.py templates/service.html app.py
git commit -m "mapping: validate category stores on create, keep pair immutable on edit; update frontend submit payload"

# 5) UI inline status and refresh logic
git add templates/service.html
git commit -m "ui: replace alert() with inline status, refresh categories & scrape status after product sync; fix action label"

# 6) logging replacements
git add app.py http_client.py demo_cache.py
git commit -m "chore(logging): replace print() with structured logger calls"

# 7) tests
git add tests/test_product_dto.py tests/test_category_sync_service.py tests/test_category_mappings_api.py
git commit -m "test: add product DTO normalization tests; category sync validation tests; fix tz usage in mapping tests"

# 8) docs
git add README.md
git commit -m "docs: document product DTO contract and mapping validation rules"

# 9) final tidy
git add app.py
git commit -m "chore: minor typing fixes and tidy up"

# push branch
git push -u origin feature/cleanup-dto-ui-validation

# create PR (if using GitHub CLI)
gh pr create --title "Cleanup: product DTO, service UI, validation, logging" --body-file PR_DESCRIPTION.md --base main
```

Если у вас нет `gh` (GitHub CLI), то выполните `git push` и создайте PR через веб-интерфейс, указав в описании содержимое `PR_DESCRIPTION.md`.

Тесты и проверка
-----------------
Перед созданием PR прогоните тесты локально:

```bash
PYTHONPATH=. pytest -q
```

Ожидаемый результат: все тесты проходят (в моей среде получилось 50 passed, 0 warnings).

Содержимое PR body
-------------------
В `PR_DESCRIPTION.md` (в корне репозитория) уже записано краткое описание PR и план коммитов. Используйте его как тело PR. Я также могу записать более детальное описание (changelog) по коммитам, если нужно.

Если вы хотите, я могу:
- попытаться автоматически создать аккуратные коммиты в этом репозитории (я пробовал сделать коммиты, но текущее рабочее дерево содержит множество модификаций; безопаснее позволить вам выполнить финальную организацию и пуш),
- или сгенерировать патч/zip с изменениями для самостоятельного применения.

Какой вариант предпочитаете: предоставить готовый набор git-команд и PR body (уже подготовлено), или чтобы я попытался окончательно сгруппировать и закоммитить всё прямо сейчас в этой среде? (Второй вариант возможен, но требует аккуратного разбора рабочего дерева и может создать менее удобную историю; первый вариант даёт вам полный контроль.)

Файл с описанием PR сохранён: `PR_DESCRIPTION.md`.

