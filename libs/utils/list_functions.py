def partition(lst, step):
    try:
        return [lst[i:i+step] for i in xrange(0, len(lst), step)]
    except:
        return None


def partition_by(lst, obj_property):
    property_values = {}
    for item in lst:
        try:
            val = getattr(item, obj_property)
        except:
            continue
        recorded = property_values.get(val, None)
        if recorded:
            recorded.append(item)
        else:
            property_values[val] = [item]
    return property_values.values()
