# One searchable app catalog

Requested on 30 October 2026: put all apps on one page, add search, retain About,
and prepare the interface before the next application list is supplied.

## Scope and design

Replace unit navigation with **Apper** and **Om eMolPat**. Reuse the existing
Norwegian desktop theme, app cards, process manager and system-status dialog.
The catalog shows every module from the manifest in its declared order. Scrolling
keeps all apps on one page; cards use one, two or three columns as space allows.

Implementation choices: search filters immediately over app names and Norwegian
and English descriptions. Matching ignores case and surrounding/repeated
whitespace, and requires every entered word to match. The search field has a clear
button and Ctrl+F shortcut. A count describes the results. No matches shows a
message with a **Vis alle apper** action. Search persists when visiting About.

Reuse the same card objects while filtering and reflow matching results from the
first cell. Running/failure state, update/repair restrictions, and installation
locks must survive filtering. Clear or search from the bottom returns results to
the top of the scroll area.

## Alternatives considered

Keeping separate unit pages with global search would still divide the app list.
A searchable catalog satisfies the explicit one-page request and reuses the
existing cards. A plain list could be denser but would replace the established
visual presentation. The implementation keeps the cards.

## Boundaries

No new applications, component pins, package dependencies, release versions or
clinical workflows change. Unit metadata remains in the release contract; it no
longer determines which page displays an app. New application integration still
requires the existing source, entry-point, icon and release validation steps.
The published 1.3.0 assets are not replaced by this development change.

## Verification

`$env:QT_QPA_PLATFORM='offscreen'; py -3.12 -m pytest -q` covers the catalog,
filtering, clear/empty states, search while running/installing/unhealthy, About
navigation, launch events, Ctrl+F, counts from the manifest, and compact/wide
layouts. Check source with `py -3.12 -m ruff check src scripts tests packaging`.
Inspect rendered desktop, filtered, no-results, compact and About states using
real Qt widgets and the Windows Segoe UI font.
