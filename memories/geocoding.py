import json
from urllib.parse import quote
from urllib.request import Request, urlopen


def geocode_location(location):
    if not location:
        return None

    request = Request(
        'https://nominatim.openstreetmap.org/search?format=jsonv2&limit=1&q=' + quote(location),
        headers={'User-Agent': 'MemoryApp/1.0 (local development)'},
    )
    try:
        with urlopen(request, timeout=4) as response:
            results = json.loads(response.read().decode('utf-8'))
    except (OSError, ValueError):
        return None

    if not results:
        return None
    try:
        return float(results[0]['lat']), float(results[0]['lon'])
    except (KeyError, TypeError, ValueError):
        return None
