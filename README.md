# End-to-End Digital Communication System

A Python-based graphical simulation of an **End-to-End Digital Communication System** using **Hamming(12,8) Error Correction**.

The project demonstrates how a text message travels through a digital communication system by converting text into binary, applying Hamming encoding, transmitting the encoded data through a simulated noisy channel, detecting and correcting single-bit errors, and finally recovering the original text.

---

## 📌 Project Overview

The system follows the complete communication pipeline:

```text
Text
  ↓
Binary Conversion
  ↓
Hamming(12,8) Encoding
  ↓
Noisy Communication Channel
  ↓
Random Bit Flips
  ↓
Hamming Syndrome Detection
  ↓
Single-Bit Error Correction
  ↓
Corrected Binary
  ↓
Text Recovery
```

The application provides a visual representation of each stage through a **Tkinter-based GUI**, making it useful for understanding concepts from **Digital Communication, Error Control Coding, and Computer Networks**.

---

## ✨ Features

* Text-to-binary conversion
* Character-by-character binary visualization
* Hamming(12,8) encoding
* 8 data bits + 4 parity bits
* Single-bit error correction (SEC)
* Simulated noisy communication channel
* Random bit-flip generation
* Dynamic interference level
* Bit-by-bit transmission animation
* Error position identification
* Hamming syndrome calculation
* Corrected codeword display
* Bit Error Rate (BER) calculation
* Binary-to-text recovery
* Communication log
* Reset functionality
* Automated Hamming self-test for all 256 possible 8-bit values
* Clean graphical interface using Tkinter

---

## 🧠 Hamming(12,8) Code

The project uses the **Hamming(12,8)** error-correcting code.

Each 8-bit data block is converted into a 12-bit Hamming codeword.

### Bit Positions

| Position | Type   |
| -------- | ------ |
| 1        | Parity |
| 2        | Parity |
| 3        | Data   |
| 4        | Parity |
| 5        | Data   |
| 6        | Data   |
| 7        | Data   |
| 8        | Parity |
| 9        | Data   |
| 10       | Data   |
| 11       | Data   |
| 12       | Data   |

Therefore:

```text
4 Parity Bits + 8 Data Bits = 12-bit Codeword
```

The implementation uses **even parity** and calculates a **4-bit syndrome** to identify the position of a single-bit error.

The Hamming decoder can determine whether there is no error or correct a single-bit error within each 12-bit block.

---

## 📡 Communication Process

### 1. Text → Binary

The entered message is converted into 8-bit binary representation.

For example:

```text
A
```

is represented as:

```text
01000001
```

The application displays this conversion character by character.

---

### 2. Binary → Hamming Code

Each 8-bit block is passed to the Hamming encoder.

```text
8-bit Data
    ↓
Hamming(12,8)
    ↓
12-bit Codeword
```

The encoded blocks are displayed in the transmitter panel.

---

### 3. Noisy Channel

The encoded data is transmitted through a simulated communication channel.

The channel randomly selects some complete 12-bit Hamming blocks and may flip **at most one bit in each affected block**.

The interference level is randomly generated between `0` and `1` and is mapped to a block-error probability:

```text
P(error) = 0.02 + (0.28 × interference_level)
```

This keeps the demonstration within the single-bit correction capability of Hamming(12,8).

---

### 4. BER Calculation

The system compares the transmitted and received encoded data.

```text
BER = Number of Bit Errors / Total Number of Transmitted Bits
```

The calculated BER is displayed in the channel panel.

---

### 5. Hamming Error Detection & Correction

At the receiver, every 12-bit block is analyzed.

The system calculates the syndrome:

```text
Syndrome = 0000
```

means:

```text
No error detected
```

A non-zero syndrome identifies the position of the erroneous bit.

The system then flips that bit to recover the original codeword.

---

### 6. Corrected Binary

After all Hamming blocks are processed, the corrected 8-bit data blocks are extracted and combined to reconstruct the original binary stream.

---

### 7. Binary → Text

The corrected binary data is converted back into characters.

If the error correction is successful:

```text
Original Message == Recovered Message
```

the communication is marked as successful.

---

## 🖥️ Graphical User Interface

The GUI is divided into three major sections:

### Transmitter

Contains:

* Message input
* Text → Binary conversion
* Hamming encoding
* Interference level
* Start Transmission button
* Reset button

