# Все мои технологии и зависимости

27.10.2026. Прямая runtime dependency — Dagster1.13.27 (официальный release26.10).
Я сверил текущую PyPI страницу/API и документацию1.13.27. Python>=3.12,<3.13,
локально CPython3.12.15. Использую stdlib csv/json/dataclasses/datetime/hashlib,
pathlib/tempfile/os/argparse/unittest/subprocess/zipfile. SQLite3.53.1локально
использует сам Dagster через SQLAlchemy; свою SQL схему я не создаю.

Я зафиксировал52distribution pins и hashes в requirements.lock через uv0.13.1
pip compile --universal --python-version3.12 --generate-hashes. На Linux активны48,
четыре условные зависимости относятся к Windows. Requirements.in содержит только
прямую dependency. Большинство библиотек таблицы я не импортирую непосредственно:
они обслуживают Dagster и его служебные возможности, а не новые функции проекта.

| Библиотека | Версия | Для чего нужна | Платформа | Официальная страница |
| --- | --- | --- | --- | --- |
| alembic | 1.20.1 | Миграции служебного SQL storage Dagster | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/alembic/1.20.1/) |
| annotated-types | 0.8.0 | Ограничения типов Pydantic | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/annotated-types/0.8.0/) |
| antlr4-python3-runtime | 4.13.2 | Разбор языка selection Dagster | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/antlr4-python3-runtime/4.13.2/) |
| certifi | 2026.10.23 | Корневые сертификаты HTTP клиента | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/certifi/2026.10.23/) |
| charset-normalizer | 3.5.2 | Определение кодировки HTTP | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/charset-normalizer/3.5.2/) |
| click | 8.5.0 | CLI инфраструктура Dagster | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/click/8.5.0/) |
| colorama | 0.4.6 | ANSI вывод Windows | Windows | [PyPI](https://pypi.org/project/colorama/0.4.6/) |
| coloredlogs | 14.0 | Оформление служебных логов | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/coloredlogs/14.0/) |
| dagster | 1.13.27 | Assets,checks,execution и run journal | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/dagster/1.13.27/) |
| dagster-pipes | 1.13.27 | Протокол внешних процессов Dagster; напрямую не вызываю | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/dagster-pipes/1.13.27/) |
| dagster-shared | 1.13.27 | Общие утилиты Dagster | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/dagster-shared/1.13.27/) |
| docstring-parser | 0.18.0 | Разбор docstrings definitions | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/docstring-parser/0.18.0/) |
| filelock | 4.2.4 | Локальные locks библиотек; мой workspace lock реализован отдельно | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/filelock/4.2.4/) |
| fsspec | 2026.9.0 | Абстракция filesystem для зависимостей | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/fsspec/2026.9.0/) |
| grpcio | 1.85.0 | gRPC инфраструктура Dagster; сервер я не запускаю | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/grpcio/1.85.0/) |
| grpcio-health-checking | 1.81.1 | gRPC health protocol библиотеки | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/grpcio-health-checking/1.81.1/) |
| humanfriendly | 10.0 | Форматирование человекочитаемых величин | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/humanfriendly/10.0/) |
| idna | 3.20 | Имена DNS HTTP клиента | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/idna/3.20/) |
| jinja2 | 3.1.6 | Шаблоны служебных инструментов | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/jinja2/3.1.6/) |
| mako | 1.4.3 | Шаблоны SQL migrations Alembic | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/mako/1.4.3/) |
| markdown-it-py | 4.2.0 | Разбор Markdown для Rich | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/markdown-it-py/4.2.0/) |
| markupsafe | 3.0.4 | Экранирование шаблонов | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/markupsafe/3.0.4/) |
| mdurl | 0.1.2 | URL обработка Markdown | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/mdurl/0.1.2/) |
| packaging | 26.3 | Сравнение версий и package metadata | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/packaging/26.3/) |
| pathlib-abc | 0.5.2 | Filesystem path interfaces | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/pathlib-abc/0.5.2/) |
| platformdirs | 4.13.5 | Платформенные каталоги | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/platformdirs/4.13.5/) |
| protobuf | 6.33.6 | Сообщения gRPC | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/protobuf/6.33.6/) |
| psutil | 7.2.2 | Информация о процессах Windows для Dagster | Windows | [PyPI](https://pypi.org/project/psutil/7.2.2/) |
| pydantic | 2.14.1 | Проверка Settings/resource config | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/pydantic/2.14.1/) |
| pydantic-core | 2.50.1 | Движок валидации Pydantic | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/pydantic-core/2.50.1/) |
| pygments | 2.21.0 | Подсветка Rich | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/pygments/2.21.0/) |
| pyreadline3 | 3.5.6 | Консольный ввод Windows | Windows | [PyPI](https://pypi.org/project/pyreadline3/3.5.6/) |
| python-dotenv | 1.2.4 | Возможности конфигурации Dagster; .env сам не загружаю | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/python-dotenv/1.2.4/) |
| pytz | 2026.5 | Timezone поддержка Dagster; business cutoff у меня UTC | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/pytz/2026.5/) |
| pywin32 | 312 | Windows API инфраструктура Dagster | Windows | [PyPI](https://pypi.org/project/pywin32/312/) |
| pyyaml | 6.0.3 | Настройки instance Dagster | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/pyyaml/6.0.3/) |
| requests | 2.34.2 | HTTP возможности зависимостей; внешние источники я не вызываю | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/requests/2.34.2/) |
| rich | 15.0.0 | Консольное форматирование | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/rich/15.0.0/) |
| six | 1.17.0 | Совместимость служебных библиотек | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/six/1.17.0/) |
| sqlalchemy | 2.1.6 | Служебные SQLite run/event tables Dagster | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/sqlalchemy/2.1.6/) |
| structlog | 26.1.0 | Структурные логи | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/structlog/26.1.0/) |
| tabulate | 0.10.0 | Консольные таблицы Dagster | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/tabulate/0.10.0/) |
| tomli | 2.5.0 | Чтение TOML инфраструктуры | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/tomli/2.5.0/) |
| tomlkit | 0.15.2 | Редактирование TOML инфраструктуры | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/tomlkit/0.15.2/) |
| toposort | 1.10 | Топологический порядок графа | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/toposort/1.10/) |
| tqdm | 4.70.1 | Консольные progress helpers | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/tqdm/4.70.1/) |
| typing-extensions | 4.16.0 | Обратная совместимость typing | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/typing-extensions/4.16.0/) |
| typing-inspection | 0.4.4 | Интроспекция Pydantic типов | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/typing-inspection/0.4.4/) |
| tzdata | 2026.5 | Timezone database библиотек | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/tzdata/2026.5/) |
| universal-pathlib | 0.3.10 | Filesystem path abstraction | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/universal-pathlib/0.3.10/) |
| urllib3 | 2.8.0 | HTTP транспорт Requests | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/urllib3/2.8.0/) |
| watchdog | 6.0.0 | Наблюдение за файлами в инструментах Dagster; watcher/daemon не запускаю | Все поддерживаемые ОС | [PyPI](https://pypi.org/project/watchdog/6.0.0/) |

Инструменты: Git2.53.0локально,GitHub Actions (Ubuntu24.04/Windows2025),
actions/checkout7.0.1SHA3d3c42e5aac5ba805825da76410c181273ba90b1,
actions/setup-python7.0.0SHA5fda3b95a4ea91299a34e894583c3862153e4b97.
На CI installer pip входит в venv Python; runtime pins/hashes от него не зависят.
Windows Python3.12.10 выбрал по доступному официальному python-versions manifest,
Linux3.12.15 сохраняю. Фактические CI outcomes описываю отдельно в VALIDATION.

Официальные API: [assets/checks](https://dagster.io/docs/guides/test/asset-checks),
[materialize](https://dagster.io/docs/api/dagster/execution#dagster.materialize),
[instance](https://dagster.io/docs/api/dagster/internals#dagster.DagsterInstance.local_temp),
[PyPI release](https://pypi.org/project/dagster/1.13.27/),
[Python csv](https://docs.python.org/3.12/library/csv.html),
[os.replace/link](https://docs.python.org/3.12/library/os.html),
[uv hashes](https://docs.astral.sh/uv/pip/compile/),
[Actions](https://docs.github.com/en/actions),[Git](https://git-scm.com/docs).
Telemetry я отключил через собственный local instance; DAGSTER_HOME/Cloud profile
не подхватываю. Отдельный Dagster webserver package не устанавливал, paid services нет.
