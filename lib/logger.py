'''
31st may 2018 thursday
'''

import logging

# setup logging
logFormat= '[%(filename)s %(levelname)s]: %(message)s'
logging.basicConfig(filename='skynet.log',level=logging.INFO, 
                    filemode='w', format=logFormat)

Logger = logging.getLogger('skynet')
