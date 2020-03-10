
class Target:
    url = ''
    test_url = ''
    params = {}
    test_param = {'name':None, 'origValue':None, 'original_negative':None}

    method = None
    ptype = None
    boundaries = []
    avaliable_char = []
    #waf = []
    avaliable_techniques = []
    unavaliable_techniques = []

    def __init__(self, attr_dict):
        for key in attr_dict:
            setattr(self, key, attr_dict[key])

    def test(self):
        print(self.url)

    def add_avaliable_technique(self, technique):
        if technique not in self.avaliable_techniques:
            self.avaliable_techniques.append(technique)
            self.unavaliable_techniques.remove(technique)


def createTarget(attr_dict):
    target = Target(attr_dict)
    return target