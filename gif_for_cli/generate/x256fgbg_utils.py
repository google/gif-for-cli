from x256 import x256
import heapq

# The max possible distance (i.e. between #000 and #fff)
_MAX_DISTANCE = 256 ** 2 * 3


def _get_closest_color(color,amount=1):
    possible_colors = enumerate(x256.colors)
    def mapper(item): return {"distance":x256.__distance(item[1], color),"index":item[0]}
    colors_and_distances = map(mapper,possible_colors)
    return heapq.nsmallest(amount,colors_and_distances,key=lambda item:item["distance"])


def top_2_colors(r, g, b):
    return tuple(_get_closest_color([r, g, b],amount=2))
