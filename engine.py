from dotenv import load_dotenv

from extractor.llm_extractor import extract_parameters

from state import PhysicsState

from equations.registry import EQUATION_REGISTRY

from planner.equation_planner import (
    find_equation_for_target
)

from solver.equation_executor import (
    execute_equation
)

from validation.feasibility import (
    validate_transmit_power
)

from utils.rf_math import (
    linear_to_db
)

load_dotenv()

MIN_SNR_DB = 10


def main():

    # =====================================================
    # Initialize State
    # =====================================================

    state = PhysicsState()

    # =====================================================
    # User Query
    # =====================================================

    text = input("Enter Query: ")

    # =====================================================
    # LLM Extraction
    # =====================================================

    extracted = extract_parameters(text)

    print("\nExtracted Parameters:")
    print(extracted)

    # =====================================================
    # Store Explicit Parameters
    # =====================================================

    for k, v in extracted.items():
        state.add_explicit(k, v)

    # =====================================================
    # Default Parameters
    # =====================================================

    defaults = {
        "Gt": 3.16,
        "Gr": 3.16,
        "B": 1e6,
        "T": 290
    }

    for k, v in defaults.items():

        if not state.has(k):
            state.add_derived(k, v)

    # =====================================================
    # Wavelength
    # =====================================================

    if state.has("frequency"):

        frequency = state.get("frequency")

        wavelength = 3e8 / frequency

        state.add_derived("lam", wavelength)

    else:

        print("\nMissing frequency")

        return

    # =====================================================
    # Compute Noise Power
    # =====================================================

    noise_eq = find_equation_for_target(
        "N",
        EQUATION_REGISTRY
    )

    noise_power = execute_equation(
        noise_eq,
        "N",
        state
    )

    if noise_power is None:

        print("\nCould not compute noise power")

        return

    state.add_derived("N", noise_power)

    print("\nNoise Power:")
    print(noise_power, "W")

    # =====================================================
    # Required SNR
    # =====================================================

    required_snr_linear = 10 ** (MIN_SNR_DB / 10)

    state.add_derived(
        "required_SNR",
        required_snr_linear
    )

    # =====================================================
    # Required Received Power
    # =====================================================

    required_received_power = (
        state.get("required_SNR") *
        state.get("N")
    )

    state.add_derived(
        "required_Pr",
        required_received_power
    )

    print("\nRequired Received Power:")
    print(required_received_power, "W")

    # =====================================================
    # Required Transmit Power
    # =====================================================

    friis_eq = find_equation_for_target(
        "Pt",
        EQUATION_REGISTRY
    )

    if friis_eq is None:

        print("\nNo equation found for Pt")

        return

    # temporarily expose required_Pr as Pr
    state.add_derived(
        "Pr",
        state.get("required_Pr")
    )

    required_pt = execute_equation(
        friis_eq,
        "Pt",
        state
    )

    if required_pt is None:

        print("\nCould not compute transmit power")

        return

    state.add_derived(
        "required_Pt",
        required_pt
    )

    print("\nRequired Transmit Power:")
    print(required_pt, "W")

    # =====================================================
    # Feasibility Validation
    # =====================================================

    validation = validate_transmit_power(
        required_pt
    )

    print("\nValidation:")
    print(validation)

    # =====================================================
    # Actual SNR (if user provided Pt)
    # =====================================================

    if state.has("Pt"):

        pr_eq = find_equation_for_target(
            "Pr",
            EQUATION_REGISTRY
        )

        actual_received_power = execute_equation(
            pr_eq,
            "Pr",
            state
        )

        if actual_received_power is not None:

            state.add_derived(
                "actual_Pr",
                actual_received_power
            )

            print("\nActual Received Power:")
            print(actual_received_power, "W")

            # expose actual_Pr as Pr
            state.add_derived(
                "Pr",
                actual_received_power
            )

            snr_eq = find_equation_for_target(
                "SNR",
                EQUATION_REGISTRY
            )

            snr_linear = execute_equation(
                snr_eq,
                "SNR",
                state
            )

            if snr_linear is not None:

                snr_db = linear_to_db(
                    snr_linear
                )

                state.add_derived(
                    "SNR_dB",
                    snr_db
                )

                print("\nActual SNR:")
                print(snr_db, "dB")

                if snr_db >= MIN_SNR_DB:

                    print("\n✅ Radar Link Feasible")

                else:

                    print("\n❌ Radar Link NOT Feasible")

    # =====================================================
    # Final State
    # =====================================================

    print("\nFinal Physics State:")
    print("\nExplicit:")
    print(state.explicit)

    print("\nDerived:")
    print(state.derived)


if __name__ == "__main__":
    main()