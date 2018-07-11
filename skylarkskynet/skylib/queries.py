'''
2nd july 2018 monday
'''
from datetime import datetime

# TODO: Change table name for every project
INSERT_BASE = '''INSERT INTO "pynot_eventnotification" ("action",
"file", "size", "status", "not_time", "parts") VALUES (\'{}\', \'{}\',
 \'{}\', \'{}\', \'{}\', 0)
'''

UPDATE_BASE = '''UPDATE "pynot_eventnotification" SET "status"=\'{}\',
"not_time"=\'{}\', "size"=\'{}\' WHERE "file" = \'{}\'
'''

MARK_BASE = '''UPDATE "pynot_eventnotification" SET "status"=\'{}\',
"not_time"=\'{}\' WHERE "file" = \'{}\'
'''

PART_BASE = '''UPDATE "pynot_eventnotification" SET "parts"="parts" + 1,
"not_time"=\'{}\' WHERE "file" = \'{}\'
'''

TRUNCATE_BASE = '''TRUNCATE pynot_eventnotification
'''

COMPLETE, PENDING, PROCESSING = 'COMPLETE', 'PENDING', 'PROCESSING'


def _lock():
    pass


def _new_notif(action, file, size):
    return INSERT_BASE.format(action, file, size,
                              PENDING, datetime.now())


def _update_notif(file, size):
    return UPDATE_BASE.format(PENDING, datetime.now(),
                              size, file)


def _mark_processing(file):
    return MARK_BASE.format(PROCESSING, datetime.now(),
                            file)


def _mark_complete(file):
    return MARK_BASE.format(COMPLETE, datetime.now(),
                            file)


def _mark_part(file):
    return PART_BASE.format(datetime.now(), file)


def _update_status(file):
    pass


def _truncate_table():
    return TRUNCATE_BASE
