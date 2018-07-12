'''
31st may 2018 thursday
'''
import os
import errno
import logging

lvl_mapping = {
    'CRITICAL': logging.CRITICAL,
    'ERROR': logging.ERROR,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
    'NOTSET': logging.NOTSET,
}


def get_logger(dirpath, level=logging.INFO):
    """
        parameters:
            level: str
                sets the logging level of the logger, logging messages
                which are less severe than level will be ignored.
            dirpath: str
                path to the directory where config and database
                is stored.
    """
    # make sure path exists
    try:
        os.makedirs(dirpath)
    except OSError as error:
        if error.errno == errno.EEXIST and os.path.isdir(dirpath):
            pass

    filepath = os.path.join(dirpath, 'skynet.log')
    logFormat = '[%(levelname)s %(filename)s %(lineno)d]: %(message)s'
    logging.basicConfig(filename=filepath, level=level,
                        filemode='a', format=logFormat)

    return logging.getLogger('skynet')
