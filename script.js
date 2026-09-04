// ============================================================
// END-TO-END DIGITAL COMMUNICATION SYSTEM
// Web version of the supplied Tkinter project.
// Hamming(12,8): 8 data bits + 4 parity bits, SEC.
// ============================================================

const DATA_POSITIONS = [3, 5, 6, 7, 9, 10, 11, 12];
const PARITY_POSITIONS = [1, 2, 4, 8];

const $ = id => document.getElementById(id);

let message = "";
let binaryData = "";
let encodedData = "";
let receivedData = "";
let correctedData = "";
let errorPositions = [];
let hammingDetails = [];
let running = false;
let cancelled = false;
let noiseProbability = Math.random();

const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

function textToBinary(text) {
  // Mirrors the supplied Python project's ord(char) + 8-bit formatting
  // for ordinary ASCII characters.
  return [...text].map(ch => {
    const value = ch.codePointAt(0);
    if (value > 255) throw new Error("Please use characters representable in one 8-bit value (0–255).");
    return value.toString(2).padStart(8, "0");
  }).join("");
}

function binaryToText(binary) {
  let result = "";
  for (let i = 0; i < binary.length; i += 8) {
    const byte = binary.slice(i, i + 8);
    if (byte.length === 8) result += String.fromCharCode(parseInt(byte, 2));
  }
  return result;
}

function hammingEncodeByte(dataBits) {
  if (dataBits.length !== 8 || /[^01]/.test(dataBits)) {
    throw new Error("Hamming encoder requires exactly 8 binary bits.");
  }

  const bits = Array(13).fill("0");

  DATA_POSITIONS.forEach((pos, i) => bits[pos] = dataBits[i]);

  PARITY_POSITIONS.forEach(parityPos => {
    let parity = 0;
    for (let pos = 1; pos <= 12; pos++) {
      if ((pos & parityPos) && pos !== parityPos) parity ^= Number(bits[pos]);
    }
    bits[parityPos] = String(parity);
  });

  return bits.slice(1).join("");
}

function hammingSyndrome(codeword) {
  if (codeword.length !== 12 || /[^01]/.test(codeword)) {
    throw new Error("Hamming decoder requires exactly 12 binary bits.");
  }

  const bits = ["0", ...codeword.split("")];
  let syndrome = 0;

  PARITY_POSITIONS.forEach(parityPos => {
    let parity = 0;
    for (let pos = 1; pos <= 12; pos++) {
      if (pos & parityPos) parity ^= Number(bits[pos]);
    }
    if (parity) syndrome += parityPos;
  });

  return {
    syndromeBits: syndrome.toString(2).padStart(4, "0"),
    errorPosition: syndrome
  };
}

function hammingDecodeCodeword(codeword) {
  const { syndromeBits, errorPosition } = hammingSyndrome(codeword);
  const corrected = codeword.split("");
  let status;

  if (errorPosition === 0) {
    status = "NO ERROR DETECTED";
  } else if (errorPosition >= 1 && errorPosition <= 12) {
    const index = errorPosition - 1;
    corrected[index] = corrected[index] === "0" ? "1" : "0";
    status = `SINGLE-BIT ERROR CORRECTED AT POSITION ${errorPosition}`;
  } else {
    status = "UNCORRECTABLE ERROR";
  }

  const correctedCodeword = corrected.join("");
  const dataBits = DATA_POSITIONS.map(pos => correctedCodeword[pos - 1]).join("");

  return { dataBits, correctedCodeword, syndromeBits, errorPosition, status };
}

function hammingEncode(data) {
  let result = "";
  for (let i = 0; i < data.length; i += 8) {
    let byte = data.slice(i, i + 8);
    if (byte.length < 8) byte = byte.padEnd(8, "0");
    result += hammingEncodeByte(byte);
  }
  return result;
}

