# DBMigration

## 概要

dbのマイグレーション

## 実施内容

- migration

```shell
docker compose exec tfk-app poetry run python -m api.migrate_db
```

## 参考

なければなにも書かなくても
