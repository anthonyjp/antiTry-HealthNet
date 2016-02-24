from __future__ import print_function
from enum import Enum

import re
import os
import sys

from datetime import datetime as dt
from subprocess import check_output, STDOUT, CalledProcessError
from os import path

SHA_REGEX = re.compile('[0-9a-f]{5,40}')
__LAST_SHA = path.expanduser(path.join('~', '.antitry-git2svn', 'last_sha'))
__COMMIT_TMP = 'svn-commit.tmp'


class PromptAnswers(Enum):
    SUCCESS = 0
    FAILURE = 1
    CONTINUE = 2


def prompt(prompt: str,
           predicate,
           err=lambda x: False) -> bool:
    while True:
        ans = input(prompt)
        state = predicate(ans)
        err_info = {}

        if isinstance(state, tuple):
            err_info = state[1]
            state = state[0]

        if state == PromptAnswers.SUCCESS:
            return True
        elif state == PromptAnswers.FAILURE and not err(err_info):
            return False


def warn(*objs):
    print(*objs, file=sys.stderr, flush=True)


def main():

    def handle_answer(input: str) -> PromptAnswers:
        if input.lower() == 'y':
            return PromptAnswers.SUCCESS
        elif input.lower() == 'n':
            return PromptAnswers.FAILURE
        else:
            return PromptAnswers.CONTINUE

    git_items = []  # type: List[GitItem]
    latest_sha = None  # type: str
    exec_args = ['git', 'log']

    os.makedirs(path.dirname(__LAST_SHA), exist_ok=True)

    if not path.exists(__LAST_SHA):
        if len(sys.argv) > 1 and SHA_REGEX.match(sys.argv[1]):
            latest_sha = sys.argv[1]
        else:
            warn('No file found at', __LAST_SHA, 'assuming first run...')
    else:
        with open(__LAST_SHA, 'r') as sha_file:
            line = sha_file.readline().strip()
            if SHA_REGEX.match(line):
                latest_sha = line
            else:
                warn('Invalid SHA-1 in', __LAST_SHA, 'please provide last git SHA-1 as argument!')

    if not prompt('We are going to use %s as the SHA-1, continue?: ' % latest_sha, handle_answer):
        print('Exiting...')
        exit()

    if latest_sha is not None:
        exec_args.append('%s..HEAD' % latest_sha)

    check_output(['git', 'pull', 'origin', 'master'], stderr=STDOUT, shell=True)
    check_output(['svn', 'add', '--force', '*', '--auto-props', '--parents', '--depth', 'infinity', '-q'], stderr=STDOUT, shell=True)

    log_data = check_output(exec_args, stderr=STDOUT, shell=True).decode()

    if log_data.strip() == '':
        warn('No new log information.')
        exit()

    # Start parsing through log information
    new_latest_sha = None
    sha1 = None  # type: str
    author = None  # type: str
    date = None  # type: str
    content = []

    for line in re.compile('\r?\n').split(log_data):
        if date:  # Rest of data is commit message until 'commit'
            if not line.startswith('commit'):
                # Put lines in list
                content.append(line.strip())
                continue
            else:
                # Create Git Item, we've reached the end of one message
                git_items.append(GitItem(sha1, author, date, '\n'.join(content)))
                if not new_latest_sha: new_latest_sha = sha1  # First sha will be new latest next run
                sha1 = author = date = None  # reset vars
                content = []

        # Parsing
        sp_idx = line.index(' ')
        tag, data = line[0:sp_idx], line[sp_idx+1:].strip()

        if tag == 'commit':
            if latest_sha == data:
                break
            sha1 = data
        elif tag == 'Author:':
            author = data
        elif tag == 'Date:':
            date = data

    # Condense GitItems, items next to each other with same author are turned into a single GitItem
    compress(git_items)

    print('\n\n'.join([x.canonical() for x in git_items]))

    with open(__LAST_SHA, 'w') as sha_file:
        sha_file.writelines([new_latest_sha])

    with open(__COMMIT_TMP, 'w') as cmt_file:
        cmt_file.write('---\n\n'.join([x.canonical() for x in git_items]))

    try:
        check_output(['svn', 'commit', '-F', __COMMIT_TMP], stderr=STDOUT, shell=True)
        os.remove(__COMMIT_TMP)
    except CalledProcessError:
        print('Done! To commit, type: svn commit -F', __COMMIT_TMP,
              'or use TortoiseSVN to commit using the message in the file!')


class GitItem(object):
    def __init__(self, sha1: str, author: str, date: str, content: str):
        self.sha = sha1.strip()
        self.author = author.strip()
        self.date = [dt.strptime(date.strip(), '%a %b %d %H:%M:%S %Y %z')]
        self.details = content.strip()

    def canonical(self):
        return '%s on %s:\n\n%s\n\n' % (self.author, self.timestamp(), self.details)

    def timestamp(self):
        return ', '.join(x.strftime('%x %X') for x in self.date)

    def __str__(self):
        return '%s by %s on %s' % (self.sha, self.author, self.timestamp())

    def __repr__(self):
        return self.__str__()


def compress(log_items):
    new_list = []
    cur_item = None

    for item in log_items:
        if cur_item is None or cur_item.author != item.author:
            new_list.append(cur_item)
            cur_item = item
        else:
            cur_item.details += '\n' + item.details
            item.date.extend(cur_item.date)
            cur_item.date = item.date

    new_list.append(cur_item)
    log_items.clear()
    log_items.extend(new_list[1:])


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'clean':
        print('Removing', __LAST_SHA, '...')
        if path.exists(__LAST_SHA):
            os.remove(__LAST_SHA)
            print('Done!')
        else:
            print('Not Found! Is it already gone?')
    else:
        main()
