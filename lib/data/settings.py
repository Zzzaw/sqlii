
#options
TECHNIQUE_BOOLEAN_BLIND = 'B'
TECHNIQUE_TIME_BLIND = 'T'
TECHNIQUE_ERROR_BASED = 'E'
TECHNIQUE_UNION_BASED = 'U'

#files
FILE_XML_BOUNDARIES = 'data/xml/boundaries.xml'
DIR_XML_PAYLOADS = 'data/xml/payloads'
FILE_XML_BOOLEAN_BLIND = 'data/xml/payloads/boolean_blind.xml'
FILE_XML_TIME_BLIND = 'data/xml/payloads/time_blind.xml'
FILE_XML_ERROR_BASED = 'data/xml/payloads/error_based.xml'
FILE_XML_ERRORS = 'data/xml/errors.xml'

#headers
USER_AGENT = 'sqlii/1.0.0'

#query
METHOD_GET = 'GET'
METHOD_POST = 'POST'

#time_blind check
SLEEP_TIME = '1'
TIME_STDEV_COEFF = 7
MIN_TIME_RESPONSES = 30
MIN_VALID_DELAYED_RESPONSE = 0.5

#checkDynamicContent
UPPER_RATIO_BOUND = 0.98

#payload
PAYLOAD_WHERE_ORIGINAL = 1
PAYLOAD_WHERE_NEGATIVE = 2
PAYLOAD_WHERE_REPLACE = 3


