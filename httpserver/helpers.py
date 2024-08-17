from collections import OrderedDict


async def readuntil(reader, separator):
    buffer = b""
    while (char := await reader.read(1)):
        buffer += char
        if buffer.endswith(separator):
            break
    return buffer


def perc_decode(v, from_form=False):
    decoded = b""
    i = 0
    while i < len(v):
        if v[i] == "%":
            encoded = v[i+1:i+3]
            decoded += bytes.fromhex(encoded)
            i += 2
        elif from_form and v[i] == "+":
            decoded += b" "
        else:
            decoded += v[i].encode()
        i += 1
    return decoded


def process_query_string(query_string):
    query = OrderedDict()
    query_string = query_string.split("&")
    query_string = map(lambda v:v.split("="), query_string)
    for key, value in query_string:
        query[key] = perc_decode(value, True)
    return query


def seperate_path_and_query(path):
    path_split = path.split("?")
    query = None
    if len(path_split) > 1:
        path, query_string = path_split
        query = process_query_string(query_string)
    else:
        query = OrderedDict()
    return path, query
