import random
import tkinter as tk
from tkinter import messagebox


# ============================================================
# TEXT <-> BINARY
# ============================================================

def text_to_binary(text):
    """Convert text to 8-bit binary, one character at a time."""
    return ''.join(format(ord(char), '08b') for char in text)


def binary_to_text(binary):
    """Convert 8-bit binary back to text."""
    chars = []
    for i in range(0, len(binary), 8):
        byte = binary[i:i + 8]
        if len(byte) == 8:
            chars.append(chr(int(byte, 2)))
    return ''.join(chars)


# ============================================================
# HAMMING(12,8) CODE
#
# 8 data bits + 4 parity bits = 12-bit Hamming codeword.
#
# Positions:
#   1, 2, 4, 8  -> parity bits
#   3, 5, 6, 7, 9, 10, 11, 12 -> data bits
#
# This implementation is SEC:
#   Single Error Correction.
#
# The syndrome identifies a single-bit error position.
# ============================================================

HAMMING_DATA_POSITIONS = [3, 5, 6, 7, 9, 10, 11, 12]
HAMMING_PARITY_POSITIONS = [1, 2, 4, 8]


def hamming_encode_byte(data_bits):
    """Encode exactly 8 data bits into a 12-bit Hamming codeword."""
    if len(data_bits) != 8 or any(bit not in "01" for bit in data_bits):
        raise ValueError("Hamming encoder requires exactly 8 binary bits.")

    bits = ['0'] * 13  # Ignore index 0; use positions 1..12.

    # Put data bits into their positions.
    for pos, bit in zip(HAMMING_DATA_POSITIONS, data_bits):
        bits[pos] = bit

    # Even parity.
    for parity_pos in HAMMING_PARITY_POSITIONS:
        parity = 0
        for pos in range(1, 13):
            if pos & parity_pos and pos != parity_pos:
                parity ^= int(bits[pos])
        bits[parity_pos] = str(parity)

    return ''.join(bits[1:])


def hamming_syndrome(codeword):
    """Calculate the 4-bit syndrome and its decimal error position."""
    if len(codeword) != 12 or any(bit not in "01" for bit in codeword):
        raise ValueError("Hamming decoder requires exactly 12 binary bits.")

    bits = ['0'] + list(codeword)
    syndrome = 0

    for parity_pos in HAMMING_PARITY_POSITIONS:
        parity = 0
        for pos in range(1, 13):
            if pos & parity_pos:
                parity ^= int(bits[pos])
        if parity:
            syndrome += parity_pos

    syndrome_bits = format(syndrome, '04b')
    return syndrome_bits, syndrome


def hamming_decode_codeword(codeword):
    """
    Decode a 12-bit Hamming codeword.

    Returns:
        data_bits
        corrected_codeword
        syndrome_bits
        error_position (0 means no error)
        status
    """
    syndrome_bits, error_position = hamming_syndrome(codeword)
    corrected = list(codeword)

    if error_position == 0:
        status = "NO ERROR DETECTED"
    elif 1 <= error_position <= 12:
        corrected[error_position - 1] = (
            '1' if corrected[error_position - 1] == '0' else '0'
        )
        status = f"SINGLE-BIT ERROR CORRECTED AT POSITION {error_position}"
    else:
        status = "UNCORRECTABLE ERROR"

    corrected_codeword = ''.join(corrected)

    # corrected_codeword is a normal 0-indexed Python string, while Hamming
    # positions are numbered 1..12. Therefore position 3 is index 2, etc.
    data_bits = ''.join(
        corrected_codeword[pos - 1]
        for pos in HAMMING_DATA_POSITIONS
    )

    return (
        data_bits,
        corrected_codeword,
        syndrome_bits,
        error_position,
        status
    )


def hamming_encode(data):
    """Encode a complete binary string in 8-bit blocks."""
    encoded_blocks = []
    for i in range(0, len(data), 8):
        byte = data[i:i + 8]
        if len(byte) < 8:
            byte = byte.ljust(8, '0')
        encoded_blocks.append(hamming_encode_byte(byte))
    return ''.join(encoded_blocks)


