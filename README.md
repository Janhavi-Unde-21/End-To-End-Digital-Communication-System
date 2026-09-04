# End-to-End Digital Communication System

A browser-based version of the supplied Tkinter project.

## Features

- Text → 8-bit binary conversion
- Hamming(12,8) encoding
- Simulated noisy communication channel
- Random single-bit flips per Hamming block
- Bit Error Rate (BER)
- Hamming syndrome calculation
- Single-bit error correction
- Corrected binary display
- Binary → text recovery
- Slow step-by-step educational animation
- Communication log
- Responsive interface
- No backend or installation required

## Run locally

Simply open `index.html` in a browser.

For a local development server, use any static server, for example:

```bash
python -m http.server 8000
```

Then open `http://localhost:8000`.

## Deploy on GitHub Pages

1. Create a new GitHub repository.
2. Upload `index.html`, `style.css`, `script.js`, and `README.md`.
3. Push to the `main` branch.
4. Open **Settings → Pages**.
5. Under **Build and deployment**, select **Deploy from a branch**.
6. Select `main` and `/ (root)`.
7. Save.

GitHub will provide a public URL similar to:

`https://YOUR-USERNAME.github.io/YOUR-REPOSITORY/`

## Note about the original Python project

The original application uses Tkinter for its desktop GUI. This version keeps the communication/Hamming behavior but implements the GUI and animation using browser-native HTML, CSS, and JavaScript so it can run directly from GitHub Pages.

The implementation intentionally follows the supplied project's Hamming(12,8) model: 8 data bits, parity positions 1, 2, 4, and 8, and single-bit correction.


## Debugging / layout fixes in the latest version

- Start button moved near the top so it is visible in the first laptop viewport.
- Long transmitter/receiver content now extends vertically and can be scrolled.
- Fixed the effective interference-probability percentage calculation.
- Fixed the channel bit indicator so it uses the actual available channel width instead of a hard-coded position.
- Prevented horizontal page overflow.
- Reduced oversized channel graphics and output areas for laptop screens.
- Changed the desktop grid to top-align panels instead of forcing every panel to the height of the tallest panel.
- Added responsive behavior for narrower screens.
- Kept the Hamming(12,8) logic and browser self-test.