### Noisy Channel

Displays:

* Data transmission
* Current transmitted/received bit
* Random bit flips
* Error positions
* BER
* Transmission status

### Receiver

Displays:

* Received data
* Hamming syndrome
* Error position
* Corrected codeword
* Corrected binary
* Recovered text

A communication log at the bottom records the complete transmission process.

---

## 🛠️ Technologies Used

* **Python 3**
* **Tkinter** – Graphical User Interface
* **Random** – Channel noise and interference simulation

No external Python packages are required because the project uses Python's built-in modules.

---

## 📋 Requirements

Make sure Python 3 is installed.

Check your Python installation:

```bash
python --version
```

or:

```bash
python3 --version
```

Tkinter must also be available.

### Windows

Tkinter is normally included with standard Python installations.

### Linux

If Tkinter is not installed:

```bash
sudo apt install python3-tk
```

---

## 🚀 Installation & Execution

### 1. Clone the repository

```bash
git clone <YOUR-GITHUB-REPOSITORY-URL>
```

### 2. Navigate into the project

```bash
cd <PROJECT-FOLDER>
```

### 3. Run the program

```bash
python main.py
```

Replace `main.py` with the actual Python filename if your file has a different name.

---

## ▶️ How to Use

1. Launch the application.
2. Enter a message in the **TRANSMITTER** section.
3. Click **START SLOW TRANSMISSION**.
4. Observe the text being converted into binary.
5. Observe Hamming(12,8) encoding.
6. Watch the data pass through the simulated noisy channel.
7. Observe any random bit flips.
8. Check the calculated BER.
9. Observe the Hamming syndrome at the receiver.
10. Observe the erroneous bit being corrected.
11. Observe the corrected binary data.
12. Verify that the original message is recovered.

---

## 🧪 Self-Test

The application includes an automated Hamming self-test before launching the GUI.

The test checks:

* All **256 possible 8-bit values**
* Correct Hamming encoding
* Correct decoding
* No-error syndrome
* Correction of every possible single-bit error in a 12-bit codeword

This provides a basic verification that the Hamming implementation correctly performs single-bit error correction.

---

## 📊 Example

Suppose the user enters:

```text
HELLO
```

The system performs:

```text
HELLO
  ↓
01001000 01000101 01001100 01001100 01001111
  ↓
Hamming(12,8) Encoding
  ↓
12-bit Codewords
  ↓
Noisy Channel
  ↓
Possible Single-Bit Errors
  ↓
Syndrome Calculation
  ↓
Error Correction
  ↓
Corrected Binary
  ↓
HELLO
```

The communication log provides information about each stage.

---

## ⚠️ Error Correction Limitation

This implementation demonstrates **Single Error Correction (SEC)**.

Hamming(12,8) can correct:

```text
One bit error per 12-bit codeword
```

The simulated channel intentionally limits each affected block to one flipped bit so that the correction demonstration remains valid.

It should not be interpreted as a general-purpose communication-channel simulator capable of correcting arbitrary multiple-bit errors.

---

## 📁 Suggested Project Structure

```text
digital-communication-system/
│
├── main.py
├── README.md
└── screenshots/
    ├── transmitter.png
    ├── noisy-channel.png
    └── receiver.png
```

If you use a different filename, update the execution command accordingly.

---

## 🎯 Learning Objectives

This project helps demonstrate:

* Digital data representation
* Binary encoding
* Error-control coding
* Hamming codes
* Parity bits
* Syndrome calculation
* Error detection
* Error correction
* Communication-channel noise
* Bit Error Rate
* End-to-end data transmission
* GUI-based visualization of communication systems

---

## 🔮 Future Enhancements

Possible improvements include:

* Support for Hamming(7,4)
* Support for Hamming(15,11)
* Double-bit error detection
* More realistic noise models
* Configurable noise levels
* Graphical BER vs. noise-level plots
* Transmission statistics
* Packet/frame visualization
* Export communication logs
* Dark/light theme
* Support for file transmission
* Comparison between different error-correcting codes

---

## 👨‍💻 Author

**Janhavi Unde**
**Sara Ture**

Department of Electronics & Telecommunication Engineering
Pillai College of Engineering
Navi Mumbai, India

---

## 📄 License

This project is intended for educational and academic purposes.

You may modify and extend the project for learning, demonstrations, and academic submissions.
