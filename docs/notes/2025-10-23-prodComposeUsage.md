# 本番用Composeファイルの使い方

## 概要

`docker-compose.prod.yaml` を使ってアプリケーションと MySQL を本番想定で立ち上げる方法を整理した。

## 実施内容

- 手順1

```shell
tmux new -s tfk-prod
```

- 手順2

```shell
docker compose -f docker-compose.prod.yaml build
```

- イメージ内にアプリのコードと依存が含まれるため、ホスト側のファイルはコンテナにマウントされない（変更したら再度 build が必要）。

- 手順3

```shell
docker compose -f docker-compose.prod.yaml up -d
```

- 手順4（作業終了時）

```shell
docker compose -f docker-compose.prod.yaml down
```

### 追記

- 既存のセッションに戻るとき

```shell
tmux attach -t tfk-prod
```

- バックグラウンドに戻すときは `Ctrl+b` → `d`

## 参考

無し
