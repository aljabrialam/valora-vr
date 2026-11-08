#!/bin/bash
# Title cards and captions for the VR demo cut (CUT=demo in edit.py; durations match it).
cd "$(dirname "$0")/../.."
T() { node scripts/video/titles.mjs "video/titles/$1" "$2" "$3" > /dev/null; echo "$1"; }
e() { python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$1"; }
B=$(e "Headset view · Meta IWER emulator")
O() { T "$1" "$2" "scene=ov&chip=$(e "$3")&label=$(e " $4")&cap=$(e "$5")&badge=$B"; }
T vr 2.6 "scene=vr"
T proof 3.4 "scene=proof"
T entry 4.2 "scene=entry"
T goal 4.6 "scene=goal"
T profile 5.0 "scene=profile"
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
# 3-minute demo additions
T d_globe 9.4 "scene=ov&chip=Choose&label=$(e ' a place')&cap=$(e 'Pick a country on the globe, then Enter VR.')&badge=$(e 'Browser view · before entering VR')"
T d_ctrl 7.9 "scene=ov&chip=VR&label=$(e ' Hanoi')&cap=$(e 'Touch controllers work too: point, pull the trigger.')&badge=$(e 'Headset view · Meta IWER emulator · Touch controllers')"
O d_score1 6.5 Score Hanoi "Two watchers at once: the neighbour and the riders."
O d_score2 7.6 Score Hanoi "A screen for the neighbour, a hedge for the riders."
O d_score3 5.6 Score Hanoi "Every rule DONE. Two pieces, par two: three stars."
O d_score4 6.9 Score Hanoi "Press play to live the day, checked hour by hour."
O d_my 7.9 VR "Kuala Lumpur" "Condo towers look down: a tree's canopy hides the table."
