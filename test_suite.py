import sys
import io
import engine

def run_test_case(name, query):
    print(f"\n==========================================")
    print(f"RUNNING TEST: {name}")
    print(f"Query: {query}")
    print(f"==========================================")
    
    # Backup stdout and stdin
    old_stdin = sys.stdin
    old_stdout = sys.stdout
    
    # Mock stdin and capture stdout
    sys.stdin = io.StringIO(query + "\n")
    sys.stdout = io.StringIO()
    
    try:
        engine.main()
        output = sys.stdout.getvalue()
    except Exception as e:
        output = f"EXCEPTION OCCURRED: {e}"
    finally:
        # Restore stdin and stdout
        sys.stdin = old_stdin
        sys.stdout = old_stdout
        
    print(output)
    return output

def main():
    # Test Case 1: Consistent kinematics SUVAT query
    run_test_case(
        "Kinematics Consistent Check",
        "Verify if a car traveling at 10 m/s after accelerating at 2 m/s^2 for 5 s from rest is physically possible."
    )
    
    # Test Case 2: Inconsistent kinematics SUVAT query
    run_test_case(
        "Kinematics Inconsistent Check",
        "Verify if a car traveling at 15 m/s after accelerating at 2 m/s^2 for 5 s from rest is physically possible."
    )

    # Test Case 3: Battery pack query matching user input
    run_test_case(
        "LFP Battery Pack Design Grounding",
        "LFP Battery Pack Thermal and Electrochemical Management System Designed for 3 C Fast-Charging at 150 A, 240 V with 60°C Temperature Limit and Active Cooling Capable of Dissipating 10 kW Heat under 5 mm Cooling Thickness Constraint"
    )

    # Test Case 4: Circuits Ohm's Law and Power check
    run_test_case(
        "Circuits Verification",
        "Check if a circuit with Voltage 12V, Resistance 6 ohms, Current 2A, and Power 24W is physically consistent."
    )

    # Test Case 5: Thermodynamics Ideal Gas Law check
    run_test_case(
        "Thermodynamics Ideal Gas Law",
        "Check if 1.0 mole of an ideal gas at 101325 Pa pressure, occupying a volume of 0.022414 m^3, at temperature 273.15 K is physically consistent."
    )

    # Test Case 6: Aerospace rocket equation delta-v calculation
    run_test_case(
        "Aerospace Rocket Equation Delta-V",
        "Compute the delta-v of a rocket stage with an initial mass of 10000 kg, an empty mass of 2000 kg, and a specific impulse of 300 seconds."
    )

    # Test Case 7: Lidar Time-of-Flight Range calculation
    run_test_case(
        "Lidar Range from Time-of-Flight",
        "Compute the range R to a target if a lidar pulse returns with a round-trip time of flight of 2.0e-5 seconds."
    )

    # Test Case 8: Battery Specific Energy
    run_test_case(
        "Battery Specific Energy",
        "Calculate specific energy of a battery cell operating at nominal voltage 3.7 V with a specific capacity of 200 Ah/kg."
    )

    # Test Case 9: Battery Nernst Potential
    run_test_case(
        "Battery Nernst Potential",
        "Compute the cell potential E_cell of a battery reaction at 298.15 K, if the standard potential is 3.0 V, reaction quotient is 1.0, and 1.0 electron is transferred."
    )

    # Test Case 10: Radar Range Equation
    run_test_case(
        "Radar Range Equation",
        "Determine received power Pr for a radar system with transmit power 10 W, transmit gain 10, receive gain 10, operating wavelength 0.01 m, target range 100 m, and radar cross section 1.0 m^2."
    )

    # Test Case 11: Hooke's Law Spring Force
    run_test_case(
        "Hooke's Law Spring Force",
        "Calculate spring force F_spring for a spring with spring constant 500 N/m stretched by 0.1 m."
    )

    # Test Case 12: Capacitor Charge
    run_test_case(
        "Capacitor Charge & Capacitance",
        "Find capacitance C_cap of a capacitor that holds a charge of 1.2e-5 C when a voltage of 12 V is applied."
    )

    # Test Case 13: Ideal Gas Density
    run_test_case(
        "Ideal Gas Density",
        "Determine gas density rho_gas at pressure 101325 Pa and temperature 273.15 K, if the gas molar mass is 0.02897 kg/mol."
    )


if __name__ == "__main__":
    main()
