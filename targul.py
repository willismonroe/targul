import csv

TABLE = 'Table of Cuneiform Signs.csv'

"""
Notes:

Important:
json.dumps(json_text, ensure_ascii=False)
"""


class SignList:
    """The constructor class for assembling signs into a list"""

    def __init__(self, period='ALL', source=TABLE):
        """Defaults to assembling from the included csv file and all periods"""
        self.period = period
        self.source = source

        # create a blank sign list
        self.sign_list = []

    def construct_list(self, skip=2):
        """Parses source file and makes list of signs"""
        with open(self.source) as f:
            # skip number of initial lines
            lines = f.readlines()[skip:]

            # create csv dict reader from lines
            reader = csv.DictReader(lines, fieldnames=['sign', 'codepoint', 'name', 'Borger(2003)', 'Borger(1981)',
                                                       'comments'])
        for line in list(reader):
            # each line is a item from the table
            sign = line['sign']
            codepoint = line['codepoint']
            name = line['name']

            # add Sign object with relevant data to sign list
            self.sign_list.append(Sign(codepoint, sign, name))

    def lookup_sign(self, sign):
        """Returns object from sign"""
        for item in self.sign_list:
            if item.sign == sign:
                return item

    def lookup_codepoint(self, codepoint):
        """Returns object from codepoint"""
        for item in self.sign_list:
            if item.codepoint == codepoint:
                return item

    def lookup_name(self, name):
        """Returns object from name"""
        for item in self.sign_list:
            if item.name == name:
                return item

    def lookup_value(self, value, period='ALL'):
        """Awaiting implementation"""


class Sign(object):
    """This class intends to represent a cuneiform sign and its metadata

    The data contained will include:
        - The cuneiform sign in unicode
        - The standard unicode name and codepoint address
        - Known values (organized by time period in a dict?)
        - Notes

    The class inherits from object so that sign.__dict__ is usable.
    """

    def __init__(self, codepoint, sign, name):
        """Signs are created by their codepoint (for now)"""
        self.codepoint = codepoint
        self.sign = sign
        self.name = name

