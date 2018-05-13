# coding: utf-8
"""
Print the weather of the day.
This code can be found on https://github.com/BoboTiG/thermalprinter-recipes
"""
from configparser import ConfigParser
from datetime import datetime

from forecastio import manual
from thermalprinter import CodePage, ThermalPrinter

__version__ = '0.0.6'
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


class Weather:
    data = {}
    printer = None
    fi_params = 'parameters.ini'
    fi_models = 'models.ini'
    url = 'https://api.forecast.io/forecast/{key}/{lat},{lon}?units=ca&lang=fr'

    def __init__(self):
        url = self.url.format(**self.get_params())
        self.forecast = manual(url)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass

    def start(self):
        """ La méthode qui s'occupe de tout gérer. """

        daily = self.forecast.daily()
        today = daily.data[3]
        self.data['icon'] = daily.data[0].icon
        self.data['temp_min'] = int(today.temperatureMin)
        self.data['temp_max'] = int(today.temperatureMax)
        self.data['wind'] = int(today.windSpeed)
        self.data['wind_dir'] = today.windBearing if self.data['wind'] else -1
        self.data['humidity'] = int(today.humidity * 100)
        self.data['precipitations'] = int(today.precipIntensityMax * 100)

        model = self.get_model()

        if not self.set_printer():
            return 1

        self.print_data(model)
        return 0

    def set_printer(self):
        """ Connection to the printer. """

        self.printer = ThermalPrinter()
        return self.printer.status()['paper']

    def get_params(self):
        """ Retrieve parameters. """

        if not self.fi_params:
            return

        ini = ConfigParser()
        ini.read(self.fi_params)
        return ini['general']

    def get_model(self):
        """
        Retrieve all ASCII art models.
        Inspiration: https://github.com/schachmat/wego
        """

        if not self.fi_models:
            return

        ini = ConfigParser()
        ini.read(self.fi_models)
        model = '{}-{}'.format(self.data['icon'],
                               precipitations(self.data['precipitations']))

        # Model name
        try:
            # Example: snow-heavy
            summary = ini['summary'][model]
        except KeyError:
            try:
                # Example: snow
                model = self.data['icon']
                summary = ini['summary'][model]
            except KeyError:
                print('Missing model: {}'.format(model))
                model = 'unknown'
                summary = ini['summary'][model]

        if summary.startswith('::'):
            summary = ini['summary'][summary[2:]]

        self.data['summary'] = summary

        # ASCII art ^^
        ascii_art = ini['models'][model].replace('a', '')
        if ascii_art.startswith('::'):
            ascii_art = ini['models'][ascii_art[2:]].replace('a', '')

        return ascii_art

    def print_data(self, model):
        """ Just print. """

        self.printer.codepage(CodePage.ISO_8859_1)
        self.printer.feed()
        self.printer.out('Weather', bold=True, size='L')
        self.printer.out(datetime.now().strftime('%Y-%m-%d'))
        self.printer.feed()

        lines = model.splitlines()[1:]
        self.printer.out(lines[0])

        # State
        self.printer.out(lines[1].format(self.data['summary']))

        # Temperature
        self.printer.out(lines[2].format(self.data['temp_min'],
                                         self.data['temp_max']))

        # Wind
        part1, part2 = lines[3].split('&')
        self.printer.out(part1, line_feed=False)
        if self.data['wind_dir'] == -1:
            self.printer.out(b'\af', line_feed=False,
                             codepage=CodePage.CP865)
        else:
            char = wind_dir(self.data['wind_dir'])
            if not isinstance(char, bytes):
                self.printer.out(char, line_feed=False)
            else:
                self.printer.out(char, line_feed=False,
                                 codepage=CodePage.THAI2)
        self.printer.out(part2.format(self.data['wind']))

        # Precipitations
        self.printer.out(lines[4].format(self.data['precipitations'],
                                         self.data['humidity']))

        self.printer.feed(3)
        return self.printer.status()['paper']


def precipitations(value):
    """ Precipitations type. """

    if value >= 10:
        return 'heavy'
    elif value >= 2.5:
        return 'moderate'
    return ''


def wind_dir(angle):
    """
    Wind direction arrows.
    `bytes` values are "Thaï 2" characteres.
    """

    directions = [b'\x8e',  # East
                  'NE', 'NE',  # North-East
                  b'\x8d', b'\x8d',  # North
                  'NO', 'NO',  # North-West
                  b'\x8c', b'\x8c',  # West
                  'SO', 'SO',  # South-West
                  b'\x8f', b'\x8f',  # South
                  'SE', 'SE',  # South-East
                  b'\x8e'  # East
                  ]
    return directions[int(angle / 22.5)]


def main():
    with Weather() as weather:
        return weather.start()


if __name__ == '__main__':
    exit(main())
