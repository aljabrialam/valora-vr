# Setup

## Requirements
- Node.js 20.19 or newer (22.12+ recommended)
- A desktop Chromium browser for the emulator; a Meta Quest 3 or 3S for headset testing

## Install and run
```bash
npm install
npm run dev
```
`npm run dev` starts the IWSDK dev server (`iwsdk dev`) at `https://localhost:8081` with the IWER emulator injected. Select **Enter XR**, then in the IWER toolbar choose **Select input mode → Gaze + Hands** ([controls](docs/CONTROLS.md)).

Plain Vite without the managed browser: `npm run dev:runtime`.

Open a specific level: `https://localhost:8081/?level=2`.

## Checks
```bash
npm run typecheck   # TypeScript
npm run prove       # every level solvable, none starts solved
npm run e2e:hand    # simulated hand solves Level 1 (needs npm run dev running)
```

## On a Quest
WebXR needs HTTPS. Either open the deployed URL, or forward the dev server over USB (`adb reverse tcp:8081 tcp:8081`) and open `https://localhost:8081` in Quest Browser, accept the certificate and select Enter VR. See the [IWSDK testing guide](https://developers.meta.com/vr/documentation/iwsdk/guides/02-testing-experience/).

## Build and deploy
```bash
npm run build       # static site in dist/
```
Deploy `dist/` to Vercel (or any static host). The page needs no server code.
