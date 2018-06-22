from x256 import x256


# The max possible distance (i.e. between #000 and #fff)
_MAX_DISTANCE = 256 ** 2 * 3


def top_2_colors(r, g, b):
    c = [r, g, b]
    best = {'distance': _MAX_DISTANCE, 'index': 1}
    second = {'distance': _MAX_DISTANCE, 'index': 1}

    for index, item in enumerate(x256.colors):
        d = x256.__distance(item, c)
        if(d <= best['distance']):
            if best:
                second = best
            best = {'distance': d, 'index': index}

    return best, second
