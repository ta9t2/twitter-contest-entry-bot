# Twitter Contest Entry Bot / ツイッター懸賞応募ボット

このボットはツイッター上の懸賞に自動的に応募(=リツイート＆フォロー)するものです。

## Description / 説明(特徴など)

- あなたのタイムライン、あるユーザのリストのタイムライン、または特定キーワードでの検索結果からツイートを集めて、それらに特定の懸賞ワードが含まれていれば、自動的に応募(=リツイート＆フォロー)します。
- ツイッターのフォロー上限を超えないようにFIFOでアンフォロー(=フォロー解除)します。すべてのフレンドを一括アンフォローするスクリプトもあります。
- 実行結果はCSVファイルに出力されます。
- ダイレクトメッセージをサマライズしてメールするツールもあります。

注: 大量のリツイート、フォロー、アンフォローによってあなたのツイッターアカウントが凍結される可能性があります。インターバルタイムや応募数を調整する必要があります。自己責任で使ってください。

## Demo / デモ

### 懸賞ツイートの収集

`tb_search_contests.py`の実行結果:

```Bash:tb_search_contests.py.log
$ python3 tb_search_contests.py
START SCRIPT
Stored the contest tweet: url=https://twitter.com/screen_name_aaa/status/tweet_id_111, tweet.text=aaaaa aaaaa Retweet! Follow @abcdef and @ghi! You could win aaaaa aaaaa
Since the tweet is not a contest, skipped: url=https://twitter.com/screen_name_bbb/status/tweet_id_222, tweet.text=test test test
Stored the contest tweet: url=https://twitter.com/screen_name_ccc/status/tweet_id_333, tweet.text=ccccc ccccc RT! FOLLOW @ghijkl! You could win aaaaa aaaaa
Stored the contest tweet: url=https://twitter.com/screen_name_ddd/status/tweet_id_444, tweet.text=ddddd ddddd Retweet! Follow @mnopqr! You could win aaaaa aaaaa

...

Wrote the contest tweet list: filename=config/contest_list.csv.
DONE
```

Output file of the collected contest tweet list - `config/contest_list.csv` :

