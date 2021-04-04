
def parseParams(param_file):
    with open(param_file) as f:
        params = f.readlines()
    return params
