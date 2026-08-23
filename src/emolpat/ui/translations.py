"""Norsk portaltekst holdt adskilt fra presentasjonskoden."""

from emolpat.domain import ModuleUnit

UNIT_NAVIGATION = (
    (ModuleUnit.HEMATO, "Hemato", "Åpne hematologiske analyseverktøy"),
    (ModuleUnit.SOLIDE, "Solide", "Verktøy for solide svulster"),
    (ModuleUnit.STAT, "STAT", "Statistikkverktøy"),
)

STATE_TEXT = {
    "ready": ("Klar til bruk", "Alle fire programmer er verifisert."),
    "not_installed": (
        "Programmer må installeres",
        "Installer hele eMolPat-pakken før programmene åpnes.",
    ),
    "update_available": (
        "Oppdatering tilgjengelig",
        "En nyere godkjent eMolPat-pakke er tilgjengelig.",
    ),
    "repair_required": (
        "Reparasjon kreves",
        "Ett eller flere programmer må repareres før de kan åpnes.",
    ),
    "unavailable": (
        "System utilgjengelig",
        "Kontroller Python FELLES og tilgang til den godkjente pakken.",
    ),
}

INSTALL_STAGE_TEXT = {
    "preflight": "Kontrollerer godkjent eMolPat-pakke",
    "dependencies": "Installerer godkjente avhengigheter",
    "components": "Installerer portal og analyseprogrammer",
    "verification": "Kontrollerer hele installasjonen",
    "record": "Fullfører eMolPat-installasjonen",
    "rollback": "Gjenoppretter forrige godkjente versjon",
}

INSTALL_COMPLETE_TEXT = "Oppdateringen er fullført. Start eMolPat på nytt."
