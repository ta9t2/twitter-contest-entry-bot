# Twitter Contest Entry Bot

This bot is for automatically to enter(=retweet and follow) contests on Twitter. 

## Description

- Automatically enter(=retweet and follow) contests if tweets collected from your timeline, a user's list of timeline or search results for specific keywords are including specific contest keywords.
- Unfollow using the FIFO so as not to exceed the Twitter following limit. There is also a script to delete all of your friendships at once.
- Execution results are output to CSV files.
- There is also a tool of emailing summarized direct messages.

NOTE: By bulk retweeting, following or unfollowing behavior, your Twitter account may be suspended by Twitter. You need to adjust interval time and count of entry. Use at your own risk.

## Demo

### Collect contest tweets

The result of executed `tb_search_contests.py`:

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

### Enter contests

The result of executed `tb_enter_contests.py`:

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

## Usage

### Fully automatic entry & unfollowing - `bot_entry.sh`, `bot_entry_win.bat`

bash:
```Bash:e.g. Bash on Ubuntu
bash bot_entry.sh
```

Windows:
```Bash:e.g. Windows
bot_entry_win.bat
```

This script repeat to execute `tb_search_contests.py`(=collecting contests), `tb_enter_contests.py`(=entry contests) and `tb_unfollow.py`(=delete friendships). Result files are saved in `result` directory. It probably is not necessary to delete friendships until the following limit is coming, so adjust the value `destroy_count` on `config/config.json` or comment out `tb_unfollow.py`.

Please refer to the following when you execute separately:

### Search contests - `tb_search_contests.py`

```Bash:e.g. Bash on Ubuntu
python3 tb_search_contests.py
```

This script searches contests if tweets collected from your timeline, a user's list of timeline or search results for specific keywords are including specific contest keywords.

- Input files - `config/config.json`
- Output files - `config/contest_list.csv`

### Entry - `tb_enter_contests.py`

```Bash:e.g. Bash on Ubuntu
python3 tb_enter_contests.py
```

This script enters(=retweet and follow) contests that are in `config/contest_list.csv`. If tweet text including screen names(=r'@[a-z|A-Z|0-9|_]{1,15}'), follow those users. Followed friends list is written out on `config/friend_list.csv` file for to delete friendships by `tb_unfollow.py`.

- Input files - `config/config.json`, `config/contest_list.csv`
- Output files - `result/entry_{YYYYMMDD}_{HHMMSS}.csv`, `config/friend_list.csv`

### Delete several friendships - `tb_unfollow.py`

```Bash:e.g. Bash on Ubuntu
python3 tb_unfollow.py
```

This script deletes(=unfollow) friendships in order by oldness according to `config/friend_list.csv` that was made by `tb_enter_contests.py`. You can specify the number of friends to delete your friendships at once is in `destroy_count` on `config/config.json`.

- Input files - `config/config.json`, `config/friend_list.csv`
- Output files - `result/unfollow_{YYYYMMDD}_{HHMMSS}.csv`, `config/friend_list.csv`

### Delete all friendships - `tb_destroy_all_friendship.py`

```Bash:e.g. Bash on Ubuntu
python3 tb_destroy_all_friendship.py
```

This script deletes(=unfollow) all of your friendships at once without reflecting `ignore_users`.

- Input files - `config/config.json`
- Output files - `result/destroy_all_friendship_{YYYYMMDD}_{HHMMSS}.csv`

### Email summarized direct messages - `tb_summarize_dms.py`

```Bash:e.g. Bash on Ubuntu
python3 tb_summarize_dms.py
```

This script summarizes your direct messages and email.

- Input files - `config/config.json`
- Output files - `result/sumdms_{YYYYMMDD}_{HHMMSS}.csv`

## Requirements

- Python 3.7
- tweepy 3.7.0

NOTE: It will probably work with older versions, but I haven't verified it.

## Installation

```Bash:e.g. Bash on Ubuntu
pip3 install tweepy
```

## Configuration

Open up `config/config.json` and make below values. These scripts work if you configure the values correspond to your Twitter API credentials, but the default values are for Japanese users.

### Common configs

#### Your Twitter API credentials (Required)

