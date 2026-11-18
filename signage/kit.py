"""The run (the Grid kit's .fk-run): a page's summary as figure tiles with the
light trail stepping over and under them. A copy of the Grid's
`lifecycle/kit.py` path maths, so Glow's runs match every other app's.
"""
import zlib

# Each path runs over or under the tiles (never through the figures) and steps
# between the two lanes only in the gap between two tiles.
TOP, LOW = 8, 112
RADIUS = 14
RUNS = ['bridge', 'rise', 'wave', 'hook', 'dip', 'fall', 'tail']

# Each Glow page with a run keeps its own path, so no two look alike.
PAGE_RUNS = {
    '/devices/': 'wave',
    '/playlists/': 'dip',
    '/designs/': 'hook',
    '/media-library/': 'rise',
    '/templates/': 'fall',
}


def _lanes(name, n):
    half = n // 2
    return {
        'hook': [LOW] + [TOP] * (n - 1),
        'tail': [TOP] * (n - 1) + [LOW],
        'bridge': [LOW] + [TOP] * (n - 2) + [LOW] if n > 2 else [LOW, TOP][:n],
        'dip': [TOP] + [LOW] * (n - 2) + [TOP] if n > 2 else [TOP, LOW][:n],
        'rise': [LOW] * half + [TOP] * (n - half),
        'fall': [TOP] * half + [LOW] * (n - half),
        'wave': [LOW if i % 2 == 0 else TOP for i in range(n)],
    }[name]


def run_path(n, name):
    """The SVG path (viewBox 0 0 1000 140) for n tiles in a row."""
    n = max(1, int(n))
    lanes = _lanes(name, n)
    r = RADIUS
    parts = [f"M-40 {lanes[0]}"]
    for i in range(n - 1):
        a, b = lanes[i], lanes[i + 1]
        if a == b:
            continue
        x = round(1000 * (i + 1) / n)
        down = 1 if b > a else -1
        parts.append(f"H{x - r} q{r} 0 {r} {down * r} V{b - down * r} q0 {down * r} {r} {down * r}")
    parts.append("H1040")
    return ' '.join(parts)


def run_for(path, name=None):
    """Pick a run by name, by the page's entry in PAGE_RUNS, or by its address."""
    if name in RUNS:
        return name
    path = str(path)
    if path == '/':
        return 'bridge'
    for prefix, run in sorted(PAGE_RUNS.items(), key=lambda kv: -len(kv[0])):
        if path.startswith(prefix):
            return run
    return RUNS[zlib.crc32(path.encode()) % len(RUNS)]
