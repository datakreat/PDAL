def find_equation_for_target(target, registry):

    for eq in registry:

        if target in eq["outputs"]:
            return eq

    return None