# Competition: Meta VR Start Developer Competition 2026

Sources: the official Devpost overview and the [official rules](https://start-developer-competition-26.devpost.com/rules), both read on 6 November 2026. **Re-check the rules and FAQ on Devpost before submitting.**

## Key facts

| | |
|---|---|
| Submission period | 24 Sept 2026, 10:00 a.m. PST to 18 Nov 2026, 12:00 p.m. PST (19 Nov, 4:00 a.m. Singapore) |
| Track | Gaming: "games designed for hands-first or eyes and hands. Puzzle, strategy, casual… genres that thrive seated, without controllers" |
| Hard requirements | Hands-first end to end; policy compliance |
| Design guidelines | Seated (two-foot radius); easy in and out, satisfying in 10 minutes or less; original, not a wrapper |
| IWSDK delivery | A hosted link (GitHub Pages, Vercel or similar). The build may not change after the deadline and must stay available through judging |
| Video | Under 3 minutes, public on YouTube or Vimeo, footage from a Meta VR device or an emulator |
| Judging | Four equally weighted criteria: innovation and creativity, experience design, technical implementation, polish and presentation (minimum 60 fps on Quest per the judging page) |

## From the official rules (verified 6 Nov 2026)

| Rule | What it means for us |
|---|---|
| Entrants must be 18+ and at the age of majority where they live | Confirm for every team member |
| Excluded: Brazil, Quebec, comprehensively sanctioned areas, and countries with banking or wire-transfer restrictions | Singapore is not named |
| The person submitting must be a Start member by submission time; everyone needs an active Meta account with Developer Access | Done for Aljabri |
| One entry per individual; a Team Representative cannot also submit solo | One entry only |
| Teams appoint one Representative, who receives communications and any prize | Decide who |
| IWSDK/WebXR entries submit a link judges can open; Devpost should link the GitHub page | Vercel URL + `github.com/aljabrialam/valora-vr` |
| The link must stay available, free and unchanged until the winner announcement (about 11 Dec) | Do not redeploy after the deadline |
| Tools must be publicly available or available to Start members; no unreleased Meta tools | IWSDK `1.1.0-rc.2` is what `npm create @iwsdk@latest` installs from public npm; re-check for a stable release before the freeze |
| Third-party and open-source code must respect its licences | See [CREDITS](../CREDITS.md) |
| Video under 3 minutes, from a Quest, XR Simulator or equivalent emulator; show real gameplay, don't rely on AI-generated video | Emulator capture of the real build, labelled |
| Judging: Stage One pass/fail viability; Stage Two four criteria at 25% each; at least 60 fps on Quest hardware, solid and bug-free | Measure on a borrowed Quest |

## From the full official rules text (read 6 Nov 2026): what changes for us

**Compliance risks to resolve**

| Rule | Risk for us | Action |
|---|---|---|
| "Projects may not mention or depict any identifiable person other than Entrants." | The VaLora name story names the designer's wife, who is not an entrant | Decide: add her to the team as an entrant, or keep the VaLora name and leave the story out of the game and the entry materials (README, video, description) |
| Entrants "may not be under any legal or contractual obligation that would prohibit their participation" | Employment agreements sometimes claim side-project IP | Check the employment contract's IP and outside-work clauses |
| No corporate logos, brand names or recognizable branded products | VaLora's own logo is ours; avoid real brands in the scene (cars, furniture) | Keep the model generic |
| Sponsor may re-assign Track and Division at its discretion | Lowers the risk of picking the wrong division | Still ask on the forum |

**What the judging criteria reward (beyond the overview)**

| Criterion wording | Our response |
|---|---|
| Innovation: "uniquely leverage Meta device capabilities (e.g. spatial depth, hands-first design, gaze…) to drive repeat usage" | Hands-first, spatial watcher views; promote the daily-sun challenge from stretch goal to core |
| Experience: "intuitive navigation, clear onboarding, and a habit-forming purpose" | Hand-in-the-sunbeam onboarding; daily sun gives the habit |
| Experience: "FoV-aware design… keep essential UI and interactions within a comfortable, narrower FoV" | Keep the level card, labels and handles inside the Meta VR Glasses view (about 37° left/right, 25° up, 43° down); test with the `metaVRGlasses` emulator profile |
| Technical: "gaze interactions… hand tracking… FoV-aware design"; min 60 fps; solid and bug-free | Ray pinch already works with gaze + pinch; add a glasses-profile test; measure fps on Quest |
| Passthrough "should be purposeful… not a scene that plays the same with passthrough off" | We do not use passthrough; nothing to lose |
| Polish: "Lead with the story and what makes your project distinct. Don't lean on AI-generated video" | Video opens on the seat view and the two-watchers idea; real emulator footage |

## Prizes we are aiming at

| Prize | Why |
|---|---|
| Best New Gaming Experience ($100k) / runner-up ($50k) | Main target |
| Best First Five Minutes ($25k) | Hand-in-the-sunbeam onboarding, first look through the neighbour's eyes |
| Boldest Original Concept ($25k) | Two watchers, one rule |
| Best Accessibility Forward Experience ($25k) | Seated, one-handed, symbols and words, look-and-pinch compatible |
| Best Reason to Come Back ($25k) | Only if the daily-sun stretch goal ships |

## Division and project history

The competition window began on **24 September 2026**. VaLora's history, from git:

| Date | What |
|---|---|
| 6 Nov 2026 | VaLora house concept and 3D website created (`aljabrialam/valora`, first commit 17:11 SGT) |
| 6 Nov 2026 | This VR game started (`valora-vr`), reusing VaLora's sun model and design |

Everything is inside the window, so we intend to enter **New Experience**. The VR game reuses the VaLora website's sun formula and house concept; because the rule says "no pre-existing codebases… repurposed", we will confirm with the organisers on the Devpost forum before choosing the division, and keep this table as evidence.

## Eligibility questions for the team (not decided here)

- [x] Start program membership: **accepted 6 Nov 2026** (welcome email from the Start Program Team; Meta developer organization "alamazing")
- [ ] Every member 18+ and at the age of majority; Singapore is not on the excluded list, but confirm the banking and wire-transfer clause does not apply
- [x] Active Meta developer account (organization "alamazing")
- [ ] Team member names, emails and roles for the form; choose the Team Representative
- [x] Registered for the competition on Devpost

No accounts were registered and no terms were accepted on the team's behalf.
