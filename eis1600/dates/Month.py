class Month:
    """

    :param int month: month.
    :param int length: number of tokens which make up the date expression.
    """
    def __init__(self, month: int, length: int):
        self.month = month
        self.length = length

    def __eq__(self, other):
        return self.month == other.month and self.length == other.length

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)

    def get_tag(self):
        # Use L because M tags are already used for misc
        tag = 'ÜL'
        tag += str(self.length)
        tag += 'X'

        month = str(self.month)
        while len(month) < 2:
            month = '0' + month

        tag += month

        return tag + 'L '
