# 概要

FastAPIの認証機能の練習用リポジトリ

# 動く認証機能

- JWT  
参考: [fastapi公式 OAuth2 with Password (and hashing), Bearer with JWT tokens](https://fastapi.tiangolo.com/ja/tutorial/security/oauth2-jwt/)

# 認証情報

ユーザー名: johndoe  
パスワード: secret  

# 使い方

イメージを作る

```shell
sudo docker image build --no-cache -t fastapi:test .
```

コンテナを起動する

```shell
sudo docker run -p 8000:8000 fastapi:test
```

以下にブラウザでアクセスする

```text
http://ipアドレス:8000/docs
```

画面右上のauthorizedにて上述の認証情報で認証する。
そうすると鍵マークがついたAPIが使える。
