# PiNinfinity - Continuous Pi Calculator

A Python program that calculates π (Pi) with continuously increasing precision using the Chudnovsky algorithm.

## Features

- Continuous calculation of π with increasing precision
- Optional time limit for calculations
- Real-time display of calculated digits
- Automatic saving of results to file
- Clean console interface
- Progress monitoring with iteration count and precision
- Graceful interruption handling

## Requirements

- Python 3.6 or higher
- Standard Python libraries (no additional packages needed):
  - decimal
  - threading
  - datetime
  - sys
  - os
  - time

## Usage

1. Run the program:
   ```bash
   python pininfinity.py
   ```

2. Choose calculation mode:
   - Set a time limit (y/n)
   - If yes, enter the desired duration in seconds

3. Monitor the calculation:
   - Watch real-time updates of π
   - See current precision and iteration count
   - Press Ctrl+C at any time to stop the calculation

## Output

- Console display:
  - Current value of π in easily readable blocks
  - Runtime statistics
  - Current precision and iteration count

- File output:
  - Results are automatically saved to `pi_calculation_YYYYMMDD_HHMMSS.txt`
  - Includes calculation details and full π value

## Technical Details

- Uses the Chudnovsky algorithm for fast convergence
- Precision increases by 100 digits every 10 iterations
- Initial precision starts at 1000 digits
- Multithreaded implementation for responsiveness
- Updates display every 2 seconds to reduce screen flicker

## Error Handling

- Graceful handling of keyboard interrupts
- Input validation for time limits
- Thread safety measures
- Automatic cleanup on program termination

## Author

Christian Möller

## License

This project is open source and available under the MIT License.
