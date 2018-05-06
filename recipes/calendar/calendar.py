# coding: utf-8
"""
Print daily stuff from your Google Calendar.
This code can be found on https://github.com/BoboTiG/thermalprinter-recipes
"""

from datetime import datetime, timedelta
from textwrap import wrap

from PIL import Image
from icalevents import icalevents
from pytz import utc
from thermalprinter import CodePage, ThermalPrinter

__version__ = '0.0.5'
__author__ = "Mickaël 'Tiger-222' Schoentgen"
__copyright__ = """
Copyright (c) 2016-2018, Mickaël 'Tiger-222' Schoentgen

Permission to use, copy, modify, and distribute this software and its
documentation for any purpose and without fee or royalty is hereby
granted, provided that the above copyright notice appear in all copies
and that both that copyright notice and this permission notice appear
in supporting documentation or portions thereof, including
modifications, that you make.
"""


class Calendar:
    printer = None
    url = 'GOOGLE_CALENDAR_URL'

    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass

    def start(self):
        """ La méthode qui s'occupe de tout gérer. """

        events = self.get_events()
        if events:
            if not self.set_printer():
                return 1
            self.print_data(events)
        return 0

    def set_printer(self):
        """ Connection to the printer. """

        self.printer = ThermalPrinter()
        return self.printer.status()['paper']

    def get_events(self):
        """ Retrieve events of the day. """

        now = utc.localize(datetime.utcnow())
        events = icalevents.events(url=self.url, end=now + timedelta(days=1))
        data = []
        for event in events:
            data.append((
                event.start.strftime('%H:%M'),
                event.end.strftime('%H:%M'),
                event.summary))
        return sorted(set(data), key=lambda x: x[0])

    def print_data(self, events):
        """ Just print. """

        def header():
            """ Print the header. """
            self.printer.codepage(CodePage.ISO_8859_1)
            self.printer.feed()
            self.printer.image(Image.open('agenda.png'))
            self.printer.feed()

        def line(evt, first_line=False, last_line=False):
            """ Impression d'un événement. """

            start, end, sumary = evt
            hour = '{} - {}'.format(start, end)
            if start == end:
                hour = 'Whole day'

            if first_line:
                self.printer.out(b'\xd5', line_feed=False,
                                 codepage=CodePage.CP437)
                self.printer.out(b'\xcd' * (self.printer.max_column - 2),
                                 line_feed=False, codepage=CodePage.CP437)
                self.printer.out(b'\xb8', codepage=CodePage.CP437)

            self.printer.out(b'\xb3', line_feed=False,
                             codepage=CodePage.CP437)
            self.printer.out(
                ' {0: <{1}} '.format(hour, self.printer.max_column - 4),
                line_feed=False,
                codepage=CodePage.ISO_8859_1)
            self.printer.out(b'\xb3', codepage=CodePage.CP437)

            for line_ in wrap(sumary, self.printer.max_column - 4):
                self.printer.out(b'\xb3', line_feed=False,
                                 codepage=CodePage.CP437)
                self.printer.out(
                    ' {0: <{1}} '.format(line_, self.printer.max_column - 4),
                    line_feed=False,
                    codepage=CodePage.ISO_8859_1)
                self.printer.out(b'\xb3', codepage=CodePage.CP437)

            if not last_line:
                self.printer.out(b'\xc3', line_feed=False,
                                 codepage=CodePage.CP437)
                self.printer.out(b'\xc4' * (self.printer.max_column - 2),
                                 line_feed=False, codepage=CodePage.CP437)
                self.printer.out(b'\xb4', codepage=CodePage.CP437)
            else:
                self.printer.out(b'\xd4', line_feed=False,
                                 codepage=CodePage.CP437)
                self.printer.out(b'\xcd' * (self.printer.max_column - 2),
                                 line_feed=False, codepage=CodePage.CP437)
                self.printer.out(b'\xbe', codepage=CodePage.CP437)

        def footer():
            """ Printed the footer. """

            self.printer.feed()
            self.printer.out('Have a nice day :)', justify='C',
                             codepage=CodePage.ISO_8859_1)
            self.printer.feed(4)

        header()
        if events:
            first, last = events[0], events[-1]
            for event in events:
                line(event,
                     first_line=event is first,
                     last_line=event is last)
        footer()

        return self.printer.status()['paper']


def main():
    with Calendar() as calendar:
        return calendar.start()


if __name__ == '__main__':
    exit(main())