def hamming_decode(encoded_data):
    """Decode a complete Hamming bitstream."""
    decoded_bits = []
    details = []

    for i in range(0, len(encoded_data), 12):
        codeword = encoded_data[i:i + 12]
        if len(codeword) != 12:
            continue

        result = hamming_decode_codeword(codeword)
        data_bits, corrected, syndrome_bits, error_position, status = result

        decoded_bits.append(data_bits)
        details.append({
            "codeword": codeword,
            "corrected": corrected,
            "syndrome": syndrome_bits,
            "position": error_position,
            "status": status
        })

    return ''.join(decoded_bits), details


# ============================================================
# CHANNEL NOISE
# ============================================================

def add_noise(data, interference_level):
    """
    Simulate changing channel interference while keeping the demo inside the
    correction capability of Hamming(12,8).

    Hamming(12,8) can correct ONE flipped bit per 12-bit codeword. Therefore,
    this channel randomly chooses some 12-bit blocks to be affected and flips
    at most one random bit in each affected block.

    The displayed interference_level is a random 0..1 channel-strength value.
    It is converted into a block-error probability for the simulation.
    """
    received = list(data)
    error_positions = []

    # Map the random interference strength to a realistic demonstration range.
    # Even at maximum interference, only up to 30% of Hamming blocks are hit.
    block_error_probability = 0.02 + (0.28 * interference_level)

    for block_start in range(0, len(received), 12):
        block_end = min(block_start + 12, len(received))
        block_length = block_end - block_start

        if block_length == 12 and random.random() < block_error_probability:
            # Interference hits one random bit in this Hamming codeword.
            error_index = random.randrange(block_start, block_end)
            received[error_index] = (
                '1' if received[error_index] == '0' else '0'
            )
            error_positions.append(error_index + 1)

    return ''.join(received), error_positions


def calculate_ber(transmitted, received):
    """Calculate bit errors and BER."""
    if not transmitted:
        return 0, 0.0

    errors = sum(
        1 for a, b in zip(transmitted, received)
        if a != b
    )
    return errors, errors / len(transmitted)


def run_hamming_self_test():
    """Verify that every possible 8-bit value round-trips through Hamming."""
    for value in range(256):
        original = format(value, "08b")
        codeword = hamming_encode_byte(original)
        decoded, corrected, syndrome, position, status = hamming_decode_codeword(codeword)
        if decoded != original or syndrome != "0000" or position != 0:
            raise RuntimeError(
                "Hamming self-test failed: "
                f"{original} -> {codeword} -> {decoded}, "
                f"syndrome={syndrome}, position={position}"
            )

        # Also test correction of every single bit in the 12-bit codeword.
        for error_pos in range(12):
            corrupted = list(codeword)
            corrupted[error_pos] = "1" if corrupted[error_pos] == "0" else "0"
            decoded, corrected, syndrome, position, status = hamming_decode_codeword(
                "".join(corrupted)
            )
            if decoded != original or position != error_pos + 1:
                raise RuntimeError(
                    "Hamming correction self-test failed: "
                    f"data={original}, error={error_pos + 1}, "
                    f"syndrome={syndrome}, decoded={decoded}"
                )




# ============================================================
# GUI
# ============================================================

