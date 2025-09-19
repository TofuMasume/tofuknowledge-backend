# Setup poetry

## 概要

poetry関連

## 実施内容

- Initialize poetry

```shell
docker compose run --entrypoint "poetry init --name tfk-app --dependency fastapi --dependency uvicorn[standard]" tfk-app
```

- Install package

```shell
docker compose  run --entrypoint "poetry install --no-root" tfk-app
```

## 参考

なければなにも書かなくても
