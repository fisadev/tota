from random import shuffle, random, choice, randint


def to_position(something):
    """Converts something (thing/position) to a position tuple."""
    if isinstance(something, tuple):
        return something
    else:
        return something.position


def distance(a, b):
    """Calculates distance between two positions or things."""
    x1, y1 = to_position(a)
    x2, y2 = to_position(b)

    return abs(x1 - x2) + abs(y1 - y2)


def distance_tie_breaker(a, b):
    x1, y1 = to_position(a)
    x2, y2 = to_position(b)
    return max([abs(x1 - x2), abs(y1 - y2)])


def sort_by_distance(something, others):
    def by_distance(other):
        return (distance(something, other),
                distance_tie_breaker(something, other),
                random())

    sorted_others = list(sorted(others, key=by_distance))
    if len(sorted_others) > 1 and (distance(something, sorted_others[0])
                                   == distance(something, sorted_others[1])):
        x1, y1 = to_position(sorted_others[0])
        x2, y2 = to_position(something)
        delta_x = abs(x1 - x2)
        delta_y = abs(y1 - y2)
        max_value = max([delta_x, delta_y])
        min_value = min([delta_x, delta_y])
        cut_point = min_value / (max_value + min_value)

        if random() < cut_point:
            sorted_others[0], sorted_others[1] = (sorted_others[1],
                                                  sorted_others[0])

    return sorted_others


def closest(something, others):
    """Returns the closest other to something (things/positions)."""
    if others:
        return sort_by_distance(something, others)[0]


def adjacent_positions(something):
    """Calculates the 4 adjacent positions of something (thing/position)."""
    position = to_position(something)
    deltas = ((0, 1),
              (0, -1),
              (1, 0),
              (-1, 0))

    return [(position[0] + delta[0],
             position[1] + delta[1])
            for delta in deltas]


def possible_moves(something, things):
    """Calculates the possible moves for a thing."""
    positions = [position for position in adjacent_positions(something)
                 if things.get(position) is None]

    return positions


def inside_map(something, size):
    """Check if a position or a thing is inside the map."""
    position = to_position(something)
    return 0 <= position[0] < size[0] and 0 <= position[1] < size[1]


def closes_empty_position(something, world):
    """Get the closest empty position to another thing or position."""
    position = to_position(something)
    fringe = [position]
    seen = set()

    while fringe:
        position = fringe.pop(0)
        seen.add(position)
        if position not in world.things:
            return position
        else:
            adjacents = adjacent_positions(position)
            shuffle(adjacents)
            for adjacent in adjacents:
                if adjacent not in seen and inside_map(adjacent, world.size):
                    fringe.append(adjacent)

    return None


def circle_positions(center, radius):
    """Get the positions of a circle."""
    x_center, y_center = center
    return [(x, y)
            for x in range(x_center - radius, x_center + radius + 1)
            for y in range(y_center - radius, y_center + radius + 1)
            if distance((x, y), center) <= radius]
