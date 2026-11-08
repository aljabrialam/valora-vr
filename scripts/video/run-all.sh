#!/bin/bash
# Renders every shot in order; each in its own browser so one failure can be redone alone.
cd "$(dirname "$0")/../.."
for s in ${SHOTS:-t_ph t_th t_id t_sg t_watch w_globe w_tiki w_place w_sun w_day w_ph3 w_th1 w_id1 w_sg1 w_vr}; do
  timeout 1500 node scripts/video/shots.mjs $s > video/log-$s.txt 2>&1 || echo "FAIL $s" >> video/log-fail.txt
  tail -1 video/log-$s.txt
done
