import sys
import ConfigParser
import logging

logger = logging.getLogger('SConsVars')


class TrackedConfig:
    def __init__(self,files):
        self.config=ConfigParser.SafeConfigParser()
        logger.info('Looking for configuration in %s.' % str(files))
        read_from = self.config.read(files)
        logger.info('Read configuration from %s.' % str(read_from))
        self.track=ConfigParser.SafeConfigParser()

    def get(self,section,option):
        result=None
        try:
            result = self.config.get(section,option)
        except (ConfigParser.NoSectionError,ConfigParser.NoOptionError):
            pass
        finally:
            if not self.track.has_section(section):
                self.track.add_section(section)
            if result is not None:
                self.track.set(section,option,result)
            else:
                self.track.set(section,option,'queried but not found')
        return result

    def get_dir(self,section,option):
        result=self.get(section,option)
        if not result: return list()
        else: return result.split(':')

    def get_lib(self,section,option):
        result=self.get(section,option)
        if not result: return list()
        else: return result.split(',')

    def write(self,filename):
        with open(filename,'w') as f:
            self.track.write(f)


cfg = TrackedConfig(['default.cfg',sys.platform+'.cfg','local.cfg'])
