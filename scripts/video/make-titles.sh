#!/bin/bash
# Title cards and caption overlays for the showcase cut (durations match edit.py).
cd "$(dirname "$0")/../.."
T() { node scripts/video/titles.mjs "video/titles/$1" "$2" "$3" > /dev/null; echo "$1"; }
e() { python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$1"; }
T same 1.7 "scene=same"
T skies 1.7 "scene=skies"
T watch 1.7 "scene=watch"
T logo 3.4 "scene=logo"
T end 4.0 "scene=end"
B=$(e "Captured in browser")
T p_ph 3.2 "scene=place&name=Manila&sub=$(e 'Philippines · bahay kubo')"
T p_th 2.5 "scene=place&name=Bangkok&sub=$(e 'Thailand · by the canal')"
T p_id 2.5 "scene=place&name=Jakarta&sub=$(e 'Indonesia · joglo')"
T p_sg 2.5 "scene=place&name=Singapore&sub=$(e 'black-and-white bungalow')"
T o_globe 6 "scene=ov&chip=Choose&label=$(e ' a place')&cap=$(e 'Spin the globe. Each place has its own house and sun path.')&badge=$B"
T o_tiki 3.5 "scene=ov&hi=1&chip=Learn&label=$(e ' with Tiki')&cap=$(e 'Tiki the gecko teaches by doing.')&badge=$B"
T o_place 6 "scene=ov&hi=1&chip=Play&label=$(e ' block the view')&cap=$(e 'Place a screen so the neighbour cannot see the reader.')&badge=$B"
T o_sun 4.5 "scene=ov&hi=1&chip=Play&label=$(e ' move the sun')&cap=$(e 'Drag the sun. Shadows follow the city’s sun path.')&badge=$B"
T o_day 5.5 "scene=ov&hi=1&chip=Check&label=$(e ' live the day')&cap=$(e 'Live the day: every rule checked, hour by hour.')&badge=$(e 'Captured in browser · 2×')"
T o_ph3 2.5 "scene=ov&hi=1&chip=Twist&label=$(e ' Manila')&cap=$(e 'Typhoon wind comes in low.')&badge=$B"
T o_th1 2.5 "scene=ov&hi=1&chip=Twist&label=$(e ' Bangkok')&cap=$(e 'Long-tail boats pass on the canal.')&badge=$B"
T o_id1 2.5 "scene=ov&hi=1&chip=Twist&label=$(e ' Jakarta')&cap=$(e 'Monsoon rain slants in from the west.')&badge=$B"
T o_sg1 2.5 "scene=ov&hi=1&chip=Twist&label=$(e ' Singapore')&cap=$(e 'The high-rise next door looks right down.')&badge=$B"
T o_vr 7 "scene=ov&chip=VR&label=$(e ' seated, hands only')&cap=$(e 'In the headset: point and pinch. No walking needed.')&badge=$(e 'Meta IWER emulator · not a headset recording')"
