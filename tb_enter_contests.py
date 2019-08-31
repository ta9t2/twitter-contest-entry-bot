#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This bot is for automatically to join contests on Twitter

import csv
import sys
import time

import tweepy

import tb_common as tbc


def print_progress(index, result):
    mess = list()
    mess += ['---------- [{m1}] ----------------------------------------'.format(
        m1=(index + 1))]
    mess += ['tweet_url: {m1}'.format(m1=result['retweet']['tweet_url'])]
    mess += ['tweet_text: {m1}'.format(m1=result['retweet']['tweet_text'])]
    mess += ['retweet: {m1}'.format(m1=result['retweet']['comment'])]
    for follow in result['follows']:
        userstr = tbc.get_userstr(
            user_id=follow['user_id'], screen_name=follow['screen_name'], name=follow['name'])
        mess += ['follow: {m1} -> {m2}'.format(m1=userstr,
                                               m2=follow['comment'])]
    for mes in mess:
        tbc.log('i', mes=mes)
    return


def write_added_friend_list(follows, filename):
    # user_id, screen_name, name
    with open(filename, mode='a', encoding="utf-8_sig") as f:
        writer = csv.writer(f, delimiter=',', quotechar='"',
                            lineterminator='\n', quoting=csv.QUOTE_ALL)
        for follow in follows:
            if follow['is_followed']:
                writer.writerow(
                    [follow['user_id'], follow['screen_name'], follow['name']])
    return


def write_result(result, filename):
    # tweet_url, tweet_id, tweet_text, is_retweeted, comment, userstr, is_followed, comment
    row_head = list()
    row_head += [result['retweet']['tweet_url']]
    row_head += [result['retweet']['tweet_id']]
    row_head += [result['retweet']['tweet_text']]
    row_head += [result['retweet']['is_retweeted']]
    row_head += [result['retweet']['comment']]

    with open(filename, mode='a', encoding="utf-8_sig") as f:
        writer = csv.writer(f, delimiter=',', quotechar='"',
                            lineterminator='\n', quoting=csv.QUOTE_ALL)
        for follow in result['follows']:
            row = list()
            row.extend(row_head)
            row += [tbc.get_userstr(follow['user_id'],
                                    follow['screen_name'], follow['name'])]
            row += [follow['is_followed']]
            row += [follow['comment']]
            writer.writerow(row)
    return


if __name__ == '__main__':
    tbc.log_init()
    tbc.log('i', mes='START SCRIPT')

    # Load configurations from the JSON file.
    CONFIG = tbc.load_config()

    # Set result file name
    result_filename = '{result_dir}/entry_{datetime}.csv'.format(
        result_dir=CONFIG['result_dir'], datetime=tbc.get_timenow())

    # Load contests
    contests = list()
    try:
        with open(CONFIG['entry_contest']['contest_list_filename'], mode='r', encoding='utf-8_sig') as f:
            reader = csv.reader(f, delimiter=',', quoting=csv.QUOTE_ALL)
            for row in reader:
                contest = dict()
                contest['tweet_id'] = int(row[0])
                contest['user_ids'] = [int(col.strip())
                                       for col in row[1].split(',')]
                contest['tweet_url'] = row[2]
                contest['tweet_text'] = row[3]
                contests.append(contest)
    except Exception as e:
        tbc.log('e', mes=e, func=str(
            sys._getframe().f_code.co_name), hdlg=tbc.ABORT)

    # Initialize the API
    api = tbc.twp_get_api(CONFIG['consumer_key'], CONFIG['consumer_secret'],
                          CONFIG['access_token'], CONFIG['access_token_secret'])

    # Count of my friends
    friends_before = len(api.friends_ids(api.me().screen_name))

    # Do entry
    retweet_cnt = 0
    for index, contest in enumerate(contests):
        result = dict()

        # Follow
        result['follows'] = tbc.twp_follow_user_ids(api, contest['user_ids'])

        # Retweet
        result['retweet'] = tbc.twp_retweet_tweet_id(api, contest['tweet_id'])
        result['retweet']['tweet_url'] = contest['tweet_url']
        result['retweet']['tweet_text'] = contest['tweet_text']

        # Print progress
        print_progress(index, result)

        # Update(Add) destroy friend list
        write_added_friend_list(
            result['follows'], CONFIG['destroy_friendship']['destroy_list_filename'])

        # Write result
        write_result(result, result_filename)

        # Count of successfully retweeted
        retweet_cnt += 1 if result['retweet']['is_retweeted'] else 0

        # Wait a few minutes to keep not to ban my account
        tbc.log('i', mes='Waiting: time.sleep({it})'.format(
            it=CONFIG['interval_time']))
        time.sleep(CONFIG['interval_time'])

    # Print count of successfully retweeted
    tbc.log('i', mes='Successfully retweeted: {rc}'.format(rc=retweet_cnt))

    # Print & Count of my friends
    friends_after = len(api.friends_ids(api.me().screen_name))
    tbc.log(
        'i', mes='Friends: {fb} -> {fa}'.format(fb=friends_before, fa=friends_after))

    # Clear contest list
    with open(CONFIG['entry_contest']['contest_list_filename'], mode='w', encoding='utf-8_sig') as f:
        writer = csv.writer(f, delimiter=',', quotechar='"',
                            lineterminator='\n', quoting=csv.QUOTE_ALL)
        writer.writerow([])
    tbc.log('i', mes='Cleared the contest list: filename={fn}'.format(
        fn=CONFIG['entry_contest']['contest_list_filename']))

    tbc.log('i', mes='DONE')
