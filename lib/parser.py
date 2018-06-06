'''
tuesday 5th june 2018
'''

from argparse import ArgumentParser
from argparse import Action

class Parser(ArgumentParser):
    def __init__(self, **kwargs):
        super(Parser, self).__init__(**kwargs)

        # display version
        self.add_argument("--version", action='store_true')
   
        # for configuring logging level
        self.add_argument("-l", "--logging", default='INFO',
            help="set logging level")

        # for changing or generating config
        self.add_argument("--config", action='store_true',
            help="configure settings")