function addNoise(data, interferenceLevel) {
  const received = data.split("");
  const positions = [];
  const blockErrorProbability = 0.02 + 0.28 * interferenceLevel;

  for (let start = 0; start < received.length; start += 12) {
    const end = Math.min(start + 12, received.length);
    if (end - start === 12 && Math.random() < blockErrorProbability) {
      const index = start + Math.floor(Math.random() * 12);
      received[index] = received[index] === "0" ? "1" : "0";
      // Python project displays 1-based position in the full stream.
      positions.push(index + 1);
    }
  }
  return { received: received.join(""), positions };
}

function calculateBER(transmitted, received) {
  if (!transmitted.length) return { errors: 0, ber: 0 };
  let errors = 0;
  for (let i = 0; i < Math.min(transmitted.length, received.length); i++) {
    if (transmitted[i] !== received[i]) errors++;
  }
  return { errors, ber: errors / transmitted.length };
}

function groupBits(data, size) {
  const groups = [];
  for (let i = 0; i < data.length; i += size) groups.push(data.slice(i, i + size));
  return groups.join(" ");
}

function setStatus(el, text, colorClass) {
  el.textContent = text;
  el.className = `status ${colorClass}`;
}

function updateNoiseLabel() {
  $("noiseLabel").textContent = `Interference Level: ${noiseProbability.toFixed(4)}`;
}

function addLog(text) {
  const log = $("logOutput");
  log.textContent += text + "\n";
  log.scrollTop = log.scrollHeight;
}

function clearOutputs() {
  $("binaryOutput").textContent = "";
  $("encodedOutput").textContent = "";
  $("receivedOutput").textContent = "";
  $("comparisonOutput").textContent = "";
  $("correctedOutput").textContent = "";
  $("recoveredText").textContent = "---";
  setStatus($("hammingStatus"), "Waiting for Hamming encoding...", "orange");
  setStatus($("receiverStatus"), "Waiting...", "gray");
  setStatus($("channelStatus"), "WAITING FOR DATA", "gray");
  $("channelBit").textContent = "Current bit: -";
  $("errorPositions").textContent = "None";
  $("berLabel").textContent = "BER: ---";
}

function reset() {
  cancelled = true;
  running = false;
  $("messageInput").value = "";
  noiseProbability = Math.random();
  updateNoiseLabel();
  binaryData = encodedData = receivedData = correctedData = "";
  errorPositions = [];
  hammingDetails = [];
  clearOutputs();
  $("logOutput").textContent = "";
  $("bitIndicator").style.left = "10px";
  $("startButton").disabled = false;
  $("resetButton").disabled = false;
}

