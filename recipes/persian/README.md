# Printing persian text

Persian text uses non standard codes and it is quite painfull to print it "out-of-the-box".
This recipe is one solution, it you find a better one open a [Pull Request](https://github.com/BoboTiG/thermalprinter-recipes/issues).

For this snippet to work, you will need to install requirements from [requirements.txt](requirements.txt).

Then, download the file [iran.py](iran.py) and place it next to your code.
It contains the unicode translations for the Iran code page.

Finally, this is the code:
```python
# Imports
from arabic_reshaper import reshape
from bidi import algorithm
from thermalprinter import CodePage, ThermalPrinter

from iran import IRAN_SYSTEM_MAP

# Here we convert and transform the text to print
data = 'سلام. این یک جمله فارسی است\nگل پژمرده خار آید'
data = reshape(data)
data = algorithm.get_display(data)

with ThermalPrinter() as printer:
    # Set the appropriate code page
    printer.codepage(CodePage.IRAN)

    # Justify to the right (as arabic is RTL)
    printer.justify('R')

    # For each line in the text to print (separated by '\n')
    for line in data.splitlines():

        # We decompose the line into characters
        for char in list(line):
            val = ord(char)
            if val > 128:
                # This char seems to be too high to be standard, so try
                # to use the iran code map and use '?' on failure.
                val = IRAN_SYSTEM_MAP.get(val, 0X3F)

            # Send bytes to the printer without line break
            printer.out(bytes([val]), line_feed=False)

        # Print a break line
        printer.feed()

    printer.feed(2)
```

## Credits

Thanks to [@ghorbanpirizad](https://github.com/ghorbanpirizad), we finally found a way for that [issue](https://github.com/BoboTiG/thermalprinter/issues/4).
