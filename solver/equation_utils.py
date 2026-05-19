def missing_parameters(metadata, state):

    missing = []

    for param in metadata["inputs"]:

        if not state.has(param):
            missing.append(param)

    return missing