# Как я разбираю и меняю проект

1. Я запускаю README demo и читаю latest/history. Намеренные failure — часть проверки.
2. Я читаю domain.fixture: семь конкретных строк дают пять доставок выбранных суток.
3. В domain.parse_csv я вижу типы/ограничения; quality не исправляет плохую строку.
4. В pipeline я вижу три assets и две blocking checks. Именно graph блокирует summary.
5. В storage я прослеживаю immutable object → optional failure → atomic pointer.
6. Я меняю один контракт и выполняю tests/smoke, затем упражнение из NOTES.

| Файл | Для чего я его держу отдельно |
| --- | --- |
| delivery_assets/domain.py | Я могу проверять правила и cutoff без Dagster/filesystem |
| delivery_assets/pipeline.py | Я связываю assets/checks/resources и собственный instance |
| delivery_assets/storage.py | Я контролирую filesystem commit и целостность latest |
| delivery_assets/__main__.py | Я разбираю CLI аргументы, не размещая здесь расчёт |
| tests/test_project.py | Я проверяю данные, реальные gates и сбои публикации |
| scripts/smoke.py | Я проверяю новый процесс и публичные команды |
| scripts/package_release.py | Я ограничиваю публикацию явным allowlist и SHA256 |
| requirements.in/lock | Я отделяю прямую dependency от полного универсального набора |

Чтобы добавить WH-C, я сначала меняю допустимые warehouse, fixture и ожидаемый
отчёт. Для новой формулы меняю ENGINE вместе с тестами: старый request_id не должен
обозначать другой расчёт. Новая check получает собственное имя/metadata и blocking
policy. Для расписания потребуется отдельная история; сейчас постоянных служб нет.
В IDE я открываю папку проекта, а не родительский домашний Git. Локальные данные
и Dagster journal находятся в ignored workspace; их не коммичу.

В scripts/ci.py я последовательно устанавливаю lock и запускаю проверки с check=True;
это единая граница ошибки для GitHub Actions в Linux и Windows.
