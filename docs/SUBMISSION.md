# Submission form (draft)

**Submission name:** VaLora: Two Watchers

**Tagline (under 140 characters):** Two watchers look at your house: the sun and the neighbour. Let one in, keep the other out. A hands-only architecture puzzle.

**Track:** Gaming

**Division:** New Experience (to confirm with the organisers; see [COMPETITION](COMPETITION.md))

**Description (draft, under 500 words):**

*Inspiration.* VaLora is a courtyard house in Singapore, named for the designer's wife, Lora. Every tropical house fights the same two battles: letting light in and keeping eyes out. We noticed they are the same question, can this watcher see that spot?, and built a game around it.

*What it is.* A seated, hands-only puzzle. A small model of the house sits on the desk in front of you. Two watchers look at it: the Sun, which should reach the garden in the morning but not the reading chair in the afternoon, and the Neighbour, who must never see the chair. You pinch and swing a privacy screen, slide the roof overhang and drag the sun across the sky. Beams show each watcher's line of sight and stop on whatever blocks it. You can look through either watcher's eyes, and when a level is solved you sit in the chair at full size.

*How we built it.* Meta's Immersive Web SDK and WebXR in Quest Browser. One small geometry engine answers "can this watcher see that target?" for both watchers, and the same code proves every level solvable by checking every snap position. Grabs use ray pinch so the game works with hand tracking and with look-and-pinch. We tested with simulated hands in Meta's IWER emulator, plus a borrowed Quest.

*What's next.* A daily challenge with that day's real sun path, more houses, and a dusk level where the house becomes a lantern.

*Note:* illustrative sunlight and visibility checks, not certified daylight, comfort or privacy analysis.

**Hand interactions:** every action is a pinch on a large handle with 15° detents and a click; no controller is needed at any point.

**Target launch date:** to decide.

**Team:** names, emails and roles to fill in.
