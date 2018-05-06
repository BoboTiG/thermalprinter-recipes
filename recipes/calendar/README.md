# Calendar

Print daily stuff from your Google Calendar.

## Preview

![Preview][preview]

[preview]: preview.png

## Files

- `agenda-model.svg`: the picture model for the cool image header.
- `calendar.py`: the actual Python code that will do the work.
- `requirements.txt`: required modules to install.
- `update-agenda.sh`: update script for the image header.

## Requirements

Fill the `url` attribute with the [exported calendar link](https://support.google.com/calendar/answer/37111).

Let's say your email ID is "foo@bar.com", the URL should be something like:

    https://calendar.google.com/calendar/ical/foo%%40bar.com/private-XXX/basic.ics

## Image Header Update

You have to call `update-agenda.sh` daily to generate the good picture according to the current day.
It will create the file agenda.png with the good month name and day number.

Personally, I use a cron job to call this script but you can do whatever you want.
