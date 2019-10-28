# -*- coding: utf-8 -*-

import requests
import threading
import time
import os
import csv
import argparse
from dateutil.parser import parse
from datetime import datetime

from credentials import API_TOKEN, X_ORG_ID
from exceptions import *

QUEUE = "REFERENCE"

parser = argparse.ArgumentParser(description="Status Updater")
parser.add_argument("-v", "--version", action="version", version="0.1")
parser.add_argument(
    "file",
    nargs="?",
    default="1.csv",
    help="File with status transition information"
)

parser.add_argument(
    "sort_flag",
    nargs="?",
    default="0",
    help="change all (0) or last (1) tickets with same uid"
)

parser.add_argument(
    "n_of_column",
    nargs="?",
    default=9,
    help="Column for yes/no in file"
)

parser.add_argument(
    "first_row",
    nargs="?",
    default=0,
    help="To skip (0) or not to skip (1) first row"
)
args = parser.parse_args()

STATUS = {0: "reviewPositive",
          1: "incorrectReference"}

BACK_STATUS = "referenceReview"


def tasks_key(task):
    return parse(task["createdAt"])


def make_transition(task, new_status):
    transitions = requests.get(
        f"https://api.tracker.yandex.net/v2/issues/{task['id']}/transitions?",
        headers={
            "Authorization": f"OAuth {API_TOKEN}",
            "X-Org-Id": X_ORG_ID
        }
    )

    #  Проверяем, что получили переходы, иначе пишем в лог и продолжаем
    if transitions.status_code not in [200, 201]:
        raise CantGetTransitions

    for transition in transitions.json():
        if transition['to']['key'] == new_status:

            r = requests.post(
                transition['self'] + '/_execute?',
                headers={
                    "Authorization": f"OAuth {API_TOKEN}",
                    "X-Org-Id": X_ORG_ID
                }
            )

            # Записываем результат в лог
            if r.status_code not in [200, 201]:
                print(r.text)
                raise CantMakeTransition
            else:
                return

    raise NoTransition


def main():
    # Сезон-2019 = 152
    log = open('log.txt', 'a')
    logp = open('logp.txt', 'a')
    r = int(args.n_of_column) - 1
    with open(args.file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        rf = int(args.first_row)
        for row in reader:
            uid = row[0]
            if not rf:
                rf = 1
                continue
            if row[r] == "yes":
                # "reviewPositive"
                status_id = 0
            elif row[r] == "no":
                # "incorrectReference"
                status_id = 1
            else:
                print('Incorrect approval data')
                continue
            tasks = requests.post(
                f"https://api.tracker.yandex.net/v2/issues/_search?",
                headers={
                    "Authorization": f"OAuth {API_TOKEN}",
                    "X-Org-Id": X_ORG_ID
                },
                json={
                    "filter": {
                        "queue": QUEUE,
                        "tags": uid,
                        "components": {
                            "id": "152"
                        }
                    }
                }
            )

            if tasks.status_code not in [200, 201]:
                print(uid + ' - connection problem')
                log.write(uid + ' 0 0 101\n')
                continue

            if not tasks.json():
                print(uid + ' - not found')
                log.write(uid + ' 0 0 404\n')
                continue
            if args.sort_flag == "0":
                for ind, task in enumerate(tasks.json()):
                    if task['status']['key'] == STATUS[status_id]:
                        logp.write(uid + ' ' + str(ind + 1) + ' ' + str(len(tasks.json())) + ' 0\n')
                        print(uid, str(ind + 1), str(len(tasks.json())), '0')
                        continue

                    if task['status']['key'] == STATUS[(status_id + 1) % 2]:
                        try:
                            make_transition(task, BACK_STATUS)
                            make_transition(task, STATUS[status_id])
                            logp.write(uid + ' ' + str(ind + 1) + ' ' + str(len(tasks.json())) + ' 1\n')
                            print(uid, str(ind + 1), str(len(tasks.json())), '1')
                        except NoTransition:
                            print(task['status']['key'], 'to', STATUS[status_id], uid, '- transition not found')
                            log.write(uid + ' 0 0 104\n')
                        except CantGetTransitions:
                            print(uid + ' - can\'t get transitions')
                            log.write(uid + str(ind + 1) + ' ' + str(len(tasks.json())) + ' 102\n')
                        except CantMakeTransition:
                            print(uid, '- can\'t make transition')
                            log.write(uid + ' ' + str(ind + 1) + ' ' + str(len(tasks.json())) + ' 103\n')
                        continue

                    try:
                        make_transition(task, STATUS[status_id])
                        logp.write(uid + ' ' + str(ind + 1) + ' ' + str(len(tasks.json())) + ' 1\n')
                        print(uid, str(ind + 1), str(len(tasks.json())), '1')
                    except NoTransition:
                        print(task['status']['key'], 'to', STATUS[status_id], uid, '- transition not found')
                        log.write(uid + ' 0 0 104\n')
                    except CantGetTransitions:
                        print(uid + ' - can\'t get transitions')
                        log.write(uid + str(ind + 1) + ' ' + str(len(tasks.json())) + ' 102\n')
                    except CantMakeTransition:
                        print(uid, '- can\'t make transition')
                        log.write(uid + ' ' + str(ind + 1) + ' ' + str(len(tasks.json())) + ' 103\n')
            else:
                tasks_list = tasks.json()
                tasks_list.sort(key=tasks_key, reverse=True)
                task = tasks_list[0]
                if task['status']['key'] == STATUS[status_id]:
                    logp.write(uid + ' 0\n')
                    print(uid, '0')
                    continue

                if task['status']['key'] == STATUS[(status_id + 1) % 2]:
                    try:
                        make_transition(task, BACK_STATUS)
                        make_transition(task, STATUS[status_id])
                        logp.write(uid + ' 1\n')
                        print(uid, '1')
                    except NoTransition:
                        print(task['status']['key'], 'to', STATUS[status_id], uid, '- transition not found')
                        log.write(uid + ' 0 0 104\n')
                    except CantGetTransitions:
                        print(uid + ' - can\'t get transitions')
                        log.write(uid + ' 102\n')
                    except CantMakeTransition:
                        print(uid, '- can\'t make transition')
                        log.write(uid + ' 103\n')
                    continue

                try:
                    make_transition(task, STATUS[status_id])
                    logp.write(uid + '1\n')
                    print(uid, '1')
                except NoTransition:
                    print(task['status']['key'], 'to', STATUS[status_id], uid, '- transition not found')
                    log.write(uid + ' 0 0 104\n')
                except CantGetTransitions:
                    print(uid + ' - can\'t get transitions')
                    log.write(uid + ' 102\n')
                except CantMakeTransition:
                    print(uid, '- can\'t make transition')
                    log.write(uid + ' 103\n')

    log.write('-\n')
    log.close()
    logp.write('-\n')
    logp.close()


if __name__ == "__main__":
    main()
