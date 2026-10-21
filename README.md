# findex — Лабораторна робота №4 Типи, тести, пакування і CLI

![CI Status](https://github.com/8470977-wq/findex/actions/workflows/ci.yml/badge.svg)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)
![Version](https://img.shields.io/badge/version-v0.4.0-blue)

## Особливості Лабораторної роботи 4
- **Пакет та збірка Wheel**: Проєкт повністю упаковано у готовий дистрибутив Wheel (`.whl`) та Source Distribution (`.tar.gz`) за допомогою `build` (версія `v0.4.0`).
- **Сучасний CLI на Typer & Rich**:
  - `findex index <data_dir>` — побудова та збереження індексу зі смугою прогресу (`rich.progress`).
  - `findex search <index.bin> "query"` — ранжований пошук із гарним виводом у вигляді Rich-таблиці або у JSON (`--json`) в `stdout`.
  - `findex stats <index.bin>` — вивід загальної статистики індексу.
- **Діагностика та логування**: Усі діагностичні повідомлення та логи виводяться через модуль `logging` у `stderr` (підтримка `-v` та `-vv`).
- **Автоматизація (CI)**: Налаштовано GitHub Actions Workflow (`ci.yml`) для автоматичної перевірки коду (`pytest`, `mypy`) при кожному push або PR.

---

## Встановлення із зібраного Wheel

```bash
pip install dist/findex-0.4.0-py3-none-any.whl
