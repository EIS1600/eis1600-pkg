from typing import Literal


class Date:
    """

    :param int year: year.
    :param int month: month.
    :param int day: day.
    :param int weekday: day of the week (Islamic calendar).
    :param int length: number of tokens which make up the date expression.
    :param Literal['B', 'D', 'K', 'H', 'P', 'L'] category:
    """
    def __init__(self, year: int, month: int, day: int, weekday: int, length: int,
            category: Literal['B', 'D', 'K', 'H', 'P', 'L'] = 'X'):
        self.year = year
        self.month = month
        self.day = day
        self.weekday = weekday
        self.length = length
        self.category = category

    def __eq__(self, other):
        return self.year == other.year and self.month == other.month and self.day == other.day and self.weekday == \
               other.weekday and self.category == other.category

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)

    def get_tag(self):
        tag = 'ÜY'
        tag += str(self.length)
        tag += self.category

        year = str(self.year)
        while len(year) < 4:
            year = '0' + year

        tag += year

        return tag + 'Y '
