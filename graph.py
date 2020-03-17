# raygor
raygor_of_keys = dict()
raygor_of_keys_to_ignore = dict()

from_y = 27
for y in range(3, 6):
    for x in range(6, from_y):
        raygor_of_keys_to_ignore[f"{y}:{x}"] = 0
    from_y = from_y - 8

to_y = 44
for y in range(7, 29):
    to_y = to_y - 1
    for x in reversed(range(to_y, 45)):
        raygor_of_keys_to_ignore[f"{y}:{x}"] = 0

raygor_number = 3
for y in range(3, 29):
    if y % 2 == 0:
        raygor_number = raygor_number + 1
    for x in range(6, 45):
        the_key = f"{y}:{x}"
        if raygor_of_keys_to_ignore.get(the_key) == 0:
            continue
        raygor_of_keys[the_key] = raygor_number


def get_value_from_raygor_graph(y_value, x_value):
    return raygor_of_keys.get(f"{y_value}:{x_value}", 0) * 2


# fry
fry_of_keys = dict()
fry_of_keys_to_ignore = dict()

from_y = 128
for y in range(2, 5):
    for x in range(108, from_y):
        fry_of_keys_to_ignore[f"{y}:{x}"] = 0
    from_y = from_y - 8

to_y = 172
for y in range(7, 26):
    to_y = to_y - 2
    for x in reversed(range(to_y, 173)):
        fry_of_keys_to_ignore[f"{y}:{x}"] = 0

fry_number = 1
for y in reversed(range(2, 26)):
    if y % 2 == 0:
        fry_number = fry_number + 1
    for x in range(108, 173):
        the_key = f"{y}:{x}"
        if fry_of_keys_to_ignore.get(the_key) == 0:
            continue
        fry_of_keys[the_key] = fry_number


def get_value_from_fry_graph(y_value, x_value):
    return fry_of_keys.get(f"{y_value}:{x_value}", 0)
