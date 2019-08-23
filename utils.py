import sys

def list_str(list):
    return ", ".join([str(x) for x in list])

def reraise(e, extra):
    raise type(e)(extra.format(str(e))).with_traceback(sys.exc_info()[2])