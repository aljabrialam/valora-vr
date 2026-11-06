#!/usr/bin/env bash
# Emulator end-to-end: a simulated right hand pinches the screen handle and swings it
# from -90° to 30°, which solves Level 1. Requires `npm run dev` (IWSDK dev server with
# its managed browser). Prints the design changes the app logged.
set -euo pipefail
cd "$(dirname "$0")/.."
npx iwsdk browser reload >/dev/null
sleep 6
npx iwsdk xr enter >/dev/null
npx iwsdk xr set-input-mode --input-json '{"mode":"hand"}' >/dev/null
npx iwsdk xr run-sequence --input-json "$(cat scripts/e2e-hand-swing.json)" >/dev/null
npx iwsdk browser logs | grep -o 'design[^}]*}[^,]*,[^,]*' | tail -6
