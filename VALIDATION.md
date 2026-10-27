# Что я фактически проверил

27.10.2026,0.1.1. Среда: Linux x86_64,CPython3.12.15,Dagster1.13.27,
SQLite3.53.1 (stdlib),uv0.13.1,Git2.53.0. Universal lock52pins,локально48активных
distributions. Я не приравниваю подготовленный workflow к выполненному CI.

| Проверка | Фактический результат |
| --- | --- |
| Unit/integration | 14tests прошли: CSV/empty/limits/UTC/day/cutoff/identity, independent checks, workspace lock, publication failure/retry, tamper, real Dagster blocking/history |
| CLI smoke |6runs в отдельных процессах,2immutable objects, latest старого отчёта при failures, повтор orphan, persisted history; exit0 |
| Runtime compatibility |uv pip check48packages: compatible |
| ZIP/roundtrip | 25 UTF-8 файла по allowlist; ZIP byte-for-byte сверён; распакованный demo завершился0,2объекта/5доставок |
| Source publication | Публикую только PUBLIC_FILES.txt; итоговое удалённое дерево сверяю с локальными blob SHA |
| CI/Windows | Результат отдельно фиксирую в [Actions](https://github.com/Decl1s/dagster-delivery-assets/actions); локально Windows не запускал |
| Release | После успешного CI выпускаю [v0.1.1](https://github.com/Decl1s/dagster-delivery-assets/releases/tag/v0.1.1) с ZIP/SHA256SUMS; публичную квитанцию сохраняю в release/Actions |

Реальная ошибка разработки: я сначала передал materialize keyword asset_checks,
получил TypeError. Проверил API именно1.13.27и передал AssetChecksDefinition в общем
списке definitions. После исправления реальные blocking checks остановили summary;
не заменял их простым ручным if. Дополнительно проверил damaged pointer JSON shape
и exact exclusive day boundary; JSON shape теперь возвращает controlled error.
Первый прогон с TypeError не считаю успешным. Ошибки expected failure в Dagster
stderr относятся к намеренным сценариям,14tests и smoke завершились0.

Я не проверял power loss, сетевые filesystem, hostile symlink races, многопроцессный
writer, web UI,публичный сервис,Cloud и произвольную нагрузку. External completeness
и время поступления файла не известны. Snapshot latest и Dagster final status не
атомарны друг с другом. Тестовые данные/SQLite/logs/credentials в source ZIP не входят.

При упаковке я убрал SyntaxWarning в regex: строку с \. сделал raw string.
Локальный shell не имел команды python; локальные служебные сценарии я вызывал
через python3, приложение — через Python собственного .venv. Это не отказ приложения.

## Уточнение CI в 0.1.1

Я подтвердил первый выпуск 0.1.0: все 14tests, CLI и ZIP прошли в Ubuntu и Windows
по фактическим логам CI40468504798. После этого я заметил риск будущих изменений:
несколько native commands в одном PowerShell step могут скрыть промежуточный nonzero
последней успешной командой. Я объединил установку и проверки в scripts/ci.py с
subprocess.run(check=True); workflow вызывает один Python процесс. Это улучшение
распространения ошибок, а не объявление прежних успешно пройденных tests сломанными.
Финальный CI и архив 0.1.1 я сверяю отдельно; 0.1.0 не переписываю.
