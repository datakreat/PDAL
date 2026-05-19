from validation.rf_limits import RF_LIMITS


def validate_transmit_power(power):

    limits = RF_LIMITS["Pt"]

    if power > limits["hard_max"]:

        return {
            "feasible": False,
            "severity": "hard",
            "reason": "Required transmit power exceeds physical radar limits"
        }

    if power > limits["soft_max"]:

        return {
            "feasible": False,
            "severity": "soft",
            "reason": "Required transmit power exceeds practical engineering limits"
        }

    return {
        "feasible": True
    }