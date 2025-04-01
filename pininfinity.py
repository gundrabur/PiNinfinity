import decimal
import time
import threading
import sys
import os
from datetime import datetime

# Decimal precision for start (continuously increasing)
BASE_PRECISION = 1000

def chudnovsky_algorithm(precision, update_callback, stop_event):
    """
    Calculates Pi using the Chudnovsky method.
    This method converges very quickly and is well suited for high precision.
    Calculates continuously until interrupted by the stop_event.
    """
    # Initialization of variables for the Chudnovsky algorithm
    decimal.getcontext().prec = precision
    C = 426880 * decimal.Decimal(10005).sqrt()
    M = decimal.Decimal(1)
    L = decimal.Decimal(13591409)
    X = decimal.Decimal(1)
    K = decimal.Decimal(6)
    S = L
    
    pi = C / S  # First rough approximation
    current_iteration = 0
    
    # Continuous calculation until the stop signal is given
    while not stop_event.is_set():
        current_iteration += 1
        
        # Algorithm steps
        M = M * (K**3 - 16 * K) // (current_iteration**3)
        L = L + 545140134
        X = X * -262537412640768000
        S = S + (M * L) / X
        K = K + 12
        
        # Calculate Pi
        pi = C / S
        
        # Increase precision every 10 iterations (slowly increasing)
        if current_iteration % 10 == 0:
            new_precision = precision + 100
            decimal.getcontext().prec = new_precision
            precision = new_precision
            
            # Call callback to report current value
            update_callback(pi, current_iteration, precision)
    
    return pi, precision, current_iteration

def save_to_file(pi_value, precision, iterations, elapsed_time):
    """Saves the calculated Pi value to a text file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"pi_calculation_{timestamp}.txt"
    
    with open(filename, "w") as file:
        file.write(f"Pi Calculation\n")
        file.write(f"Achieved Precision: ~{precision} digits\n")
        file.write(f"Completed Iterations: {iterations}\n")
        file.write(f"Calculation Time: {elapsed_time:.2f} seconds\n\n")
        file.write(str(pi_value))
    
    return filename

def display_pi(pi_value, max_display=1000):
    """Displays Pi on screen (with limit for very large values)."""
    pi_str = str(pi_value)
    
    # Clear screen and start new output
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Current Pi Calculation:")
    print("-" * 60)
    
    print("Pi =", pi_str[:2], end="")  # Shows "3."
    
    # Shows the decimal places in blocks of 10 for better readability
    display_length = min(max_display + 2, len(pi_str))
    
    for i in range(2, display_length):
        if (i - 2) % 10 == 0:
            print(" ", end="")
        if (i - 2) % 50 == 0 and i > 2:
            print("\n    ", end="")
        print(pi_str[i], end="")
    
    # For very large numbers, indicate that the output has been shortened
    if len(pi_str) > display_length:
        print(f"\n... (additional {len(pi_str) - display_length} digits being calculated)")
    
    print("\n" + "-" * 60)

def calculate_pi(time_limit=None):
    """Main function for continuous Pi calculation with optional time limit."""
    print("Starting continuous Pi calculation" + 
          (f" (Time limit: {time_limit} seconds)" if time_limit else ""))
    print("Precision increases with runtime.")
    print("Press Ctrl+C to stop the calculation at any time.")
    
    # Event to stop the calculation
    stop_event = threading.Event()
    
    # Current calculation results
    current_results = {
        "pi": None,
        "precision": BASE_PRECISION,
        "iterations": 0,
        "last_update": time.time()
    }
    
    # Callback function for updates from the calculation thread
    def update_results(pi, iterations, precision):
        current_results["pi"] = pi
        current_results["iterations"] = iterations
        current_results["precision"] = precision
        
        # Update screen only every 2 seconds (reduces flickering)
        current_time = time.time()
        if current_time - current_results["last_update"] > 2:
            display_pi(pi)
            elapsed = current_time - start_time
            print(f"Runtime: {elapsed:.2f} seconds | Iterations: {iterations} | Precision: ~{precision} digits")
            current_results["last_update"] = current_time
    
    # Function for the calculation thread
    def calculation_thread():
        try:
            pi, final_precision, iterations = chudnovsky_algorithm(
                BASE_PRECISION, 
                update_results,
                stop_event
            )
            current_results["pi"] = pi
            current_results["precision"] = final_precision
            current_results["iterations"] = iterations
        except Exception as e:
            print(f"\nError during calculation: {e}")
    
    # Timer function for time limit
    def timeout_thread():
        time.sleep(time_limit)
        print("\nTime limit reached, calculation will be stopped...")
        stop_event.set()
    
    # Record start time
    start_time = time.time()
    
    # Start thread for calculation
    thread = threading.Thread(target=calculation_thread)
    thread.daemon = True
    thread.start()
    
    # If a time limit is set, start timer
    if time_limit:
        timer = threading.Thread(target=timeout_thread)
        timer.daemon = True
        timer.start()
    
    # Wait for calculation to complete or manual interruption
    try:
        while thread.is_alive():
            thread.join(0.1)  # Short wait to allow keyboard input
    except KeyboardInterrupt:
        print("\nCalculation manually interrupted...")
    finally:
        # Stop calculation
        stop_event.set()
        # Short wait to give the thread time to finish
        time.sleep(0.5)
    
    # Record end time
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # Final display
    if current_results["pi"]:
        pi_value = current_results["pi"]
        precision = current_results["precision"]
        iterations = current_results["iterations"]
        
        display_pi(pi_value)
        
        print(f"\nCalculation completed after {elapsed_time:.2f} seconds")
        print(f"Completed Iterations: {iterations}")
        print(f"Achieved Precision: ~{precision} digits")
        
        filename = save_to_file(pi_value, precision, iterations, elapsed_time)
        print(f"Result saved in {filename}")
        
        return pi_value, precision
    else:
        print("No results (calculation was stopped too early)")
        return None, 0

def main():
    """Main program with user interface."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 60)
    print("Continuous Pi Calculation".center(60))
    print("=" * 60)
    print("This program calculates Pi continuously with increasing precision")
    print("until the set time expires or you stop the calculation.")
    print("=" * 60)
    
    try:
        use_time_limit = input("Set time limit? (y/n): ").lower() == 'y'
        time_limit = None
        
        if use_time_limit:
            time_limit = float(input("Time limit in seconds: "))
        
        print("\nCalculation starting...")
        print("Press Ctrl+C to stop the calculation at any time.")
        # Short pause to allow user to read the message
        time.sleep(2)  
        
        calculate_pi(time_limit)
        
    except ValueError:
        print("Error: Please enter a valid number.")
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    
    print("\nThank you for using this program!")

if __name__ == "__main__":
    main()