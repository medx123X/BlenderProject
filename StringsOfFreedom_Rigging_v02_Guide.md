# Strings of Freedom — Rig v02

## Source and preservation

Built from the live `StringsOfFreedom_Rigging_v01.blend`. `Character_v11.blend` was inspected in a separate background Blender process: its 477-object active character has object parenting, no armature, no constraints, and no string hooks. Rigging v01 already contains the rigid 23-bone character and two 17-bone controller-hand rigs, so it is the more complete source.

The original files are not overwritten. A separate pre-edit backup was saved as `StringsOfFreedom_before_rig_v02_20261018_163417.blend`.

Character meshes, materials, proportions, hat placement, stage, seats, lights, and controller-hand assets are preserved. Hidden archives remain hidden. The starting pose includes the original slight head tilt and right-elbow adjustment; those are preserved rather than replaced with a different rest appearance.

## Existing rig

Rigid bone parenting already moves the wooden pieces without skin deformation. Root > Pelvis > Torso > Neck > Head controls the body. Arms branch through Shoulder > UpperArm > Elbow > Wrist; legs branch through Hip > UpperLeg > Knee > Ankle > Foot. The limb bone heads align with their joint locations. Some decorative objects use the character origin instead of a joint origin; their bone parenting provides the correct pivot, so their origins were deliberately left intact.

The main head pivot carries the face, hair, and beret together. String anchor objects already follow the appropriate head, torso, wrist, and knee bones. The string curves previously had only a fingertip hook at the upper end, leaving the lower ends behind when the boy moved.

## Added or corrected

- A lower-end hook for each of the six strings, bound to its existing puppet attachment. The right-wrist endpoint is aligned to the actual current wrist attachment.
- `CTRL_Suspension` inserted between Root and Pelvis, with a pivot at the neck/head support height. Translate it to lift/drop the body; rotate it for suspended sway.
- Independent hand and foot IK targets and pole controls: nine new bones total, 32 bones in the character rig.
- Optional two-bone IK with stretching disabled and orientation controls for wrists and feet. Pole angles are calibrated to the original bend planes.
- Optional translation-only fingertip-follow constraints for the suspension and each hand target. These preserve the starting transform when enabled.
- Colored control shapes and bone collections. Joint translation and scale channels are locked where appropriate to discourage accidental separation or stretching.
- A strings visibility switch. This controls display only, not a simulated break.

## Controls to animate

Select `RIG_HERO` and enter Pose Mode. Rig switches are in the armature object's Custom Properties, not on individual pose bones.

| Control | Purpose |
|---|---|
| `Root` | Overall character placement and travel |
| `CTRL_Suspension` | Lift, drop, and whole-body hanging sway |
| `Pelvis`, `Torso`, `Neck`, `Head` | Weight shift, torso tilt, and head acting |
| `Shoulder.L/R`, `UpperArm.L/R`, `Elbow.L/R`, `Wrist.L/R` | Direct arm and hand rotations |
| `Hip.L/R`, `UpperLeg.L/R`, `Knee.L/R`, `Ankle.L/R`, `Foot.L/R` | Direct leg and foot rotations |
| `CTRL_Foot.L_IK`, `CTRL_Foot.R_IK` | Position and orient each foot for steps or planted contact |
| `CTRL_Hand.L_IK`, `CTRL_Hand.R_IK` | Position and orient each hand for pulls or reaching |
| Corresponding `*_Pole` bones | Guide elbow/knee bend direction |

All four `Foot_IK_L/R` and `Hand_IK_L/R` switches default to **0** (direct FK). Set a limb's switch to **1** to use its IK target. Controls start aligned with the saved pose. For later transitions, match targets to the current limb pose before changing modes; there is no automatic IK/FK snapping operator. IK targets are independent of Root inside the armature, allowing feet to stay planted while Root/Pelvis move. Move the Root bone rather than the armature object for character travel.

`Suspension_String_Follow` defaults to 0; at 1 the suspension follows translation of the existing left-index fingertip target. `Hand_String_Follow_L/R` similarly follow the left-pinky/right-index targets. Enable the respective Hand IK switch as well to pull the actual wrist. The existing hand rigs and fingertip targets remain the upper string controls. These links transfer displacement; they do not enforce fixed rope length or calculate gravity.

For independent movement, leave the three string-follow values at 0. Use foot IK and body/FK controls as needed. `Strings_Visible` can hide all strings, but cinematic broken-string remnants require a later effect. Turning off follow during a posed shot requires matching the resulting independent pose to prevent a jump.

## Validation

- Tested 15 head, torso, pelvis, bilateral arm/hand, and leg/foot joint rotations without keyframes.
- Tested a crouch with one raised, advanced foot and both lifted hands. IK endpoint error was below 0.00007 Blender units in the tested positions.
- Tested all three fingertip-follow links with a 0.12-unit upward pull. Baseline switching was stable within floating-point tolerance.
- Checked all six evaluated string meshes against the moving lower anchors: the nearest surface distance was their 0.0032-unit string radius.
- Inspected temporary pose and restored starting pose from front, side, and three-quarter views.
- Restored starting body transforms within 0.000001 Blender units/matrix components. Geometry and material identities remained unchanged. No animation actions or keys were created.
- Detailed numerical results are embedded as `RIG_V02_VALIDATION.json`.

## Scope and limitations

Ready for a first 10-second blocking/acting test. This is an animator-driven rigid marionette rig, not rope or ragdoll simulation. Fingers remain rigid with each puppet hand; facial expression controls, automatic foot roll, automatic contact/collision handling, hard mechanical joint-angle limits, and a string-breaking effect are not included. Extreme poses still require manual collision and costume-gap checks. Keep IK targets within limb reach; use poles to guide bends, and avoid dragging a target exactly through its shoulder or hip.

No film animation has been created.
