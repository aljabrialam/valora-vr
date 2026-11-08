#!/bin/bash
# Title cards and captions for the VR demo cut (CUT=demo in edit.py; durations match it).
cd "$(dirname "$0")/../.."
T() { node scripts/video/titles.mjs "video/titles/$1" "$2" "$3" > /dev/null; echo "$1"; }
e() { python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$1"; }
B=$(e "Headset view · Meta IWER emulator")
O() { T "$1" "$2" "scene=ov&chip=$(e "$3")&label=$(e " $4")&cap=$(e "$5")&badge=$B"; }
T vr 2.6 "scene=vr"
T proof 3.4 "scene=proof"
O d_tiki 4.3 VR Manila "Point at Tiki and pinch to start."
O d_place 5.9 VR Manila "Pinch a screen on the raft, point it at the courtyard, let go."
O d_private 1.8 VR Manila "The neighbour's line of sight stops at the screen."
O d_turn 3.75 VR Manila "A short pinch turns a placed piece."
O d_look 7.4 VR Bangkok "Look around: the neighbour, the boats on the canal, the sun."
O d_sun 10.1 VR Manila "Pinch the sun and drag it. Each capital follows its own sun path."
O d_day 11 VR Manila "Press play: live the day, every watcher checked hour by hour."
O d_th 7.9 VR Bangkok "A hedge hides the garden table from the long-tail boats."
O d_th2 14.6 VR Bangkok "Lunch by the Water: two screens, turned until lunch is shaded and unseen."
O d_id 7.9 VR Jakarta "A pergola keeps the table dry in the monsoon rain."
O d_sg 7.9 VR Singapore "A tree's canopy hides the pool from the high-rise."
