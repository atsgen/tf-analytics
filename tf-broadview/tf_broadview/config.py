#
# Copyright (c) 2015 Juniper Networks, Inc. All rights reserved.
#

from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import object
import argparse, os, sys, re
from six.moves import configparser
from pysandesh.sandesh_base import *
from pysandesh.gen_py.sandesh.ttypes import SandeshLevel
from . import device_config

class CfgParser(object):
    CONF_DEFAULT_PATH = '/etc/tungstenfabric/tf-broadview.conf'
    def __init__(self, argv):
        self._args = None
        self.__pat = None
        self._argv = argv or ' '.join(sys.argv[1:])

    def parse(self):
        '''
            command line example
tf-broadview [-h] [-c FILE]
                         [--analytics_api ANALYTICS_API [ANALYTICS_API ...]]
                         [--collectors COLLECTORS [COLLECTORS ...]]
                         [--log_file LOG_FILE] [--log_local]
                         [--log_category LOG_CATEGORY] [--log_level LOG_LEVEL]
                         [--use_syslog] [--syslog_facility SYSLOG_FACILITY]
                         [--scan_frequency SCAN_FREQUENCY]
                         [--http_server_port HTTP_SERVER_PORT]

optional arguments:
  -h, --help            show this help message and exit
  -c FILE, --conf_file FILE
                        Specify config file
  --analytics_api ANALYTICS_API [ANALYTICS_API ...]
                        List of analytics-api IP addresses in ip:port format
  --collectors COLLECTORS [COLLECTORS ...]
                        List of Collector IP addresses in ip:port format
  --log_file LOG_FILE   Filename for the logs to be written to
  --log_local           Enable local logging of sandesh messages
  --log_category LOG_CATEGORY
                        Category filter for local logging of sandesh messages
  --log_level LOG_LEVEL
                        Severity level for local logging of sandesh messages
  --use_syslog          Use syslog for logging
  --syslog_facility SYSLOG_FACILITY
                        Syslog facility to receive log lines
  --scan_frequency SCAN_FREQUENCY
                        Time between snmp poll
  --http_server_port HTTP_SERVER_PORT
                        introspect server port

        '''
        # Source any specified config/ini file
        # Turn off help, so we print all options in response to -h
        conf_parser = argparse.ArgumentParser(add_help=False)

        kwargs = {'help': "Specify config file", 'metavar':"FILE",
                  'action':'append'
                 }
        if os.path.exists(self.CONF_DEFAULT_PATH):
            kwargs['default'] = [self.CONF_DEFAULT_PATH]
        conf_parser.add_argument("-c", "--conf_file", **kwargs)
        args, remaining_argv = conf_parser.parse_known_args(self._argv.split())

        defaults = {
            'collectors'      : ['127.0.0.1:8086'],
            'analytics_api'   : ['127.0.0.1:8081'],
            'log_local'       : False,
            'log_level'       : SandeshLevel.SYS_DEBUG,
            'log_category'    : '',
            'log_file'        : Sandesh._DEFAULT_LOG_FILE,
            'use_syslog'      : False,
            'syslog_facility' : Sandesh._DEFAULT_SYSLOG_FACILITY,
            'scan_frequency'  : 60,
            'http_server_port': 5922,
            'zookeeper'       : '127.0.0.1:2181',
            'device_file'     : '/etc/contrail/bv_devices.conf',
        }
        defaults.update(SandeshConfig.get_default_options(['DEFAULTS']))
        sandesh_opts = SandeshConfig.get_default_options()

        config = None
        if args.conf_file:
            config = configparser.SafeConfigParser()
            config.optionxform = str
            config.read(args.conf_file)
            if 'DEFAULTS' in config.sections():
                defaults.update(dict(config.items("DEFAULTS")))
            SandeshConfig.update_options(sandesh_opts, config)
        # Override with CLI options
        # Don't surpress add_help here so it will handle -h
        parser = argparse.ArgumentParser(
            # Inherit options from config_parser
            parents=[conf_parser],
            # print script description with -h/--help
            description=__doc__,
            # Don't mess with format of description
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        defaults.update(sandesh_opts)
        parser.set_defaults(**defaults)
        parser.add_argument("--analytics_api",
            help="List of analytics-api IP addresses in ip:port format",
            nargs="+")
        parser.add_argument("--collectors",
            help="List of Collector IP addresses in ip:port format",
            nargs="+")
        parser.add_argument(
            "--log_file",
            help="Filename for the logs to be written to")
        parser.add_argument("--log_local", action="store_true",
            help="Enable local logging of sandesh messages")
        parser.add_argument(
            "--log_category",
            help="Category filter for local logging of sandesh messages")
        parser.add_argument(
            "--log_level",
            help="Severity level for local logging of sandesh messages")
        parser.add_argument("--use_syslog",
            action="store_true",
            help="Use syslog for logging")
        parser.add_argument("--syslog_facility",
            help="Syslog facility to receive log lines")
        parser.add_argument("--scan_frequency", type=int,
            help="Time between snmp poll")
        parser.add_argument("--http_server_port", type=int,
            help="introspect server port")
        parser.add_argument("--device_file",
            help="boardview devices")
        parser.add_argument("--zookeeper",
            help="ip:port of zookeeper server")
        SandeshConfig.add_parser_arguments(parser)
        self._args = parser.parse_args(remaining_argv)
        if isinstance(self._args.collectors, (basestring, str)):
            self._args.collectors = self._args.collectors.split()
        if isinstance(self._args.analytics_api, (basestring, str)):
            self._args.analytics_api = self._args.analytics_api.split()

        self._args.config_sections = config
        self.devices = device_config.DeviceConfig.from_file(
                            self.device_file())

    def get_prouters(self):
        self.devices = device_config.DeviceConfig.from_file(
                            self.device_file())
        return self.devices

    def get_remote_info(self, info):
        for d in self.devices:
            if d.ip() == info:
                return d
        return device_config.DeviceConfig(info.replace('.', '-'),
                dict(ip=info, port=0))

    def _pat(self):
        if self.__pat is None:
           self.__pat = re.compile(', *| +')
        return self.__pat

    def _mklist(self, s):
        return self._pat().split(s)

    def collectors(self):
        return self._args.collectors

    def zookeeper_server(self):
        return self._args.zookeeper

    def analytics_api(self):
        return self._args.analytics_api

    def log_local(self):
        return self._args.log_local

    def log_category(self):
        return self._args.log_category

    def log_level(self):
        return self._args.log_level

    def log_file(self):
        return self._args.log_file

    def use_syslog(self):
        return self._args.use_syslog

    def syslog_facility(self):
        return self._args.syslog_facility

    def frequency(self):
        return self._args.scan_frequency

    def http_port(self):
        return self._args.http_server_port

    def device_file(self):
        return self._args.device_file

    def sandesh_config(self):
        return SandeshConfig.from_parser_arguments(self._args)
