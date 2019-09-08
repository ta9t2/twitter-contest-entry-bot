#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This bot is for automatically to collec contests on Twitter

import re
import sys
import csv

import tweepy

import tb_common as tbc


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


if __name__ == '__main__':
    tbc.log_init()
    tbc.log('i', mes='START SCRIPT')

    # Load configurations from the JSON file.
    CONFIG = tbc.load_config()

    # Initialize the API
    api = tbc.twp_get_api(CONFIG['consumer_key'], CONFIG['consumer_secret'],
                          CONFIG['access_token'], CONFIG['access_token_secret'])

    # Make tweet list
    tweets = list()

    # Collect tweets from my timeline
    CT = CONFIG['entry_contest']['collect_tweets']['timeline']
    if CT['is_enable']:
        try:
            tweets += api.home_timeline(count=CT['count'])
        except tweepy.error.TweepError as e:
            tbc.log('e', mes=e, func=str(
                sys._getframe().f_code.co_name), hdlg=tbc.CONTD)

    # Collect tweets from tilmeline of SCREEN_NAME's list
    # Necessary specify the slug parameter(the slug name or numerical ID of the list).
    CT = CONFIG['entry_contest']['collect_tweets']['list']
    if CT['is_enable']:
        try:
            tweets += api.list_timeline(
                owner_screen_name=CT['screen_name'], slug=CT['slug'], count=CT['count'])
        except tweepy.error.TweepError as e:
            tbc.log('e', mes=e, func=str(
                sys._getframe().f_code.co_name), hdlg=tbc.CONTD)

    # Collect tweets from searched
    CT = CONFIG['entry_contest']['collect_tweets']['search']
    if CT['is_enable']:
        try:
            # Unspecified tweet_mode - Tweets are stored in each SearchResult.text
            tweets += api.search(q=CT['search_queries'], lang=CT['lang'],
                                 result_type='recent', count=CT['count'])

            # tweet_mode="extended" - Tweets are stored in each SearchResult.full_text
            # result_tweets = api.search(q=que, lang=lang', result_type='recent', count=count, tweet_mode="extended")
        except tweepy.error.TweepError as e:
            tbc.log('e', mes=e, func=str(
                sys._getframe().f_code.co_name), hdlg=tbc.CONTD)

    # Get ignore users and Convert screen_name to user_id
    ignore_user_ids = tbc.twp_convert_screen_names_to_user_ids(
        api, CONFIG['entry_contest']['ignore_users'])

    # Make contests list
    contests = list()
    for tweet in tweets:

        # Get a tweet url
        tweet_url = tbc.get_tweet_url(tweet.user.screen_name, tweet.id)

        # Get a tweet text excluding return codes
        tweet_text = ''.join(tweet.text.splitlines())

        # whether or not a contest
        if not is_contest(tweet.text, CONFIG['entry_contest']['entry_keywords2d']):
            tbc.log('i', mes='Skipped, for the tweet is NOT a contest: url={tweet_url}, tweet.text={text}'.format(
                tweet_url=tweet_url, text=tweet_text))
            continue

        # Get screen_names from a user object and a tweet.text
        # Convert screen_name to user_id
        screen_names = [tweet.user.screen_name] + \
            extract_screen_names(tweet.text)
        user_ids = tbc.twp_convert_screen_names_to_user_ids(api, screen_names)

        # whether or not a icluding ignore list
        if tbc.is_ignore(user_ids, ignore_user_ids):
            tbc.log('i', mes='Skipped, for the tweet is in ignore user(s): url={tweet_url}, tweet.text={text}'.format(
                tweet_url=tweet_url, text=tweet_text))
            continue

        # Store contest info
        contest = dict()
        contest['tweet_id'] = tweet.id
        contest['user_ids'] = user_ids
        contest['tweet_url'] = tweet_url
        contest['tweet_text'] = tweet_text
        contests.append(contest)
        tbc.log('i', mes='Stored the list, for the tweet is a contest: url={tweet_url}, tweet.text={text}'.format(
            tweet_url=tweet_url, text=tweet_text))

    # Write out the contest list on a CSV sheet
    with open(CONFIG['entry_contest']['contest_list_filename'], mode='w', encoding='utf-8_sig') as f:
        writer = csv.writer(f, delimiter=',', quotechar='"',
                            lineterminator='\n', quoting=csv.QUOTE_ALL)
        for contest in contests:
            user_ids_str = ''
            for user_id in contest['user_ids']:
                user_ids_str += str(user_id) + ','
            user_ids_str = user_ids_str[:-1:]
            writer.writerow([contest['tweet_id'], user_ids_str,
                             contest['tweet_url'], contest['tweet_text']])
    tbc.log('i', mes='Wrote the contest tweet list: filename={fn}.'.format(
        fn=CONFIG['entry_contest']['contest_list_filename']))

    tbc.log('i', mes='DONE')
