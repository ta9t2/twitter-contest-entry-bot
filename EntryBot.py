#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This bot is for automatically to join contests on Twitter

import tweepy
import re
from datetime import timedelta
from datetime import datetime
import csv
import time
import json
import sys
import os


def get_api(consumer_key, consumer_secret, access_token, access_token_secret):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True,
                     wait_on_rate_limit_notify=True)
    return api


def log(level, text):
    timemes = datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
    levmes = '[ERROR]' if level == 'e' else '[INFO]'
    logmes = ''.join(str(text).splitlines())
    print(logmes)
    with open('bot.log', mode='a', encoding="utf-8_sig") as f:
        f.write(timemes + levmes + logmes + '\n')


def get_tweets_search(api, que, lang, count):
    result_tweets = list()
    try:
        # Unspecified tweet_mode - Tweets are stored in each SearchResult.text
        result_tweets = api.search(
            q=que, lang=lang, result_type='recent', count=count)

        # tweet_mode="extended" - Tweets are stored in each SearchResult.full_text
        # result_tweets = api.search(q=que, lang=lang', result_type='recent', count=count, tweet_mode="extended")
    except tweepy.error.TweepError as e:
        log('e', 'func=' + str(sys._getframe().f_code.co_name) +
            ', e.reason=' + str(e.reason) + ', abort')
        sys.exit(1)
    return result_tweets


def is_contest(tweet, keywords2d):
    result_is_contest = all(
        (
            any(
                (keyword in tweet) for keyword in keywords
            )
        ) for keywords in keywords2d
    )
    return result_is_contest


def extract_screen_names(tweet):
    result_screen_names = list()
    at_screen_names = re.findall(r'@[a-z|A-Z|0-9|_]{1,15}', tweet)
    for at_screen_name in at_screen_names:
        screen_name = at_screen_name.replace('@', '')
        result_screen_names.append(screen_name)
    return result_screen_names


def convert_screen_names_to_user_ids(api, screen_names):
    result_user_ids = list()
    for screen_name in screen_names:
        try:
            result_user_ids.append(api.get_user(screen_name).id)
        except tweepy.error.TweepError as e:
            log('e', 'func=' + str(sys._getframe().f_code.co_name) + ', screen_name="' +
                str(screen_name) + '", e.reason=' + str(e.reason))
    return result_user_ids


def convert_ignore_users_to_ignore_user_ids(ignore_users):
    result_ignore_user_ids = list()
    for user in ignore_users:
        try:
            result_ignore_user_ids.append(api.get_user(user).id)
        except tweepy.error.TweepError as e:
            log('e', 'func=' + str(sys._getframe().f_code.co_name) + ', user="' +
                str(user) + '", e.reason=' + str(e.reason))
    return result_ignore_user_ids


def check_ignore(user_ids, ignore_user_ids):
    is_ignore = False
    ignore_user_id = ''
    ignore_screen_name = ''
    ignore_name = ''
    for user_id in user_ids:
        if user_id in ignore_user_ids:
            is_ignore = True
            ignore_user_id = user_id
            try:
                ignore_screen_name = api.get_user(user_id).screen_name
                ignore_name = api.get_user(user_id).name
            except tweepy.error.TweepError as e:
                log('e', 'func=' + str(sys._getframe().f_code.co_name) + ', is_ignore="' + str(is_ignore) + ', ignore_user_id="' + str(ignore_user_id) +
                    ', ignore_screen_name="' + str(ignore_screen_name) + ', ignore_name="' + str(ignore_name) + '", e.reason=' + str(e.reason))
    return is_ignore, ignore_user_id, ignore_screen_name, ignore_name