![contest_list.csv](https://user-images.githubusercontent.com/48476117/64070857-8ab17080-cca7-11e9-98a0-95fba6b070c1.png)

### 懸賞応募

`tb_enter_contests.py`の実行結果:

```Bash:tb_enter_contests.log
$ python3 tb_enter_contests.py
START SCRIPT
---------- [1] ----------------------------------------
tweet_url: https://twitter.com/screen_name_aaa/status/tweet_id_111
retweet: Successfully retweeted
follow: ABC(@abcdef/111111) -> Successfully followed
follow: GHI(@ghi/222222) -> Successfully followed
Waiting: time.sleep(180)
---------- [2] ----------------------------------------
tweet_url: https://twitter.com/screen_name_ccc/status/tweet_id_333
retweet: Successfully retweeted
follow: GL(@ghijkl/333333) -> Successfully followed
Waiting: time.sleep(180)
---------- [3] ----------------------------------------
tweet_url: https://twitter.com/screen_name_ddd/status/tweet_id_444
retweet: Successfully retweeted
follow: MNO(@mnopqr/222222) -> Successfully followed
follow: DD(@dddddd/444444) -> Already followed
Waiting: time.sleep(180)

...

Successfully retweeted: 3
Friends: 100 -> 104
Cleared the contest list: filename=config/contest_list.csv
DONE
```

Output file of the result of contest entry - `result/entry_YYYYMMDD_HHMMSS.csv` :

![entry_YYYYMMDD_HHMMSS.csv](https://user-images.githubusercontent.com/48476117/64070990-dade0200-ccaa-11e9-9c9b-89e4c673871a.png)

## Usage / 使い方

### 全自動の応募＆アンフォロー - `bot_entry.sh`, `bot_entry_win.bat`

bash:
```Bash:e.g. Bash on Ubuntu
bash bot_entry.sh
```

Windows:
```Bash:e.g. Windows
bot_entry_win.bat
```

このスクリプトは `tb_search_contests.py` (=懸賞ツイートの収集)、 `tb_enter_contests.py` (=応募=リツイート＆フォロー) と `tb_unfollow.py` (=アンフォロー) を繰り返し実行します。出力ファイルは `result` ディレクトリに移動されてマージされます。フォロー上限近くになるまではアンフォローは必要ないと思いますので、 `config/config.json` の `destroy_count` 項目の値を調整するか、 `tb_unfollow.py` の実行をコメントアウトします。

個別に実行する場合は以下を参照してください。

### 懸賞ツイートの収集 - `tb_search_contests.py`

```Bash:e.g. Bash on Ubuntu
python3 tb_search_contests.py
```

このスクリプトは、あなたのタイムライン、あるユーザのリストのタイムライン、または特定キーワードでの検索結果からツイートを集めて、それらに特定の懸賞ワードが含まれていれば懸賞ツイートリストとして保存します。

- Input files - `config/config.json`
- Output files - `config/contest_list.csv`

### 応募 - `tb_enter_contests.py`

```Bash:e.g. Bash on Ubuntu
python3 tb_enter_contests.py
```

このスクリプトは`config/contest_list.csv`の懸賞に応募(=リツイート＆フォロー)します。ツイート内容にスクリーンネーム(=r'@[a-z|A-Z|0-9|_]{1,15}'=@マークから始まるユーザ名)が含まれていれば、そのユーザもフォローします。フォローされたユーザのリストは `tb_unfollow.py` でアンフォローするために `config/friend_list.csv` ファイルに出力されます。

- Input files - `config/config.json`, `config/contest_list.csv`
- Output files - `result/entry_{YYYYMMDD}_{HHMMSS}.csv`, `config/friend_list.csv`

### アンフォロー - `tb_unfollow.py`

```Bash:e.g. Bash on Ubuntu
python3 tb_unfollow.py
```

このスクリプトは `tb_enter_contests.py` で作られた `config/friend_list.csv` に従って、古い順にフレンドをアンフォロー(=フォロー解除)します。一度にアンフォローするユーザ数は `config/config.json` の `destroy_count` で指定できます。

- Input files - `config/config.json`, `config/friend_list.csv`
- Output files - `result/unfollow_{YYYYMMDD}_{HHMMSS}.csv`, `config/friend_list.csv`

### 全フレンドのアンフォロー - `tb_destroy_all_friendship.py`

```Bash:e.g. Bash on Ubuntu
python3 tb_destroy_all_friendship.py
```

このスクリプトは `ignore_users` の設定を反映せずにすべてのフレンドを一括アンフォロー(=フォロー解除)します。

- Input files - `config/config.json`
- Output files - `result/destroy_all_friendship_{YYYYMMDD}_{HHMMSS}.csv`

## Requirements / 動作条件

- Python 3.7
- tweepy 3.7.0

注: 旧バージョンでも動作すると思いますが、検証していません。

## Installation / インストール方法

```Bash:e.g. Bash on Ubuntu
pip3 install tweepy
```

## Configuration / 設定方法

`config/config.json` を開いて下記の項目を設定してください。これらのスクリプトはツイッターのAPI認証情報を設定すれば動きますが、初期値は日本ユーザ向けです。

### 共通設定

#### ツイッター認証情報 (設定必須)

```JSON:config.json
  "consumer_key": "specify your consumer API key",
  "consumer_secret": "specify your consumer API secret key",
  "access_token": "specify your access token",
  "access_token_secret": "specify your access token secret",
```
#### タイムゾーン

```JSON:config.json
  "timezone": 9,
```
e.g. JST -> `9`, EST -> `-5`

#### 結果ファイルのディレクトリ

```JSON:config.json
  "result_dir": "result",
```
結果ファイルはこのディレクトリに保存されます。

#### 応募間隔やアンフォロー間隔のインターバルタイム(秒)

```JSON:config.json
  "interval_time": 180,
```

### 応募(=リツイート＆フォロー)の設定

#### 懸賞ツーとリストのファイル名

```JSON:config.json
    "contest_list_filename": "config/contest_list.csv",
```

`tb_search_contests.py`で検索、収集された懸賞ツーとがこのファイルに保存されます。`tb_enter_contests.py`から利用して懸賞に応募します。

#### 応募のキーワード

```JSON:config.json
    "entry_keywords2d": [
      [
        "RT",
        "RETWEET",
        "Retweet",
        "retweet",
      ],
      [
        "FOLLOW",
        "Follow",
        "follow",
      ]
    ],
```

ツイート内容にこれらのキーワードが含まれていれば応募します。1次元リストは 'OR' 条件を付与し、2次元リストは 'AND' 条件を付与します。

(例) [["RT", "Retweet"], ["FOLLOW", "Follow"]] -> (("RT" OR "Retweet") AND ("FOLLOW" OR "Follow"))

#### あなたのタイムラインからのツイート収集

```JSON:config.json
      "timeline": {
        "is_enable": false,
        "count": 30
      },
```

- `is_enable` - `true` なら、あなたのタイムラインからツイートを集めます。
- `count` - 収集するツイート数を指定します。

#### あるユーザのリストのタイムラインからのツイート収集

```JSON:config.json
      "list": {
        "is_enable": false,
        "count": 30,
        "screen_name": "foo",
        "slug": "bar"
      },
```

- `is_enable` - `true` なら、あるユーザのリストのタイムラインからツイートを集めます。 
- `count` - 収集するツイート数を指定します。
- `screen_name` - リストのオーナーのスクリーンネームを指定します。
- `slug` - リスト名(slug name)またはリストID(numerical ID)を指定します。

(例) @fooユーザのリストのURL `https://twitter.com/foo/lists/bar` -> `screen_name` には `"foo"` 、 `slug` には `"bar"` を指定します。

#### 特定キーワードでの検索結果からのツイート収集

```JSON:config.json
      "search": {
        "is_enable": true,
        "count": 30,
        "search_queries": [
          "contest",
          "retweet",
          "win"
        ],
        "lang": "en"
      }
```

- `is_enable` - `true` なら、特定キーワードでの検索結果からツイートを集めます。
- `count` - 収集するツイート数を指定します。
- `search_queries` - 検索キーワードを指定します。複数キーワードは 'OR' 条件です。
- `lang` - ISO 639-1コードで指定された言語に検索結果を制限します。 (参考 '[List of ISO 639-1 codes - Wikipedia](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)')

(例) `lang` には、English -> `"en"`, Japanese -> `"ja"` を指定します。

#### 応募無視ユーザ

```JSON:config.json
    "ignore_users": [
      "foo",
      "foo2",
      "foo3"
    ]
```

ツイートしたユーザやツイート内容に特定の無視ユーザが含まれていれば、応募しません。

### アンフォロー設定

#### アンフォローリストのファイル名

```JSON:config.json
    "destroy_list_filename": "config/destroy_list.csv",
```

#### 一度にアンフォローするフレンド数

```JSON:config.json
    "destroy_count": 20,
```

#### アンフォロー無視ユーザ

```JSON:config.json
    "ignore_users": [
      "foo",
      "foo2",
      "foo3"
    ]
```

アンフォローしない無視ユーザを指定します。

### ダイレクトメッセージサマライズの設定

#### 一度にサマライズするダイレクトメッセージの数

```JSON:config.json
  "sum": {
      "count": 20,
```

#### 最後のタイムスタンプを格納するファイル名

```JSON:config.json
      "last_timestamp_filename": "config/sum_last_timestamp.txt",
```

メール送信時にダイレクトメッセージから最新のタイムスタンプを取得して保存します。次回のメール送信時はそのファイルからタイムスタンプを取得してそれよりも新しいダイレクトメッセージを取得します。

#### Eメール

```JSON:config.json
      "email": {
          "is_enable": true,
          "mailto": "mailto address",
          "gmail_addr": "your gmail address(@gmail.com)",
          "gmail_pw": "your gmail password"
      }
```

- `is_enable` - `true` なら、以下の情報を使用してEmailを送信します。 `false` なら、サマライズしたダイレクトメッセージのファイルのみを作成します。
- `mailto` - 宛先アドレスを設定します。
- `gmail_addr` - 送信者アドレスを設定します。あなたのgmailアカウントです。
- `gmail_pw` - `gmail_addr`のパスワードを設定します。

## License / ライセンス

MITライセンスです。LICENSEファイルを参照ください。

## References / 参考

次のウェブサイトを参考にしています。

- [How I won 4 Twitter contests a day (every day for 9 months straight) | Hunter Scott](https://www.hscott.net/twitter-contest-winning-as-a-service/)
