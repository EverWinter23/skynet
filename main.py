'''
thursday 7th june 2018
command line interface
'''

import time
import sys
import lib.logger as log
import skyconf
from skynet import SkyNet
from lib.parser import Parser


def main():
    # parser to generate config file using command-line interface
    parser = Parser(
        description='Magically syncs a local dir to a remote storage.')
    args = parser.parse_args()

    # setup logging
    logger = log.get_logger(skyconf.DIR_PATH,
                            log.lvl_mapping[args.loglvl])

    if args.version:
        skyconf._version()
        # exit after printing version
        sys.exit()

    if not args.run_with and not args.config:
        logger.info('Storage service not specified.'
                    ' Supported services are {}.'.format(
                        ", ".join(skyconf.SERVICES)))
        print('Please, specify a storage service.'
              ' Supported services are {}.'.format(
                  ", ".join(skyconf.SERVICES)))
        print('Use --run-with [SERVICE] to specify a storage service.')
        sys.exit('Exiting, check log for details.')

    # check for config before proceeding
    if not skyconf._check_config() and not args.config:
        logger.info('No config file found.'.format(
            skyconf.SKYNET, skyconf.VERSION))
        print('No config found, please configure {} v{}.'.format(
            skyconf.SKYNET, skyconf.VERSION))
        print('You can use --config [SERVICE] option for gen a config.')
        sys.exit('Exiting, check log for exact details.')

    # actions based on parsed arguments
    if args.config:
        skyconf._config(args.config)
        # exit after configuration
        sys.exit('{} v{} is ready to run.'.format(
            skyconf.SKYNET, skyconf.VERSION))

    if args.config_file:
        logger.info('Loading the specified config.')
        skyconf._load_config(args.config_file)

    skynet = SkyNet(config=skyconf._get_config(),
                    service=args.run_with,
                    db_path=skyconf.DB_PATH)
    skynet._start_execution()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        skynet._stop_execution()


if __name__ == '__main__':
    main()