def do_entry(api, user_ids, tweet_id, ignore_user_ids):
    result_follows = list()
    result_retweet = dict()

    # If including ignore user, not to enter
    is_ignore, ignore_user_id, ignore_screen_name, ignore_name = check_ignore(
        user_ids, ignore_user_ids)
    if is_ignore:
        comment = 'Ignored(ignore_user_id="' + str(ignore_user_id) + ', ignore_screen_name="' + \
            str(ignore_screen_name) + ', ignore_name="' + str(ignore_name) + ')'
        result_follows.append(
            dict(user_id='', screen_name='', name='', is_followed=False, comment=comment))
        result_retweet = dict(
            tweet_id=tweet_id, is_retweeted=False, comment=comment)
        return result_follows, result_retweet

    # Follow(Create friendship with new users)
    for user_id in user_ids:
        screen_name = ''
        name = ''
        try:
            friendship = api.show_friendship(
                source_id=api.me().id, target_id=user_id)
            screen_name = api.get_user(user_id).screen_name
            name = api.get_user(user_id).name
            if friendship[0].following:
                result_follows.append(
                    dict(user_id=user_id, screen_name=screen_name, name=name, is_followed=False, comment='Already followed'))
            else:
                api.create_friendship(user_id)
                result_follows.append(
                    dict(user_id=user_id, screen_name=screen_name, name=name, is_followed=True, comment='Successfully followed'))
        except tweepy.error.TweepError as e:
            result_follows.append(
                dict(user_id=user_id, screen_name=screen_name, name=name, is_followed=False, comment=e.reason))

    # Retweet
    try:
        api.retweet(tweet_id)
        result_retweet = dict(
            tweet_id=tweet_id, is_retweeted=True, comment='Successfully retweeted')
    except tweepy.error.TweepError as e:
        result_retweet = dict(
            tweet_id=tweet_id, is_retweeted=False, comment=e.reason)

    return result_follows, result_retweet


def get_tweet_url(screen_name, tweet_id):
    tweet_url = 'https://twitter.com/{screen_name}/status/{tweet_id}'.format(
        screen_name=screen_name, tweet_id=tweet_id)
    return tweet_url


def print_progress(index, result):
    mes = list()
    mes += ['---------- [{m1}] ----------------------------------------'.format(
        m1=(index + 1))]
    mes += ['tweet-url: {m1}'.format(m1=result['tweet-url'])]
    mes += ['tweet-text: {m1}'.format(m1=result['tweet-text'])]
    if result['tweet-is_contest']:
        mes += ['retweet: {m1}'.format(m1=result['retweet']['comment'])]
        for follow in result['follows']:
            mes += ['follow: {m1}(@{m2}) -> {m3}'.format(m1=follow['name'],
                                                          m2=follow['screen_name'], m3=follow['comment'])]
    for m in mes:
        log('i', m)


def convert_result_dic_to_list(result):
    row = list()
    row += [result['tweet-url']]
    row += [result['tweet-id']]
    row += [result['tweet-text']]
    row += [result['tweet-created_at'].strftime('%Y-%m-%d %H:%M:%S')]
    row += [result['tweet-is_contest']]
    if result['tweet-is_contest']:
        row += [result['retweet']['tweet_id']]
        row += [result['retweet']['is_retweeted']]
        row += [result['retweet']['comment']]
        for follow in result['follows']:
            row += [follow['user_id']]
            row += [follow['screen_name']]
            row += [follow['name']]
            row += [follow['is_followed']]
            row += [follow['comment']]
    return row


def write_results(results, filename):
    header = [[
        'tweet-url',
        'tweet-id',
        'tweet-text',
        'tweet-created_at',
        'tweet-is_contest',
        'retweet-tweet_id',
        'retweet-is_retweeted',
        'retweet-comment',
        'follow-user_id',
        'follow-screen_name',
        'follow-name',
        'follow-is_followed',
        'follow-comment',
        'follow-...',
    ]]

    rows = list()
    for result in results:
        rows.append(convert_result_dic_to_list(result))

    with open(filename, mode='w', encoding="utf-8_sig") as f:
        writer = csv.writer(f, delimiter=',', quotechar='"',
                            lineterminator='\n', quoting=csv.QUOTE_ALL)
        writer.writerows(header + rows)


def add_destroy_list(results, filename, result_filename):
    rows = list()
    for result in results:
        if result['tweet-is_contest']:
            for follow in result['follows']:
                if follow['is_followed']:
                    row = list()
                    row += [result_filename]
                    row += [follow['user_id']]
                    row += [follow['screen_name']]
                    row += [follow['name']]
                    rows.append(row)

    with open(filename, mode='a', encoding="utf-8_sig") as f:
        writer = csv.writer(f, delimiter=',', quotechar='"',
                            lineterminator='\n', quoting=csv.QUOTE_ALL)
        writer.writerows(rows)


