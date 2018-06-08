'''
31st may 2018 thursday
'''

import logging

lvl_mapping = {
    'CRITICAL': logging.CRITICAL,
    'ERROR': logging.ERROR,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
    'NOTSET': logging.NOTSET,
}

# setup logging
"""
    parameters:
        level
            sets the logging level of the logger, logging messages
            which are less severe than level will be ignored.
"""


def get_logger(level=logging.INFO):
    logFormat = '[%(levelname)s %(filename)s %(lineno)d]: %(message)s'
    logging.basicConfig(filename='skynet.log', level=level,
                        filemode='w', format=logFormat)

    return logging.getLogger('skynet')
