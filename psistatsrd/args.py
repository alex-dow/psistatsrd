import argparse

parser = argparse.ArgumentParser(description="Psikon InfoScreen")
parser.add_argument("--config-file",dest="config_file", help="Configuration file", default="./psistatsrd.conf")
parser.add_argument('--config-log-file',dest='config_log_file', help='Logging Config File', default='./psistatsrd-log.conf')


args = vars(parser.parse_args())


