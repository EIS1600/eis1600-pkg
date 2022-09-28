class Date:
    def __init__(self, year, month, day, weekday, category):
        self.year = year
        self.month = month
        self.day = day
        self.weekday = weekday
        self.category = category

    def __eq__(self, other):
        return self.year == other.year and self.month == other.month and self.day == other.day and self.weekday == other.weekday and self.category == other.category

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)

    def get_tag(self):
        tag = '@YEA'
        if self.category:
            tag += self.category
        else:
            tag += 'X'

        year = self.year.__str__
        while len(year) < 4:
            year = '0' + year

        tag += year

        return tag + ' '