async function startTransmission() {
  if (running) return;

  const input = $("messageInput").value;
  if (!input) {
    alert("Message cannot be empty.");
    return;
  }

  try {
    textToBinary(input);
  } catch (error) {
    alert(error.message);
    return;
  }

  running = true;
  cancelled = false;
  $("startButton").disabled = true;
  $("resetButton").disabled = true;

  clearOutputs();

  // Keep the Start button in the first viewport; users can naturally scroll
  // through the longer transmitter/receiver stages while the demo runs.
  document.querySelector(".transmitter")?.scrollIntoView({ behavior: "smooth", block: "start" });

  message = input;
  binaryData = encodedData = receivedData = correctedData = "";
  errorPositions = [];
  hammingDetails = [];

  const probability = noiseProbability;

  addLog("==================================================");
  addLog("TRANSMISSION STARTED");
  addLog(`Original message: ${message}`);
  addLog("Using Hamming(12,8) for single-bit error correction.");
  addLog(`Random interference level: ${probability.toFixed(4)}`);
  addLog(`Effective Hamming-block interference probability: ${((0.02 + 0.28 * probability) * 100).toFixed(2)}%`);
  addLog("Channel model: at most ONE random bit is flipped per 12-bit Hamming block.");
  addLog("All stages are intentionally slowed for visual learning.");

  // STEP 1
  for (let i = 0; i < message.length; i++) {
    if (cancelled) return finishCancelled();

    const ch = message[i];
    const bits = ch.codePointAt(0).toString(2).padStart(8, "0");
    binaryData += bits;

    $("binaryOutput").textContent =
      `Character ${i + 1}/${message.length}: '${ch}'  →  ${bits}\n` +
      `Binary so far: ${binaryData}`;

    addLog(`Step 1: '${ch}' converted to binary ${bits}`);
    await delay(650);
  }

  addLog("✓ Step 1 complete: TEXT → BINARY");
  await delay(900);

  // STEP 2
  const totalBytes = Math.ceil(binaryData.length / 8);
  for (let byteIndex = 0; byteIndex < totalBytes; byteIndex++) {
    if (cancelled) return finishCancelled();

    let byte = binaryData.slice(byteIndex * 8, byteIndex * 8 + 8).padEnd(8, "0");
    const codeword = hammingEncodeByte(byte);
    encodedData += codeword;

    setStatus($("hammingStatus"),
      `Byte ${byteIndex + 1}/${totalBytes}\n` +
      `Data bits:    ${byte}\n` +
      `Hamming code: ${codeword}\n` +
      `Positions:     123456789012\n` +
      `                ${codeword}`, "orange");

    $("encodedOutput").textContent =
      `Encoded blocks so far:\n${groupBits(encodedData, 12)}`;

    addLog(`Step 2: Byte ${byteIndex + 1} ${byte} → Hamming ${codeword}`);
    await delay(450);
  }

  setStatus($("hammingStatus"), "✓ Hamming encoding complete.", "green");
  addLog("✓ Step 2 complete: BINARY → HAMMING CODE");
  await delay(1000);

  // STEP 3
  setStatus($("channelStatus"),
    `INTERFERENCE: ${probability.toFixed(4)}  |  TRANSMITTING...`, "blue");
  addLog(`Step 3: Sending ${encodedData.length} bits through noisy channel.`);

  const noise = addNoise(encodedData, probability);
  receivedData = noise.received;
  errorPositions = noise.positions;

  for (let i = 0; i < encodedData.length; i++) {
    if (cancelled) return finishCancelled();

    const tx = encodedData[i];
    const rx = receivedData[i];
    const flipped = tx !== rx;

    addLog(`Channel bit ${i + 1}: ${tx} → ${rx}${flipped ? "  [NOISE FLIP]" : ""}`);

    $("receivedOutput").textContent =
      `Receiving bit ${i + 1}/${encodedData.length}\nReceived so far:\n${receivedData.slice(0, i + 1)}`;

    $("channelBit").textContent = `Bit ${i + 1}: TX=${tx}  RX=${rx}`;
    $("channelBit").style.color = flipped ? "var(--red)" : "var(--green)";
    setStatus($("channelStatus"), flipped ? "NOISE FLIP" : "UNCHANGED", flipped ? "red" : "green");

    const progress = i / Math.max(1, encodedData.length - 1);
    const visual = document.querySelector(".channel-visual");
    const indicator = $("bitIndicator");
    const visualWidth = visual ? visual.clientWidth : 220;
    const indicatorWidth = indicator.offsetWidth || 20;
    const startX = 12;
    const endX = Math.max(startX, visualWidth - indicatorWidth - 18);
    const x = startX + (endX - startX) * progress;
    indicator.style.left = `${x}px`;

    await delay(160);
  }

  setStatus($("channelStatus"), "TRANSMISSION COMPLETE", "green");
  $("errorPositions").textContent = errorPositions.length ? errorPositions.join(", ") : "None";
  $("errorPositions").style.color = errorPositions.length ? "var(--red)" : "var(--green)";

  const { errors, ber } = calculateBER(encodedData, receivedData);
  $("berLabel").textContent = `BER: ${ber.toFixed(6)}`;
  addLog(`Channel complete: ${errors} bit error(s), measured BER = ${ber.toFixed(6)}`);
  await delay(1000);

  // STEP 4
  const totalBlocks = Math.floor(receivedData.length / 12);
  for (let blockIndex = 0; blockIndex < totalBlocks; blockIndex++) {
    if (cancelled) return finishCancelled();

    const start = blockIndex * 12;
    const receivedCodeword = receivedData.slice(start, start + 12);
    const { syndromeBits, errorPosition } = hammingSyndrome(receivedCodeword);
    const result = hammingDecodeCodeword(receivedCodeword);

    correctedData += result.dataBits;
    hammingDetails.push({
      received: receivedCodeword,
      syndrome: syndromeBits,
      position: errorPosition,
      corrected: result.correctedCodeword,
      data: result.dataBits,
      status: result.status
    });

    const color = errorPosition === 0 ? "green" : "red";
    let statusText =
      `Block ${blockIndex + 1}/${totalBlocks}\n` +
      `Received codeword: ${receivedCodeword}\n` +
      `Syndrome:          ${syndromeBits}  (decimal ${errorPosition})\n`;

    if (errorPosition === 0) {
      statusText += "Result: NO ERROR DETECTED";
    } else {
      statusText +=
        `Error position:    ${errorPosition}\n` +
        `Corrected code:    ${result.correctedCodeword}\n` +
        "Result:            SINGLE-BIT ERROR CORRECTED";
    }

    setStatus($("receiverStatus"), statusText, color);

    $("comparisonOutput").textContent = hammingDetails.map((d, i) =>
      `BLOCK ${i + 1}\n` +
      `RX:       ${d.received}\n` +
      `SYNDROME: ${d.syndrome}\n` +
      `ERROR:    ${d.position || "None"}\n` +
      `FIXED:    ${d.corrected}\n` +
      `DATA:     ${d.data}\n` +
      `STATUS:   ${d.status}\n`
    ).join("\n");

    addLog(`Step 4: Block ${blockIndex + 1}: syndrome=${syndromeBits}, position=${errorPosition}, ${result.status}`);

    $("correctedOutput").textContent = `Corrected data bits:\n${correctedData}`;
    await delay(650);
  }

  setStatus($("receiverStatus"), "✓ All Hamming blocks checked and corrected.", "green");
  addLog("✓ Step 4 complete: Hamming detection/correction finished.");
  await delay(1000);

  // STEP 5
  let recovered = "";
  const totalChars = Math.floor(correctedData.length / 8);

  for (let i = 0; i < totalChars; i++) {
    if (cancelled) return finishCancelled();

    const byte = correctedData.slice(i * 8, i * 8 + 8);
    const ch = String.fromCharCode(parseInt(byte, 2));
    recovered += ch;
    $("recoveredText").textContent = recovered;
    $("recoveredText").style.color = "var(--green)";
    addLog(`Step 5: Binary ${byte} → '${ch}'`);
    await delay(650);
  }

  addLog("✓ Step 5 complete: BINARY → TEXT");

  if (recovered === message) {
    addLog("✓ TRANSMISSION SUCCESSFUL.");
    addLog("✓ Original message was recovered correctly.");
  } else {
    addLog("⚠ Message differs from original. Inspect the Hamming blocks and channel log.");
  }

  running = false;
  $("startButton").disabled = false;
  $("resetButton").disabled = false;
}

