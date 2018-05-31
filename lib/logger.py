'''
31st may 2018 thursday
'''

import logging

# setup logging
logFormat='%(levelname)s: %(message)s'
logging.basicConfig(filename='skynet.log',level=logging.DEBUG, 
                    filemode='w', format=logFormat)

logger = logging.getLogger('skynet')
