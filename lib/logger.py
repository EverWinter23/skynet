'''
31st may 2018 thursday
'''

import logging

# setup logging
"""
    parameters:
        level
            sets the logging level of the logger, logging messages
            which are less severe than level will be ignored.
"""
def get_logger(level = logging.INFO):
    logFormat= '[%(filename)s %(levelname)s]: %(message)s'
    logging.basicConfig(filename='skynet.log',level=level, 
                        filemode='w', format=logFormat)

    return logging.getLogger('skynet')
