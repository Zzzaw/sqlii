import optparse
import urllib

from lib.common import logger

def getArguments():
	parse=optparse.OptionParser(usage='"usage:%prog [options] arg1,arg2"',version="%prog 1.2")  
	parse.add_option('-u','--url',dest='url',type=str,help='Target URL (e.g. "http://www.site.com/search.php?id=1")')
	parse.add_option('--method',dest='method',help='Method')
	parse.add_option('--data',dest='data',help='POST data')
	parse.add_option('-p',dest='testParam',help='One parameter for tests')
	parse.add_option('--technique',dest='technique',help='SQL injection techniques to use (T/E/U/B)')

	options,args=parse.parse_args()
	return options

def parseArgumentsToTarget(args):
	target = {}
	target['originalUrl'] = args.url

	#method, url, params
	if args.method == 'GET' :
		query = urllib.parse.urlparse(url=args.url,scheme='http').query
		if query:
			params = dict(_.split('=') for _ in query.split('&'))
			target['method'] = 'GET'
			target['params'] = params
			target['url_without_testParam'] = args.url.replace(query, '')
			target['url_without_query'] = args.url.replace('?' + query, '')
		else:
			print('todo')
	elif args.method == 'POST':
		logger.info('POST is not supported now')
		return None
	else:
		errorMsg = "please input method: GET/POST"
		logger.error(errorMsg)
		return None

	#testable param
	if args.testParam:
		if args.testParam in target['params']:
			target['paramName'] = args.testParam
			target['origValue'] = target['params'][args.testParam]

			for name in target['params'].keys():
				if name != target['paramName']:
					target['url_without_testParam'] += name + '=' + target['params'][name] + '&'
			target['url_without_testParam'] = target['url_without_testParam'][:-1]
		else:
			errorMsg = 'testParam not found'
			logger.error(errorMsg)
	else:
		errorMsg = 'please input testable parameter (e.g. -p "id")'
		logger.error(errorMsg)
		return None

	return target