```JSON:config.json
  "consumer_key": "specify your consumer API key",
  "consumer_secret": "specify your consumer API secret key",
  "access_token": "specify your access token",
  "access_token_secret": "specify your access token secret",
```

#### Your local time zone

```JSON:config.json
  "timezone": 9,
```
e.g. JST -> `9`, EST -> `-5`

#### Directory of result files

```JSON:config.json
  "result_dir": "result",
```
Results files are saved the directory.

#### Interval time(sec) between entries or between unfollowings

```JSON:config.json
  "interval_time": 180,
```

### Entry configs

#### Contest list filename

```JSON:config.json
    "contest_list_filename": "config/contest_list.csv",
```

Searched and collected contests are saved the file by `tb_search_contests.py`. `tb_enter_contests.py` uses the file for to enter contests.

#### Entry keywords

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

If a contest tweet including these keywords, this script enters it. One-dimensional list behaviors are to append 'OR' conditions, two-dimensional list behaviors are to append 'AND'.

e.g. [["RT", "Retweet"], ["FOLLOW", "Follow"]] -> (("RT" OR "Retweet") AND ("FOLLOW" OR "Follow"))

#### Collect tweets from your timeline

```JSON:config.json
      "timeline": {
        "is_enable": false,
        "count": 30
      },
```

- `is_enable` - If `true`, tweets are collected from your timeline.
- `count` - Specify the number of tweets to collect.

#### Collect tweets from a user's list of timeline

```JSON:config.json
      "list": {
        "is_enable": false,
        "count": 30,
        "screen_name": "foo",
        "slug": "bar"
      },
```

- `is_enable` - If `true`, tweets are collected from a user's list of a timeline. 
- `count` - Specify the number of tweets to collect.
- `screen_name` - Specify the screen name of the owner of the list.
- `slug` - Specify the slug name or numerical ID of the list.

e.g. URL of @foo user's list `https://twitter.com/foo/lists/bar` -> `"foo"` in `screen_name`, `"bar"` in `slug`.

#### Collect tweets from search results for specific keywords

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

- `is_enable` - If `true`, tweets are collected from search results for specific keywords.
- `count` - Specify the number of tweets to collect.
- `search_queries` - Specify search queries. Multiple queries behaviors are to append 'OR' conditions.
- `lang` - Restricts tweets to the given language, given by an ISO 639-1 code. (Ref. '[List of ISO 639-1 codes - Wikipedia](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)')

e.g. In `lang`, English -> `"en"`, Japanese -> `"ja"`.

#### Entry ignore users

```JSON:config.json
    "ignore_users": [
      "foo",
      "foo2",
      "foo3"
    ]
```

If a tweeted user or tweet text are including specified ignore users, it does not enter the contest tweet.

### Unfollowing configs

#### File name of to unfollow list

```JSON:config.json
    "destroy_list_filename": "config/friend_list.csv",
```

#### Number of friends to delete your friendships at once

```JSON:config.json
    "destroy_count": 20,
```

#### Unfollowing ignore users

```JSON:config.json
    "ignore_users": [
      "foo",
      "foo2",
      "foo3"
    ]
```

Specified ignore users are not to do unfollow.

### Summarization direct messages configs

#### Number of direct messages to email at once

```JSON:config.json
  "sum": {
      "count": 20,
```

#### Filename stored last timestamp of direct message

```JSON:config.json
      "last_timestamp_filename": "config/sum_last_timestamp.txt",
```

Get the latest timestamp from direct messages and store the file when do mail. When do mail next time, get the last timestamp from the file and collect direct messages newer than the timestamp.

#### Email

```JSON:config.json
      "email": {
          "is_enable": true,
          "mailto": "mailto address",
          "gmail_addr": "your gmail address(@gmail.com)",
          "gmail_pw": "your gmail password"
      }
```

- `is_enable` - If `true`, send to email using below info. If `false`, only create a file of summarized dms.
- `mailto` - Specify a destination email address.
- `gmail_addr` - Specify a sender email address. It is your gmail account.
- `gmail_pw` - Specify a password of `gmail_addr`.

## License

This software is released under the MIT License, see LICENSE.

## References

The following websites are referenced:

- [How I won 4 Twitter contests a day (every day for 9 months straight) | Hunter Scott](https://www.hscott.net/twitter-contest-winning-as-a-service/)
