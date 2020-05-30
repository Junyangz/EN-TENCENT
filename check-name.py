# Lint as: python3
# Copyright 2019, JUNYANG ZHANG mailto: junyangz.iie@gmail.com
#
# Licensed Reseverd
#
#

import requests
from absl import app, flags
import itertools
from string import ascii_lowercase
import json

flags.DEFINE_integer('name_length', 2,
                     'The length of name which you want to check'
                     '-1 for check from 1 to 6(max length)')
flags.DEFINE_string('last_name', 'zhang',
                    'The last name you want to check')
flags.DEFINE_boolean('debug', True,
                     'Wheater enable debug mode, '
                     'debug mode will only gengerate 10 name for check')
flags.DEFINE_string('result_file', './EnglishName/check_result.txt',
                    'The file to write check result.')
flags.DEFINE_string('ref_file', './EnglishName/ref-name-english.csv',
                    'Read reference name from the file, '
                    'name must separate by `lf` or `crlf` and'
                    'name must at first column if last name specified'
                    'example: abcd zhang the Englishname abcd+last_name will be check')

FLAGS = flags.FLAGS

_MAX_LENGTH = 11 - len(FLAGS.last_name)
_STOP_CHECK_FLAG = "---\n"

def check_name(english_name: str, url: str, cookies: dict = {}) -> bool:
    """
    Use request for get name check result.
    """
    payload = {'englishName': english_name}
    r = requests.get(url, params=payload, cookies=cookies)
    if r.status_code == 200 and json.loads(r.json()['Data'])["IsSuccess"]:
        if FLAGS.debug:
            result = 'Name "%s" is avaliable.' % english_name
            print(result)
        return True
    else:
        return False


def name_generate(length: int = 1, from_pre=False, csv: str = None) -> str:
    """
    Generate name for check
    """
    if from_pre and csv != None:
        with open(csv) as pre_name:
            name = pre_name.readline()
            while name != '' and name != '\n' and name != _STOP_CHECK_FLAG:
                yname = name.split()[0].lower()
                if len(yname) <= _MAX_LENGTH:
                    yield yname
                name = pre_name.readline()
        return

    count = 10 if FLAGS.debug else -1
    chars = ascii_lowercase
    for item in itertools.product(chars, repeat=length):
        if count > 0:
            count -= 1
            yield "".join(item)
        elif count == -1:
            yield "".join(item)
        else:
            break


def main(argv):
    del argv  # Unused

    if FLAGS.name_length != -1:
        start = FLAGS.name_length
        end = FLAGS.name_length + 1
    else:
        start = 1
        end = _MAX_LENGTH + 1
    # ep.tencent.com cookies 
    cookies = {'_ga': 'GA1.2.1063074355.1564712104',
               'pgv_pvi': '9486345216',
               '_gcl_au': '1.1.208395210.1574304255',
               'go-user-ep': '73203a2cb12b4ff982756d5902a89e2a'}

    with open(FLAGS.result_file, 'a+') as rf:
        for name_length in range(start, end):
            for name in name_generate(FLAGS.name_length, from_pre=True, csv=FLAGS.ref_file):
                english_name = name+FLAGS.last_name
                if check_name(english_name=english_name,
                              url='https://ep.tencent.com/api/User/CheckEnglishName',
                              cookies=cookies):
                    rf.writelines('\n' + english_name)

if __name__ == "__main__":
    app.run(main)