class DigitalCommunicationGUI:

    def __init__(self, root):
        self.root = root

        self.root.title("End-to-End Digital Communication System - Hamming Code")
        self.root.geometry("1550x900")
        self.root.minsize(1200, 760)
        self.root.configure(bg="#f5f5f5")

        # ----------------------------------------------------
        # NEUTRAL / NORMAL WHITE UI
        # ----------------------------------------------------
        self.bg = "#f5f5f5"
        self.panel = "#ffffff"
        self.panel2 = "#fafafa"
        self.border = "#d9d9d9"

        self.text = "#222222"
        self.gray = "#666666"
        self.blue = "#356ae6"
        self.green = "#278a4b"
        self.red = "#c62828"
        self.orange = "#b26a00"
        self.black = "#111111"

        # ----------------------------------------------------
        # ANIMATION SPEED
        # Higher value = slower.
        # ----------------------------------------------------
        self.text_delay = 650
        self.hamming_delay = 450
        self.channel_delay = 160
        self.receiver_delay = 650

        # ----------------------------------------------------
        # DATA
        # ----------------------------------------------------
        self.message = ""
        self.binary_data = ""
        self.encoded_data = ""
        self.received_data = ""
        self.corrected_data = ""

        self.error_positions = []
        self.hamming_details = []

        self.running = False
        self.cancelled = False

        # Dynamic noise probability: a new random value in [0, 1] is
        # generated whenever the transmission data is reset.
        self.noise_probability = random.random()

        self.create_header()

        self.main_frame = tk.Frame(self.root, bg=self.bg)
        self.main_frame.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=8
        )

        self.create_transmitter()
        self.create_channel()
        self.create_receiver()
        self.create_log()

    # ========================================================
    # HEADER
    # ========================================================

    def create_header(self):
        header = tk.Frame(self.root, bg=self.bg)
        header.pack(fill="x", padx=25, pady=(16, 5))

        tk.Label(
            header,
            text="END-TO-END DIGITAL COMMUNICATION SYSTEM",
            font=("Segoe UI", 21, "bold"),
            fg=self.text,
            bg=self.bg
        ).pack()

        tk.Label(
            header,
            text="Text → Binary → Hamming Encoding → Noisy Channel → Hamming Correction → Text",
            font=("Segoe UI", 11),
            fg=self.gray,
            bg=self.bg
        ).pack(pady=(4, 0))

    # ========================================================
    # TRANSMITTER
    # ========================================================

    def create_transmitter(self):
        self.transmitter = tk.Frame(
            self.main_frame,
            bg=self.panel,
            highlightbackground=self.border,
            highlightthickness=1
        )
        self.transmitter.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 7)
        )

        tk.Label(
            self.transmitter,
            text="TRANSMITTER",
            font=("Segoe UI", 16, "bold"),
            fg=self.blue,
            bg=self.panel
        ).pack(pady=(13, 8))

        tk.Label(
            self.transmitter,
            text="Enter Message",
            font=("Segoe UI", 10, "bold"),
            fg=self.text,
            bg=self.panel
        ).pack(anchor="w", padx=15)

        self.message_entry = tk.Entry(
            self.transmitter,
            font=("Consolas", 12),
            bg="#ffffff",
            fg=self.text,
            insertbackground=self.text,
            relief="solid",
            bd=1
        )
        self.message_entry.pack(
            fill="x",
            padx=15,
            pady=7,
            ipady=7
        )

        self.create_section_label(
            self.transmitter,
            "① TEXT → BINARY (VISIBLE CHARACTER-BY-CHARACTER)"
        )

        self.binary_text = self.create_text_box(
            self.transmitter,
            height=6
        )

        self.create_section_label(
            self.transmitter,
            "② HAMMING(12,8) ENCODING"
        )

        self.hamming_status = tk.Label(
            self.transmitter,
            text="Waiting for Hamming encoding...",
            font=("Consolas", 10, "bold"),
            fg=self.orange,
            bg=self.panel
        )
        self.hamming_status.pack(anchor="w", padx=15, pady=3)

        self.encoded_text = self.create_text_box(
            self.transmitter,
            height=7
        )

        probability_frame = tk.Frame(
            self.transmitter,
            bg=self.panel
        )
        probability_frame.pack(
            fill="x",
            padx=15,
            pady=7
        )

        self.noise_probability_label = tk.Label(
            probability_frame,
            text=f"Interference Level: {self.noise_probability:.4f}",
            font=("Segoe UI", 10, "bold"),
            fg=self.orange,
            bg=self.panel
        )
        self.noise_probability_label.pack(side="left")

        tk.Label(
            probability_frame,
            text="(randomly changes from 0 to 1; Hamming-safe interference model)",
            font=("Segoe UI", 9),
            fg=self.gray,
            bg=self.panel
        ).pack(side="left", padx=8)

        button_frame = tk.Frame(
            self.transmitter,
            bg=self.panel
        )
        button_frame.pack(
            fill="x",
            padx=15,
            pady=9
        )

        self.send_button = tk.Button(
            button_frame,
            text="▶  START SLOW TRANSMISSION",
            command=self.start_transmission,
            font=("Segoe UI", 10, "bold"),
            bg="#e9eefc",
            fg=self.blue,
            activebackground="#dce5fb",
            relief="solid",
            bd=1,
            cursor="hand2"
        )
        self.send_button.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=7
        )

        self.reset_button = tk.Button(
            button_frame,
            text="RESET",
            command=self.reset,
            font=("Segoe UI", 10, "bold"),
            bg="#ffffff",
            fg=self.text,
            activebackground="#eeeeee",
            relief="solid",
            bd=1,
            cursor="hand2"
        )
        self.reset_button.pack(
            side="left",
            padx=(8, 0),
            ipady=7
        )

    # ========================================================
    # CHANNEL
    # ========================================================

    def create_channel(self):
        self.channel = tk.Frame(
            self.main_frame,
            bg=self.panel2,
            width=260,
            highlightbackground=self.border,
            highlightthickness=1
        )
        self.channel.pack(
            side="left",
            fill="both",
            padx=7
        )
        self.channel.pack_propagate(False)

        tk.Label(
            self.channel,
            text="NOISY CHANNEL",
            font=("Segoe UI", 15, "bold"),
            fg=self.orange,
            bg=self.panel2
        ).pack(pady=(18, 8))

        self.canvas = tk.Canvas(
            self.channel,
            width=220,
            height=250,
            bg=self.panel2,
            highlightthickness=0
        )
        self.canvas.pack(pady=8)

        self.canvas.create_line(
            25, 125, 195, 125,
            fill="#bdbdbd",
            width=3
        )

        self.canvas.create_polygon(
            195, 125,
            180, 117,
            180, 133,
            fill=self.blue,
            outline=""
        )

        self.canvas.create_text(
            110, 82,
            text="DATA",
            fill=self.gray,
            font=("Segoe UI", 10, "bold")
        )

        self.canvas.create_text(
            110, 168,
            text="RANDOM BIT FLIPS",
            fill=self.red,
            font=("Segoe UI", 9, "bold")
        )

        self.bit_indicator = self.canvas.create_oval(
            15, 115, 35, 135,
            fill=self.blue,
            outline=""
        )

        self.channel_bit_label = tk.Label(
            self.channel,
            text="Current bit: -",
            font=("Consolas", 10, "bold"),
            fg=self.text,
            bg=self.panel2
        )
        self.channel_bit_label.pack(pady=3)

        self.channel_status = tk.Label(
            self.channel,
            text="WAITING FOR DATA",
            font=("Segoe UI", 10, "bold"),
            fg=self.gray,
            bg=self.panel2
        )
        self.channel_status.pack(pady=8)

        tk.Label(
            self.channel,
            text="ERROR POSITIONS",
            font=("Segoe UI", 10, "bold"),
            fg=self.text,
            bg=self.panel2
        ).pack(pady=(12, 4))

        self.error_label = tk.Label(
            self.channel,
            text="None",
            font=("Consolas", 9),
            fg=self.red,
            bg=self.panel2,
            wraplength=225,
            justify="center"
        )
        self.error_label.pack(padx=10)

        self.ber_label = tk.Label(
            self.channel,
            text="BER: ---",
            font=("Segoe UI", 12, "bold"),
            fg=self.blue,
            bg=self.panel2
        )
        self.ber_label.pack(pady=18)

    # ========================================================
    # RECEIVER
    # ========================================================

    def create_receiver(self):
        self.receiver = tk.Frame(
            self.main_frame,
            bg=self.panel,
            highlightbackground=self.border,
            highlightthickness=1
        )
        self.receiver.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(7, 0)
        )

        tk.Label(
            self.receiver,
            text="RECEIVER",
            font=("Segoe UI", 16, "bold"),
            fg=self.green,
            bg=self.panel
        ).pack(pady=(13, 8))

        self.create_section_label(
            self.receiver,
            "③ RECEIVED DATA AFTER CHANNEL"
        )

        self.received_text = self.create_text_box(
            self.receiver,
            height=7
        )

        self.create_section_label(
            self.receiver,
            "④ HAMMING SYNDROME + CORRECTION"
        )

        self.hamming_receiver_status = tk.Label(
            self.receiver,
            text="Waiting...",
            font=("Consolas", 10, "bold"),
            fg=self.gray,
            bg=self.panel,
            justify="left",
            anchor="w"
        )
        self.hamming_receiver_status.pack(
            fill="x",
            padx=15,
            pady=3
        )

        self.comparison_text = self.create_text_box(
            self.receiver,
            height=8
        )

        self.create_section_label(
            self.receiver,
            "⑤ CORRECTED BINARY"
        )

        self.corrected_binary_text = self.create_text_box(
            self.receiver,
            height=5
        )

        self.create_section_label(
            self.receiver,
            "⑥ BINARY → TEXT"
        )

        self.recovered_label = tk.Label(
            self.receiver,
            text="---",
            font=("Consolas", 14, "bold"),
            fg=self.text,
            bg="#ffffff",
            highlightbackground=self.border,
            highlightthickness=1,
            wraplength=470,
            padx=10,
            pady=9
        )
        self.recovered_label.pack(
            fill="x",
            padx=15,
            pady=5
        )

    # ========================================================
    # LOG
    # ========================================================

    def create_log(self):
        log_frame = tk.Frame(
            self.root,
            bg=self.panel,
            highlightbackground=self.border,
            highlightthickness=1
        )
        log_frame.pack(
            fill="x",
            padx=18,
            pady=(4, 15)
        )

        tk.Label(
            log_frame,
            text="COMMUNICATION LOG",
            font=("Segoe UI", 10, "bold"),
            fg=self.text,
            bg=self.panel
        ).pack(
            anchor="w",
            padx=10,
            pady=(7, 2)
        )

        self.log = tk.Text(
            log_frame,
            height=5,
            bg="#ffffff",
            fg=self.gray,
            font=("Consolas", 9),
            relief="solid",
            bd=1,
            state="disabled"
        )
        self.log.pack(
            fill="x",
            padx=10,
            pady=(2, 8)
        )

    # ========================================================
    # HELPERS
    # ========================================================

    def create_section_label(self, parent, text):
        tk.Label(
            parent,
            text=text,
            font=("Segoe UI", 10, "bold"),
            fg=self.text,
            bg=self.panel
        ).pack(
            anchor="w",
            padx=15,
            pady=(7, 2)
        )

    def create_text_box(self, parent, height=5):
        text = tk.Text(
            parent,
            height=height,
            bg="#ffffff",
            fg=self.text,
            insertbackground=self.text,
            font=("Consolas", 9),
            relief="solid",
            bd=1,
            wrap="word"
        )
        text.pack(
            fill="x",
            padx=15,
            pady=4
        )
        text.config(state="disabled")
        return text

    def update_text_box(self, widget, text):
        widget.config(state="normal")
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, text)
        widget.config(state="disabled")
        widget.see(tk.END)
        self.root.update_idletasks()

    def append_text_box(self, widget, text):
        widget.config(state="normal")
        widget.insert(tk.END, text)
        widget.config(state="disabled")
        widget.see(tk.END)
        self.root.update_idletasks()

    def add_log(self, text):
        self.log.config(state="normal")
        self.log.insert(tk.END, text + "\n")
        self.log.see(tk.END)
        self.log.config(state="disabled")
        self.root.update_idletasks()

    # ========================================================
    # START
    # ========================================================

    def start_transmission(self):
        if self.running:
            return

        message = self.message_entry.get()

        if message == "":
            messagebox.showwarning(
                "Invalid Input",
                "Message cannot be empty."
            )
            return

        probability = self.noise_probability

        self.running = True
        self.cancelled = False
        self.send_button.config(state="disabled")
        self.reset_button.config(state="disabled")

        self.clear_all_output()

        self.message = message
        self.binary_data = ""
        self.encoded_data = ""
        self.received_data = ""
        self.corrected_data = ""
        self.error_positions = []
        self.hamming_details = []

        self.add_log("==================================================")
        self.add_log("TRANSMISSION STARTED")
        self.add_log(f"Original message: {message}")
        self.add_log("Using Hamming(12,8) for single-bit error correction.")
        self.add_log(
            f"Random interference level: {probability:.4f}"
        )
        self.add_log(
            f"Effective Hamming-block interference probability: "
            f"{(0.02 + 0.28 * probability):.2%}"
        )
        self.add_log(
            "Channel model: at most ONE random bit is flipped per 12-bit Hamming block, "
            "so the Hamming correction demonstration remains valid."
        )
        self.add_log("All stages are intentionally slowed for visual learning.")

        # Start visible step-by-step conversion.
        self.animate_text_to_binary(0, "")

    # ========================================================
    # STEP 1: TEXT -> BINARY, CHARACTER BY CHARACTER
    # ========================================================

    def animate_text_to_binary(self, index, current):
        if self.cancelled:
            return

        if index < len(self.message):
            char = self.message[index]
            bits = format(ord(char), "08b")

            self.binary_data += bits

            display = (
                f"Character {index + 1}/{len(self.message)}: "
                f"'{char}'  →  {bits}\n"
                f"Binary so far: {self.binary_data}"
            )

            self.update_text_box(self.binary_text, display)

            self.add_log(
                f"Step 1: '{char}' converted to binary {bits}"
            )

            self.root.after(
                self.text_delay,
                lambda: self.animate_text_to_binary(index + 1, current)
            )
        else:
            self.add_log("✓ Step 1 complete: TEXT → BINARY")
            self.root.after(
                900,
                lambda: self.start_hamming_encoding(0)
            )

    # ========================================================
    # STEP 2: HAMMING ENCODING
    # ========================================================

    def start_hamming_encoding(self, byte_index):
        if self.cancelled:
            return

        total_bytes = len(self.binary_data) // 8

        if byte_index >= total_bytes:
            self.hamming_status.config(
                text="✓ Hamming encoding complete.",
                fg=self.green
            )
            self.add_log("✓ Step 2 complete: BINARY → HAMMING CODE")
            self.root.after(
                1000,
                self.start_channel
            )
            return

        byte = self.binary_data[
            byte_index * 8:(byte_index + 1) * 8
        ]

        codeword = hamming_encode_byte(byte)
        self.encoded_data += codeword

        parity_info = (
            f"Byte {byte_index + 1}/{total_bytes}\n"
            f"Data bits:    {byte}\n"
            f"Hamming code: {codeword}\n"
            f"Positions:     123456789012\n"
            f"                {codeword}"
        )

        self.hamming_status.config(
            text=parity_info,
            fg=self.orange
        )

        self.update_text_box(
            self.encoded_text,
            f"Encoded blocks so far:\n{self.group_bits(self.encoded_data, 12)}"
        )

        self.add_log(
            f"Step 2: Byte {byte_index + 1} "
            f"{byte} → Hamming {codeword}"
        )

        self.root.after(
            self.hamming_delay,
            lambda: self.start_hamming_encoding(byte_index + 1)
        )

    # ========================================================
    # STEP 3: CHANNEL
    # ========================================================

    def start_channel(self):
        if self.cancelled:
            return

        probability = self.noise_probability

        self.channel_status.config(
            text=f"INTERFERENCE: {probability:.4f}  |  TRANSMITTING...",
            fg=self.blue
        )

        self.add_log(
            f"Step 3: Sending {len(self.encoded_data)} bits through noisy channel."
        )

        # Generate final received data now, but display it one bit at a time.
        self.received_data, self.error_positions = add_noise(
            self.encoded_data,
            probability
        )

        self.animate_channel(0, "")

    def animate_channel(self, index, shown):
        if self.cancelled:
            return

        if index < len(self.encoded_data):
            tx_bit = self.encoded_data[index]
            rx_bit = self.received_data[index]

            if tx_bit != rx_bit:
                self.add_log(
                    f"Channel bit {index + 1}: {tx_bit} → {rx_bit}  [NOISE FLIP]"
                )
                status = "NOISE FLIP"
                status_color = self.red
            else:
                self.add_log(
                    f"Channel bit {index + 1}: {tx_bit} → {rx_bit}"
                )
                status = "UNCHANGED"
                status_color = self.green

            shown += rx_bit

            self.update_text_box(
                self.received_text,
                f"Receiving bit {index + 1}/{len(self.encoded_data)}\n"
                f"Received so far:\n{shown}"
            )

            self.channel_bit_label.config(
                text=f"Bit {index + 1}: TX={tx_bit}  RX={rx_bit}",
                fg=status_color
            )

            self.channel_status.config(
                text=status,
                fg=status_color
            )

            x = 20 + (175 * index / max(1, len(self.encoded_data) - 1))

            self.canvas.coords(
                self.bit_indicator,
                x - 10, 115,
                x + 10, 135
            )

            self.root.after(
                self.channel_delay,
                lambda: self.animate_channel(index + 1, shown)
            )

        else:
            self.channel_status.config(
                text="TRANSMISSION COMPLETE",
                fg=self.green
            )

            if self.error_positions:
                self.error_label.config(
                    text=", ".join(map(str, self.error_positions)),
                    fg=self.red
                )
            else:
                self.error_label.config(
                    text="None",
                    fg=self.green
                )

            errors, ber = calculate_ber(
                self.encoded_data,
                self.received_data
            )

            self.ber_label.config(
                text=f"BER: {ber:.6f}"
            )

            self.add_log(
                f"Channel complete: {errors} bit error(s), measured BER = {ber:.6f}"
            )

            self.root.after(
                1000,
                lambda: self.start_hamming_decoding(0)
            )

    # ========================================================
    # STEP 4: HAMMING DETECTION + CORRECTION
    # ========================================================

    def start_hamming_decoding(self, block_index):
        if self.cancelled:
            return

        total_blocks = len(self.received_data) // 12

        if block_index >= total_blocks:
            self.hamming_receiver_status.config(
                text="✓ All Hamming blocks checked and corrected.",
                fg=self.green
            )

            self.update_text_box(
                self.corrected_binary_text,
                f"Corrected data bits:\n{self.corrected_data}"
            )

            self.add_log(
                "✓ Step 4 complete: Hamming detection/correction finished."
            )

            self.root.after(
                1000,
                self.start_binary_to_text
            )
            return

        start = block_index * 12
        received_codeword = self.received_data[start:start + 12]

        syndrome_bits, syndrome_value = hamming_syndrome(
            received_codeword
        )

        data_bits, corrected_codeword, _, error_position, status = (
            hamming_decode_codeword(received_codeword)
        )

        self.corrected_data += data_bits
        self.hamming_details.append({
            "received": received_codeword,
            "syndrome": syndrome_bits,
            "position": error_position,
            "corrected": corrected_codeword,
            "data": data_bits,
            "status": status
        })

        if error_position == 0:
            status_color = self.green
        else:
            status_color = self.red

        status_text = (
            f"Block {block_index + 1}/{total_blocks}\n"
            f"Received codeword: {received_codeword}\n"
            f"Syndrome:          {syndrome_bits}  "
            f"(decimal {syndrome_value})\n"
        )

        if error_position == 0:
            status_text += "Result: NO ERROR DETECTED"
        else:
            status_text += (
                f"Error position:    {error_position}\n"
                f"Corrected code:    {corrected_codeword}\n"
                f"Result:            SINGLE-BIT ERROR CORRECTED"
            )

        self.hamming_receiver_status.config(
            text=status_text,
            fg=status_color
        )

        self.update_text_box(
            self.comparison_text,
            self.build_hamming_comparison(block_index)
        )

        self.add_log(
            f"Step 4: Block {block_index + 1}: "
            f"syndrome={syndrome_bits}, "
            f"position={error_position}, "
            f"{status}"
        )

        self.root.after(
            self.receiver_delay,
            lambda: self.start_hamming_decoding(block_index + 1)
        )

    # ========================================================
    # HAMMING COMPARISON DISPLAY
    # ========================================================

    def build_hamming_comparison(self, current_block):
        lines = []

        for i, detail in enumerate(self.hamming_details):
            lines.append(
                f"BLOCK {i + 1}\n"
                f"RX:       {detail['received']}\n"
                f"SYNDROME: {detail['syndrome']}\n"
                f"ERROR:    "
                f"{detail['position'] if detail['position'] else 'None'}\n"
                f"FIXED:    {detail['corrected']}\n"
                f"DATA:     {detail['data']}\n"
                f"STATUS:   {detail['status']}\n"
            )

        return "\n".join(lines)

    # ========================================================
    # STEP 5: BINARY -> TEXT, CHARACTER BY CHARACTER
    # ========================================================

    def start_binary_to_text(self, char_index=0):
        if self.cancelled:
            return

        total_chars = len(self.corrected_data) // 8

        if char_index >= total_chars:
            self.add_log("✓ Step 5 complete: BINARY → TEXT")
            self.recovered_label.config(
                text=self.binary_to_text_visible_result(),
                fg=self.green
            )

            recovered = self.binary_to_text_visible_result()

            if recovered == self.message:
                self.add_log("✓ TRANSMISSION SUCCESSFUL.")
                self.add_log("✓ Original message was recovered correctly.")
            else:
                self.add_log(
                    "⚠ Message differs from original. "
                    "Unexpected mismatch: inspect the Hamming blocks and channel log."
                )

            self.running = False
            self.send_button.config(state="normal")
            self.reset_button.config(state="normal")
            return

        start = char_index * 8
        byte = self.corrected_data[start:start + 8]
        char = chr(int(byte, 2))

        previous = self.recovered_label.cget("text")
        if previous == "---":
            previous = ""

        new_text = previous + char

        self.recovered_label.config(
            text=new_text,
            fg=self.green
        )

        self.add_log(
            f"Step 5: Binary {byte} → '{char}'"
        )

        self.root.after(
            self.text_delay,
            lambda: self.start_binary_to_text(char_index + 1)
        )

    def binary_to_text_visible_result(self):
        return binary_to_text(self.corrected_data)

    # ========================================================
    # GROUP BITS
    # ========================================================

    @staticmethod
    def group_bits(data, group_size):
        return " ".join(
            data[i:i + group_size]
            for i in range(0, len(data), group_size)
        )

    # ========================================================
    # CLEAR OUTPUT
    # ========================================================

    def clear_all_output(self):
        self.update_text_box(self.binary_text, "")
        self.update_text_box(self.encoded_text, "")
        self.update_text_box(self.received_text, "")
        self.update_text_box(self.comparison_text, "")
        self.update_text_box(self.corrected_binary_text, "")

        self.hamming_status.config(
            text="Waiting for Hamming encoding...",
            fg=self.orange
        )

        self.hamming_receiver_status.config(
            text="Waiting...",
            fg=self.gray
        )

        self.recovered_label.config(
            text="---",
            fg=self.text
        )

        self.error_label.config(
            text="None",
            fg=self.gray
        )

        self.ber_label.config(
            text="BER: ---"
        )

        self.channel_status.config(
            text="WAITING FOR DATA",
            fg=self.gray
        )

        self.channel_bit_label.config(
            text="Current bit: -",
            fg=self.text
        )

    # ========================================================
    # RESET
    # ========================================================

    def reset(self):
        if self.running:
            self.cancelled = True

        self.running = False

        self.message_entry.delete(0, tk.END)

        # Generate a completely new noise probability for this reset.
        self.noise_probability = random.random()
        self.noise_probability_label.config(
            text=f"Interference Level: {self.noise_probability:.4f}"
        )

        self.binary_data = ""
        self.encoded_data = ""
        self.received_data = ""
        self.corrected_data = ""
        self.error_positions = []
        self.hamming_details = []

        self.clear_all_output()

        self.canvas.coords(
            self.bit_indicator,
            15, 115,
            35, 135
        )

        self.log.config(state="normal")
        self.log.delete("1.0", tk.END)
        self.log.config(state="disabled")

        self.send_button.config(state="normal")
        self.reset_button.config(state="normal")


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":
    run_hamming_self_test()
    root = tk.Tk()
    app = DigitalCommunicationGUI(root)
    root.mainloop()
