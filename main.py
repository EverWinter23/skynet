'''
thursday 7th june 2018
'''

import time
import sys
import lib.logger as log
import arg_actions
from skynet import SkyNet
from lib.parser import Parser


def main():
    # parser to generate config file using command-line interface
    parser = Parser(
        description='Magically syncs a local dir to a remote storage.')
    args = parser.parse_args()

    # setup logging
    logger = log.get_logger(log.lvl_mapping[args.loglvl])

    if args.version:
        arg_actions._version()
        # exit after printing version
        sys.exit()

    if not args.run_with and not args.config:
        logger.info('Storage service not specified.'
                    ' Supported services are {}.'.format(
                        ", ".join(arg_actions.SERVICES)))
        print('Please, specify a storage service.'
              ' Supported services are {}.'.format(
                  ", ".join(arg_actions.SERVICES)))
        print('Use --run-with [SERVICE] to specify a storage service.')
        sys.exit('Exiting, check log for details.')

    # check for config before proceeding
    if not arg_actions._check_config() and not args.config:
        logger.info('No config file found.'.format(
            arg_actions.SKYNET, arg_actions.VERSION))
        print('No config found, please configure {} v{}.'.format(
            arg_actions.SKYNET, arg_actions.VERSION))
        print('You can use --config [SERVICE] option for gen a config.')
        sys.exit('Exiting, check log for exact details.')

    # actions based on parsed arguments
    if args.config:
        arg_actions._config(args.config)
        # exit after configuration
        sys.exit('{} v{} is ready to run.'.format(
            arg_actions.SKYNET, arg_actions.VERSION))

    if args.config_file:
        logger.info('Loading the specified config.')
        arg_actions._load_config(args.config_file)

    skynet = SkyNet(config=arg_actions._get_config(),
                    service=args.run_with,
                    db_path=arg_actions.DB_PATH)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        skynet._stop_execution()


if __name__ == '__main__':
    main()
