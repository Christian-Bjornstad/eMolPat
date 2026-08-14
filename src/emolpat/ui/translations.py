"""Norwegian portal text kept separate from presentation code."""

NAVIGATION = (
    ("Programmer", "Åpne installerte analyseprogrammer"),
    ("Systemstatus", "Kontroller installasjon og komponenter"),
    ("Oppdatering", "Administrer hele eMolPat-pakken"),
    ("Hjelp og støtte", "Finn veiledning og teknisk informasjon"),
)

STATE_TEXT = {
    "ready": ("Klar til bruk", "Alle fire programmer er kontrollert."),
    "not_installed": (
        "Programmer må installeres",
        "Installer den komplette eMolPat-pakken før programmene åpnes.",
    ),
    "update_available": (
        "Oppdatering tilgjengelig",
        "En nyere godkjent eMolPat-pakke er tilgjengelig.",
    ),
    "repair_required": (
        "Reparasjon kreves",
        "Et eller flere programmer må repareres før de kan åpnes.",
    ),
    "unavailable": (
        "Systemet er utilgjengelig",
        "Kontroller Python FELLES og tilgangen til den godkjente pakken.",
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
