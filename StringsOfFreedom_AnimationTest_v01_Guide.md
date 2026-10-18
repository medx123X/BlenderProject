# The Awakening — animation test v01

10 seconds, 24 FPS, frames 1–240. Built on Rigging v02; the original rig file is unchanged. Three animation actions are embedded in the new project. Scene markers identify the five story beats.

## Timing

| Frames | Performance |
|---|---|
| 1–48 | Suspended silence: slight downward head, very small pendulum sway, feet hovering above the stage |
| 49–96 | Hesitant head lift, a brief pause, then a delayed torso response |
| 97–144 | Right index curls and the puppeteer hand lifts; the wrist string leads the arm upward; shoulder and torso react later |
| 145–192 | Small downward efforts oppose the pull, with deliberately placed irregular tension changes |
| 193–240 | Pull releases, wrist dips slightly past its resting level and settles; head turns toward the right wrist string |

## Exact keyed controls

All listed channels have keys spanning frames 1–240. The first and last values hold the intended starting/ending state; movement occurs within the beats above.

`RIG_HERO` — action `AWAKENING | Puppet | 001-240`:

- `CTRL_Suspension`: location and quaternion rotation. Constant 0.075-unit suspension lift; slow sway stays under 0.4 degrees per axis.
- `Head`: quaternion rotation. Awareness lift and final 22-degree relative turn toward the right string.
- `Torso`: quaternion rotation. Delayed tilt and small resistance responses.
- `Shoulder.R`: quaternion rotation. Reaction begins after frame 104; no competing right upper-arm/elbow FK keys.
- `CTRL_Hand.R_IK`: location and quaternion rotation. Constant hanging offset plus small resistance corrections; the existing fingertip-follow constraint supplies the main pull displacement.
- `UpperLeg.L`, `UpperLeg.R`: quaternion rotation. Very small delayed hanging motion, below 0.2 degrees.
- Eight mode properties keyed CONSTANT at frames 1 and 240: right Hand IK=1, right Hand String Follow=1; both Foot IK, left Hand IK, left Hand String Follow, and Suspension String Follow=0; Strings Visible=true. No mode switches occur mid-shot.

`RIG_Controller_R` — action `AWAKENING | Puppeteer right pull | 001-240`:

- `Wrist.R`: location. Small hand lift and backward adjustment.
- `Index_Base.R`, `Index_Middle.R`, `Index_Tip.R`: quaternion rotation. The base reaches about 17 degrees of additional flexion. Forced motion starts at frame 100, peaks during resistance, and releases after frame 192.

`RIG_Controller_L` — action `AWAKENING | Left index support yield | 001-240`:

- `Index_Base.L`: quaternion rotation. A quiet support adjustment of approximately 0 to -5.65 degrees, allowing the head to rise while keeping its string length visually consistent.

Transform curves use Bezier interpolation with auto-clamped handles. No random-noise modifiers, geometry deformation keys, or scale keys were added. Existing controller-hand skinning is preserved.

## Framing and preservation

`CAM_Awakening_Test` is a new, static review camera including the boy, all strings, and the puppeteer hands. Existing cameras, stage, lights, materials, meshes, and hidden archives are retained. The camera is for reviewing the cause and response together, not a final edited film shot.

## Validation

All 240 frames were numerically checked, with visual checks at 1, 48, 96, 120, 144, 168, 192, 216, and 240. Additional three-quarter and hand views were inspected.

- Maximum right wrist IK target error: about 0.000103 Blender units.
- Maximum tested limb joint separation: less than 0.000001 units.
- Both ends of each evaluated string reach their anchors within the 0.0032-unit tube radius.
- Maximum wrist displacement between consecutive frames: about 0.0162 units; no large position jump was found.
- Minimum shoe-sole height is 2.0963, above the stage surface at 2.0119.
- String-length deviations from the opening pose: head 0.33%, left wrist 0.36%, right wrist 0.52%, left knee 0.14%, right knee 1.79%, back support 1.27%.
- A small settling overshoot was adjusted after the scan detected an unreachable wrist target. The corrected motion stays inside the arm's reach.

Detailed metrics are embedded as `AWAKENING_VALIDATION.json`.

## Limits

Strings are animated straight curves with attachment tracking, not fixed-length rope physics. Small remaining length changes are accepted for this acting test. Visual inspection found no obvious new clipping in the sampled poses; there is no automatic collision system. Facial features are unchanged and the emotional beat relies on head/body posing. The lightweight preview uses Material Preview viewport lighting, so it is not a final cinematic lighting render.
