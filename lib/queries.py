'''
2nd july 2018 monday
'''
from datetime import datetime

INSERT_BASE = '''INSERT INTO "pynot_eventnotification" ("action",
"file", "status", "not_time") VALUES (\'{}\', \'{}\', \'{}\', \'{}\')
'''
UPDATE_BASE = '''UPDATE "pynot_eventnotification" SET "status"=\'{}\'
WHERE "file" = \'{}\' AND "status"=\'{}\'
'''
COMPLETE, PENDING, PROCESSING = 'COMPLETE', 'PENDING', 'PROCESSING'


def _lock():
    pass


def _new_notification(entry):
    q = INSERT_BASE.format(
        entry['action'], entry['src_path'],
        PENDING, datetime.now())
    print(q)
    return q


def _mark_processing(entry):
    # q = UPDATE COMPANY SET SALARY = 15000 WHERE ID = 3;
    q = UPDATE_BASE.format(PROCESSING, entry['src_path'], PENDING)
    return q


def _mark_complete(entry):
    # q = UPDATE COMPANY SET SALARY = 15000 WHERE ID = 3;
    q = UPDATE_BASE.format(COMPLETE, entry['src_path'], PROCESSING)
    return q


def _update_status(entry):
    pass
