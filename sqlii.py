

try:
	import sys
	from lib.parsers import argumentParser
	from lib.parsers import payloadParser
	from lib.objects import Target
	from lib.controller import initController
	from lib.controller import checkController
	from lib.data.data import target
	from lib.data.data import options
	from lib.common.exception import *
	from lib.common import logger
except ImportError:
	print("ImportError")
	exit()


if sys.version_info < (3,0):
	sys.stdout.write("sqlii requires Python 3.x\nExit.\n")
	sys.exit(1)


def main():
	try:
		msg = '\n[*]Hi, I am learning SQLMAP'
		logger.puts(msg)
		msg = '[*] starting\n'
		logger.puts(msg)

		options.cmdArgs = argumentParser.getArguments()
		initController.initOptions()
		checkController.check()
	except QuitException:
		raise SystemExit
	finally:
		msg = '\n[*] ending'
		logger.puts(msg)





if __name__== "__main__":

	try:
		main()
	except KeyboardInterrupt:
		pass
	except SystemExit:
		raise
