"""English portal text kept separate from presentation code."""

NAVIGATION = (
    ("Programs", "Open installed analysis applications"),
    ("System Status", "Check installation and components"),
    ("Update", "Manage the entire eMolPat package"),
    ("Help & Support", "Find guidance and technical information"),
)

STATE_TEXT = {
    "ready": ("Ready", "All four applications have been verified."),
    "not_installed": (
        "Applications must be installed",
        "Install the complete eMolPat package before opening the applications.",
    ),
    "update_available": (
        "Update available",
        "A newer approved eMolPat package is available.",
    ),
    "repair_required": (
        "Repair required",
        "One or more applications must be repaired before they can be opened.",
    ),
    "unavailable": (
        "System unavailable",
        "Check Python FELLES and access to the approved package.",
    ),
}

INSTALL_STAGE_TEXT = {
    "preflight": "Checking approved eMolPat package",
    "dependencies": "Installing verified dependencies",
    "components": "Installing portal and analysis applications",
    "verification": "Verifying the entire installation",
    "record": "Completing eMolPat installation",
    "rollback": "Restoring previous approved version",
}

INSTALL_COMPLETE_TEXT = "The update is complete. Restart eMolPat."