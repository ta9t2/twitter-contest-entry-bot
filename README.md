# Twitter Contest Entry Bot

This bot is for automatically to enter(=retweet and follow) contests on Twitter. 

## Description

- Automatically enter(=retweet and follow) contests if tweets collected from your timeline, a user's list of timeline or search results for specific keywords are including specific contest keywords.
- Unfollow using the FIFO so as not to exceed the Twitter following limit. There is also a script to delete your all friendships at once.
- Execution results are output to CSV files.

NOTE: By bulk retweeting, following or unfollowing behavior, your Twitter account may be suspended by Twitter. You need to adjust interval time and count of entry. Use at your own risk.

## Demo

The result of executed `EntryBot.py`:

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

Output file - `result_EntryBot_YYYYMMDD_HHMMSS.csv` :

![result_EntryBot_1](https://user-images.githubusercontent.com/48476117/54944974-12b48100-4f78-11e9-82e0-897332a5c069.png)

![result_EntryBot_2](https://user-images.githubusercontent.com/48476117/54944991-1942f880-4f78-11e9-8b22-ccb9942a91ff.png)

## Usage

### Fully automatic entry & unfollowing - `Looper.sh`

```Bash:e.g. Bash on Ubuntu
bash Looper.sh
```

This script repeat to execute `EntryBot.py`(=entry contests) and `UnfollowBot.py`(=delete friendships). Output files are moved to the `result_files` directory and merged. It probably is not necessary to delete friendships until the following limit is coming, so adjust the value `destroy_count` on `config.json` or comment out `UnfollowBot.py`.

Please refer to the following when you execute separately:

### Entry - `EntryBot.py`

```Bash:e.g. Bash on Ubuntu
python3 EntryBot.py
```

This script enters(=retweet and follow) contests if tweets collected from your timeline, a user's list of timeline or search results for specific keywords are including specific contest keywords. If tweet text including screen names(=r'@[a-z|A-Z|0-9|_]{1,15}'), follow those users. Followed friends list is written out on `destroy_list.csv` file for to delete friendships by `UnfollowBot.py`.

- Input files - `config.json`
- Output files - `result_EntryBot_{YYYYMMDD}_{HHMMSS}.csv`, `destroy_list.csv`

### Delete several friendships - `UnfollowBot.py`

```Bash:e.g. Bash on Ubuntu
python3 UnfollowBot.py
```

This script deletes(=unfollow) friendships in order by oldness according to `destroy_list.csv` that was made by `EntryBot.py`. You can specify the number of friends to delete your friendships at once is in `destroy_count` on `config.json`.

- Input files - `config.json`, `destroy_list.csv`
- Output files - `result_UnfollowBot_{YYYYMMDD}_{HHMMSS}.csv`, `destroy_list.csv`

### Delete all friendships - `DestroyAllFriendshipsBot.py`

```Bash:e.g. Bash on Ubuntu
python3 DestroyAllFriendshipsBot.py
```

This script deletes(=unfollow) your all friendships at once without reflecting `ignore_users`.

- Input files - `config.json`
- Output files - `result_DestroyAllFriendshipsBot_{YYYYMMDD}_{HHMMSS}.csv`

## Requirements

- Python 3.7
- tweepy 3.7.0

NOTE: It will probably work with older versions, but I haven't verified it.

## Installation

```Bash:e.g. Bash on Ubuntu
pip3 install tweepy
```

## Configuration

Open up `config.json` and make below values. These scripts work if you configure the values correspond to your Twitter API credentials, but the default values are for Japanese users.

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

#### Interval time(sec) between entries or between unfollowings

```JSON:config.json
  "interval_time": 180,
```

### Entry configs

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
    "destroy_list_filename": "destroy_list.csv",
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

## License

This software is released under the MIT License, see LICENSE.

## References

The following websites are referenced:

- [How I won 4 Twitter contests a day (every day for 9 months straight) | Hunter Scott](https://www.hscott.net/twitter-contest-winning-as-a-service/)
