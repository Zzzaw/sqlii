

class Target:
    originalUrl = ''
    url_without_query = ''
    url_without_testParam = ''
    params = {}
    paramName = None
    origValue = None
    origValue_negative = None
    testParam = {'name':None, 'origValue':None, 'original_negative':None}
    method = None
    boundaries = []
    avaliable_char = []
    avaliable_techniques = []

    def __setattr__(self, item, value):
        if not hasattr(self, item):
            raise AttributeError("class has no item '%s'" % item)
        return dict.__setattr__(self, item, value)


class AttribDict(dict):
    cmdArgs = None
    def __getattr__(self, item):
        try:
            return self.__getitem__(item)
        except KeyError:
            raise AttributeError("unable to access item '%s'" % item)

    def __setattr__(self, item, value):
        return dict.__setattr__(self, item, value)

