from lib.parsers import argumentParser
from lib.data.data import target
from lib.data.data import options
from lib.common import logger
from lib.common.exception import *
from lib.common.common import *

def initOptions():

    #init target
    if options.cmdArgs:
        dict_target = argumentParser.parseArgumentsToTarget(options.cmdArgs)
        if dict_target:
            for key in dict_target:
                setattr(target, key, dict_target[key])

        #TODO
            if target.origValue.isdigit():
                target.origValue_negative = '-{}'.format(randomInt())
            else:
                target.origValue_negative = ''

            msg = '---\n'
            msg += 'Target:\n'
            msg += '\tUrl: {} ({})\n'.format(target.originalUrl, target.method)
            msg += '\tParameter:\n'
            msg += '\t\tName: {}\n'.format(target.paramName)
            msg += '\t\tOrigValue: {}\n'.format(target.origValue)
            msg += '\t\tOrigValue_negative: {}\n'.format(target.origValue_negative)
            msg += '---'
            logger.puts(msg)

        else:
            errorMsg = 'parse arguments failed'
            logger.error(errorMsg)
            raise QuitException
    else:
        errorMsg = 'options not found'
        logger.error(errorMsg)
        raise QuitException




