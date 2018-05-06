#!/bin/sh
set -eu

model="agenda-model.svg"
out="agenda.svg"
png="agenda.png"
month=$(/bin/date +%B | sed 's/.*/\u&/')
day=$(/bin/date +%d | sed 's/^0//')

[ -f ${out} ] && rm -f ${out}
[ -f ${png} ] && rm -f ${png}
/bin/sed "s/MOIS/${month}/ ; s/JOUR/{$day}/" ${model} >${out}
/usr/bin/convert ${out} -colorspace Gray ${png}
