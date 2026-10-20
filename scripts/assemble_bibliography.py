"""Combine locally verified BibTeX fragments, rejecting duplicate keys/DOIs."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
entries, keys, dois = [], set(), set()
for path in sorted((ROOT / "assets").glob("refs-*.bib")):
    chunks = re.split(r"(?=^@\w+\s*\{)", path.read_text(), flags=re.M)
    for entry in chunks:
        if not entry.lstrip().startswith("@"):
            continue
        entry = entry.strip()
        key = re.search(r"@\w+\s*\{\s*([^,]+)", entry).group(1)
        assert key not in keys, f"duplicate citation key: {key}"
        keys.add(key)
        match = re.search(r"doi\s*=\s*\{([^}]+)\}", entry, re.I)
        if match:
            doi = match.group(1).lower()
            assert doi not in dois, f"duplicate DOI: {doi}"
            dois.add(doi)
        entries.append(entry)
destination = ROOT / "assets/bibliography.bib"
destination.write_text("% Verified bibliography assembled from refs-*.bib fragments.\n\n"
                       + "\n\n".join(entries) + "\n")
print(f"Assembled {len(entries)} verified bibliography entries.")
