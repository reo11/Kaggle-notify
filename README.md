# Kaggle-notify
KaggleのKernelを通知したい民

## 使い方
1. Kaggle APIをインストールしてTokenを設定する
2. Googleスプレッドシートを設定し、サービスアカウントを作成する
3. Line notifyを設定し、Tokenを取得する
4. `kaggle_notify.py`の8-11行目を自分用に変更する．
	- Googleのサービスアカウントを作成した時のjsonファイルのパス
	- 記録したいGoogleスプレッドシートの名前(スプレッドシートでサービスアカウントの共有設定を忘れずに)
	- Line notifyのトークン
	- 通知したいKaggleのコンテスト名
5. `kaggle_notify.sh`を起動する
	- ex. `$ bash kaggle_notify.sh`, `$zsh kaggle_notify.sh`

以上
詳しくはhttps://qiita.com/reo11/items/142843ba5f53ee8f2199

結構バグだらけな気がするので、プルリクもらえると嬉しいです