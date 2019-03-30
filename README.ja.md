# Twitter Contest Entry Bot / ツイッター懸賞応募ボット

このボットはツイッター上の懸賞に自動的に応募(=リツイート＆フォロー)するものです。

## Description / 説明(特徴など)

- あなたのタイムライン、あるユーザのリストのタイムライン、または特定キーワードでの検索結果からツイートを集めて、それらに特定の懸賞ワードが含まれていれば、自動的に応募(=リツイート＆フォロー)します。
- ツイッターのフォロー上限を超えないようにFIFOでアンフォロー(=フォロー解除)します。すべてのフレンドを一括アンフォローするスクリプトもあります。
- 実行結果はCSVファイルに出力されます。

注: 大量のリツイート、フォロー、アンフォローによってあなたのツイッターアカウントが凍結される可能性があります。インターバルタイムや応募数を調整する必要があります。自己責任で使ってください。

## Demo / デモ

`EntryBot.py`の実行結果:

```Bash:bot.log
$ python3 EntryBot.py
START EntryBot.py
---------- [1] ----------------------------------------
tweet-url: https://twitter.com/screen_name/status/xxxxxxxxxxxxxx
tweet-text: aaaaa aaaaa Retweet! Follow @abcdef and @ghi! You could win aaaaa aaaaa
retweet: Successfully retweeted
follow: Abc Def(@abcdef) -> Successfully followed
follow: Ghi Jk(@ghi) -> Already followed
time.sleep(180)
---------- [2] ----------------------------------------
tweet-url: https://twitter.com/screen_name/status/xxxxxxxxxxxxxx
tweet-text: aaaaa aaaaa Retweet! Follow @abcdef and @ghi! You could win aaaaa 
retweet: Successfully retweeted
follow: Abc Def(@abcdef) -> Successfully followed
follow: Ghi Jk(@ghi) -> Already followed
time.sleep(180)

...

DONE! See the "result_EntryBot_YYYYMMDD_HHMMSS.csv" file.
Friends: 770 -> 772
Successfully retweeted: 2
Added destroy list: destroy_list.csv
```

出力ファイル - `result_EntryBot_YYYYMMDD_HHMMSS.csv` :

![result_EntryBot_1](https://user-images.githubusercontent.com/48476117/54944974-12b48100-4f78-11e9-82e0-897332a5c069.png)

![result_EntryBot_2](https://user-images.githubusercontent.com/48476117/54944991-1942f880-4f78-11e9-8b22-ccb9942a91ff.png)

## Usage / 使い方

### 全自動の応募＆アンフォロー - `Looper.sh`, `Looper_win.bat`

bash:
```Bash:e.g. Bash on Ubuntu
bash Looper.sh
```

Windows:
```Bash:e.g. Bash on Ubuntu
Looper_win.bat
```

このスクリプトは `EntryBot.py` (=応募=リツイート＆フォロー) と `UnfollowBot.py` (=アンフォロー) を繰り返し実行します。出力ファイルは `result_files` ディレクトリに移動されてマージされます。フォロー上限近くになるまではアンフォローは必要ないと思いますので、 `config.json` の `destroy_count` 項目の値を調整するか、 `UnfollowBot.py` の実行をコメントアウトします。

個別に実行する場合は以下を参照してください。

### 応募 - `EntryBot.py`

```Bash:e.g. Bash on Ubuntu
python3 EntryBot.py
```

このスクリプトは、あなたのタイムライン、あるユーザのリストのタイムライン、または特定キーワードでの検索結果からツイートを集めて、それらに特定の懸賞ワードが含まれていれば、応募(=リツイート＆フォロー)します。ツイート内容にスクリーンネーム(=r'@[a-z|A-Z|0-9|_]{1,15}'=@マークから始まるユーザ名)が含まれていれば、そのユーザもフォローします。フォローされたユーザのリストは `UnfollowBot.py` でアンフォローするために `destroy_list.csv` ファイルに出力されます。

- Input files - `config.json`
- Output files - `result_EntryBot_{YYYYMMDD}_{HHMMSS}.csv`, `destroy_list.csv`

### アンフォロー - `UnfollowBot.py`

```Bash:e.g. Bash on Ubuntu
python3 UnfollowBot.py
```

このスクリプトは `EntryBot.py` で作られた `destroy_list.csv` に従って、古い順にフレンドをアンフォロー(=フォロー解除)します。一度にアンフォローするユーザ数は `config.json` の `destroy_count` で指定できます。

- Input files - `config.json`, `destroy_list.csv`
- Output files - `result_UnfollowBot_{YYYYMMDD}_{HHMMSS}.csv`, `destroy_list.csv`

### 全フレンドのアンフォロー - `DestroyAllFriendshipsBot.py`

```Bash:e.g. Bash on Ubuntu
python3 DestroyAllFriendshipsBot.py
```

このスクリプトは `ignore_users` の設定を反映せずにすべてのフレンドを一括アンフォロー(=フォロー解除)します。

- Input files - `config.json`
- Output files - `result_DestroyAllFriendshipsBot_{YYYYMMDD}_{HHMMSS}.csv`

## Requirements / 動作条件

- Python 3.7
- tweepy 3.7.0

注: 旧バージョンでも動作すると思いますが、検証していません。

## Installation / インストール方法

```Bash:e.g. Bash on Ubuntu
pip3 install tweepy
```

## Configuration / 設定方法

`config.json` を開いて下記の項目を設定してください。これらのスクリプトはツイッターのAPI認証情報を設定すれば動きますが、初期値は日本ユーザ向けです。

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

#### 応募間隔やアンフォロー間隔のインターバルタイム(秒)

```JSON:config.json
  "interval_time": 180,
```

### 応募(=リツイート＆フォロー)の設定

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
    "destroy_list_filename": "destroy_list.csv",
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

## License / ライセンス

MITライセンスです。LICENSEファイルを参照ください。

## References / 参考

次のウェブサイトを参考にしています。

- [How I won 4 Twitter contests a day (every day for 9 months straight) | Hunter Scott](https://www.hscott.net/twitter-contest-winning-as-a-service/)
