# eMolPat Portal UI Polish Design

## Goal

Make the portal header and status area quieter, use the correct HemaFrag identity, and give ownership information a dedicated, discoverable page.

## Programs page

- Use HemaFrag's canonical `assets/app_icon.png` artwork in its application card. This is the blue rounded-square application icon, not the soft full-canvas transparent variant currently bundled by eMolPat.
- Replace the sidebar label `Suite 1.0.0` with `Versjon 1.0.0`. Internal release and installation models may continue to use the technical term *suite*; this change removes it only from the visible portal identity.
- Remove the wide ready banner from the page flow.
- Show health as a compact box aligned to the upper-right of the page heading. The ready state reads `✓ Klar til bruk` in green. Non-ready states use the same location, concise state text, and the existing warning semantics and accessible label.
- Keep installation progress separate and full-width because it represents an active operation rather than passive health.

## About navigation and page

- Remove `Kun teknisk status / Ingen pasientdata lagres` from the lower-left sidebar.
- Add an `Om eMolPat` navigation tab at the bottom of the sidebar, visually separated from the operational navigation items but using the same keyboard and checked-state behavior.
- The tab opens a real page in the existing stacked navigation container.
- Page copy:

  > eMolPat er en samlet portal for molekylærpatologiske analyseverktøy. Portalen gir enkel tilgang til HemaFrag Diagnostics, IGH Merge, VPM / HTS Tolkning og MPN Tolkning, samtidig som hvert program fortsetter å kjøre som et selvstendig verktøy.
  >
  > **Utviklet av Christian Bjørnstad**

## Accessibility and behavior

- `Om eMolPat` remains a normal keyboard-focusable navigation button with an accessible name and description.
- The compact health box includes visible text and a symbol, so state is not conveyed by color alone.
- Application launch behavior remains unchanged: choosing an application closes eMolPat before starting the standalone tool.

## Validation

- Add UI tests for the visible version label, the About tab/page and creator credit, compact ready-state copy, and absence of the removed privacy text.
- Preserve existing tests for four applications, accessible navigation, health-state behavior, and portal-close launch handoff.
- Capture and inspect an updated portal screenshot for the README.
- Run the full pytest suite, Ruff, package build/resource verification, and GitHub Windows CI before merging to `master`.
