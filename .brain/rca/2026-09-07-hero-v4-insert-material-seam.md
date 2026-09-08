# Hero v4 insert material seam

- Symptom: the mid-opening production render showed a rectangular boundary around the photographic insert plate.
- Evidence: the initial full-resolution A frame60 used an unfeathered image texture on a plane over procedural foam; the surrounding foam had a different color, roughness and normal response.
- Root cause: abrupt material transition at the reference plate edge, accentuated by a0.005-unit height offset above the supporting foam.
- Why detection was delayed: endpoint proofs at50% resolution made the boundary less visible; the full-resolution mid-opening image exposed it.
- Prevention: blend only the empty outer7.5% foam margin into the common foam material in local UV coordinates, match surface roughness/microtexture, and reduce height offset to0.0003. Preserve product pixels within the plate. Re-render visible-insert frames23–119; retain the previously verified fully occluded common prefix0–22. Inspect the final decoded mid-opening contact sheet before delivery.

This is a local material correction within the user-authorized video production scope. No application or customer data changes.
