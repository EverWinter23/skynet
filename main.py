'''
thursday 7th june 2018
'''

import argactions
from pathlib import Path

def main():
    # parser to generate config file using command-line interface
    parser = Parser(description='Magically syncs a local dir to a remote dir')
    args = parser.parse_args()

    # check for config before proceeding
    if not arg_actions._check_config() and not args.config:
        print('error: A configuration file could not be found,\n'\
              '       please configure {} first...\n\n'.format(arg_actions.SKYNET))
        parser.print_help()
        sys.exit()
    
    # actions based on parsed arguments
    if args.config: 
        arg_actions._config()
        # exit after configuration
        sys.exit()
    if args.version:
        arg_actions._version()
        # exit after printing version
        sys.exit()
    
    skynet = SkyNet(config_file=arg_action._get_config()
                    logging_lvl=args.logging_lvl)   

if __name__ == '__main__':
    main()