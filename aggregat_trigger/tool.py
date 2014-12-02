def parse_kwarg(arg):
    """Parse a string and build the corresponding SQL filter
    """
    ops = {'=': '=',
           'gt': '>',
           'gte': '>=',
           'lt': '<',
           'lte': '<='}
    
    cols = arg.split('__')
    if len(cols) == 1:
        sqw = "%s=" % (cols[0])
    if len(cols) == 2:
        sqw = "%s %s" % (cols[0], ops[cols[1]])
    return (cols[0], sqw)
