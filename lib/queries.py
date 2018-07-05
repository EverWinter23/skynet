'''
2nd july 2018 monday
'''
from datetime import datetime

# TODO: Change table name for every mapping or project
INSERT_BASE = '''INSERT INTO "pynot_eventnotification" ("action",
"file", "status", "not_time") VALUES (\'{}\', \'{}\', \'{}\', \'{}\')
'''
UPDATE_BASE = '''UPDATE "pynot_eventnotification" SET "status"=\'{}\',
"not_time" = \'{}\' WHERE "file" = \'{}\'
'''
COMPLETE, PENDING, PROCESSING = 'COMPLETE', 'PENDING', 'PROCESSING'


def _lock():
    pass


def _new_notif(entry):
    return INSERT_BASE.format(entry['action'], entry['src_path'],
                              PENDING, datetime.now())


def _update_notif(entry):
    return UPDATE_BASE.format(PENDING, datetime.now(),
                              entry['src_path'], COMPLETE)


def _mark_processing(entry):
    return UPDATE_BASE.format(PROCESSING, datetime.now(),
                              entry['src_path'])


def _mark_complete(entry):
    return UPDATE_BASE.format(COMPLETE, datetime.now(),
                              entry['src_path'])


def _update_status(entry):
    pass
