from __future__ import annotations

import re
from pathlib import Path


def test_readme_points_to_complete_release_not_source_zip() -> None:
    text = Path("README.md").read_text(encoding="utf-8")

    assert "https://github.com/Christian-Bjornstad/eMolPat/releases" in text
    assert "eMolPat-<version>-windows.zip" in text
    assert "Installer eMolPat.cmd" in text
    assert "pip --user" in text
    assert "Code > Download ZIP" in text
    assert "source code" in text.lower()


def test_readme_relative_links_resolve() -> None:
    readme = Path("README.md")
    text = readme.read_text(encoding="utf-8")
    targets = re.findall(r"\[[^]]+\]\(([^)]+)\)", text)
    targets += re.findall(r'<img[^>]+src="([^"]+)"', text)

    missing = []
    for raw in targets:
        target = raw.strip("<>").split("#", 1)[0]
        if not target or target.startswith(("http://", "https://", "#")):
            continue
        if not (readme.parent / target).is_file():
            missing.append(target)
    assert missing == []