if __name__ == '__main__':
    log('i', 'START {script_name}'.format(
        script_name=os.path.basename(__file__)))

    tweets = list()
    results = list()
    start_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = 'result_EntryBot_' + start_time + '.csv'

    # Load configurations from the JSON file.
    with open('config.json', mode='r', encoding="utf-8_sig") as f:
        cf = json.load(f)
    CONSUMER_KEY = cf['consumer_key']
    CONSUMER_SECRET = cf['consumer_secret']
    ACCESS_TOKEN = cf['access_token']
    ACCESS_TOKEN_SECRET = cf['access_token_secret']
    TIMEZONE = cf['timezone']
    INTERVAL_TIME = cf['interval_time']
    ENTRY_KEYWORDS2D = cf['entry_contest']['entry_keywords2d']
    COLLECT_TWEETS = cf['entry_contest']['collect_tweets']
    IGNORE_USERS = cf['entry_contest']['ignore_users']
    DESTROY_LIST_FILENAME = cf['destroy_friendship']['destroy_list_filename']

    # Initialize the API
    api = get_api(CONSUMER_KEY, CONSUMER_SECRET,
                  ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    # Count of my friends
    friends_before = len(api.friends_ids(api.me().screen_name))

    # Collect tweets from my timeline
    if COLLECT_TWEETS['timeline']['is_enable']:
        tweets += api.home_timeline(count=COLLECT_TWEETS['timeline']['count'])

    # Collect tweets from tilmeline of SCREEN_NAME's list
    # Necessary specify the slug parameter(the slug name or numerical ID of the list).
    if COLLECT_TWEETS['list']['is_enable']:
        tweets += api.list_timeline(owner_screen_name=COLLECT_TWEETS['list']['screen_name'],
                                    slug=COLLECT_TWEETS['list']['slug'], count=COLLECT_TWEETS['list']['count'])

    # Collect tweets from searched
    if COLLECT_TWEETS['search']['is_enable']:
        tweets += get_tweets_search(api, que=COLLECT_TWEETS['search']['search_queries'],
                                    lang=COLLECT_TWEETS['search']['lang'], count=COLLECT_TWEETS['search']['count'])

    # Create ignore user id list
    ignore_user_ids = convert_ignore_users_to_ignore_user_ids(IGNORE_USERS)

    # Enter contests
    for index, tweet in enumerate(tweets):
        result = dict()
        tweet_text = tweet.text

        # whether or not to enter a contest
        if is_contest(tweet_text, ENTRY_KEYWORDS2D):
            result['tweet-is_contest'] = True

            # Get screen_names from a tweet_text
            screen_names = extract_screen_names(tweet_text)

            # Convert screen_names to user_ids
            user_ids = [tweet.user.id] + \
                convert_screen_names_to_user_ids(api, screen_names)

            # Enter the contest
            result['follows'], result['retweet'] = do_entry(
                api, user_ids, tweet.id, ignore_user_ids)

        else:
            result['tweet-is_contest'] = False

        # Store results
        result['tweet-url'] = get_tweet_url(tweet.user.screen_name, tweet.id)
        result['tweet-id'] = tweet.id
        result['tweet-text'] = ''.join(
            tweet_text.splitlines())  # Delete return codes
        result['tweet-created_at'] = tweet.created_at + \
            timedelta(hours=TIMEZONE)  # Add hours for your timezone
        results.append(result)

        # Print progress
        print_progress(index, result)

        # Wait a few minutes to keep not to ban my account
        if result['tweet-is_contest']:
            log('i', 'time.sleep(' + str(INTERVAL_TIME) + ')')
            time.sleep(INTERVAL_TIME)

    # Write out the results on a CSV sheet
    write_results(results, output_filename)
    log('i', 'DONE! See the "' + output_filename + '" file.')

    # Count of my friends
    friends_after = len(api.friends_ids(api.me().screen_name))
    log('i', 'Friends: ' +
        str(friends_before) + ' -> ' + str(friends_after))

    # Count of successfully retweeted
    retweet_cnt = 0
    for result in results:
        if result['tweet-is_contest']:
            if result['retweet']['is_retweeted']:
                retweet_cnt += 1
    log('i', 'Successfully retweeted: ' + str(retweet_cnt))

    # Update destroy list
    add_destroy_list(results, DESTROY_LIST_FILENAME, output_filename)
    log('i', 'Added destroy list: ' + DESTROY_LIST_FILENAME)