function finishCancelled() {
  running = false;
  $("startButton").disabled = false;
  $("resetButton").disabled = false;
  addLog("Transmission cancelled/reset.");
}

$("startButton").addEventListener("click", startTransmission);
$("resetButton").addEventListener("click", reset);
$("messageInput").addEventListener("keydown", event => {
  if (event.key === "Enter" && !running) startTransmission();
});

updateNoiseLabel();

// Basic self-test, equivalent to the important supplied Python self-test.
(function runSelfTest() {
  for (let value = 0; value < 256; value++) {
    const original = value.toString(2).padStart(8, "0");
    const codeword = hammingEncodeByte(original);
    const decoded = hammingDecodeCodeword(codeword);
    if (decoded.dataBits !== original || decoded.syndromeBits !== "0000" || decoded.errorPosition !== 0) {
      throw new Error(`Hamming self-test failed for ${original}`);
    }

    for (let errorPos = 0; errorPos < 12; errorPos++) {
      const corrupted = codeword.split("");
      corrupted[errorPos] = corrupted[errorPos] === "0" ? "1" : "0";
      const result = hammingDecodeCodeword(corrupted.join(""));
      if (result.dataBits !== original || result.errorPosition !== errorPos + 1) {
        throw new Error(`Hamming correction self-test failed: data=${original}, error=${errorPos + 1}`);
      }
    }
  }
})();
