// news-image-20261121 entrypoint.
// Validates the bundled entry.png, then copies it atomically to the
// make.fun output directory. Node 22, standard library only.
import { readFileSync, writeFileSync, renameSync, mkdirSync, statSync, unlinkSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const MAX_BYTES = 1024 * 1024; // 1 MiB
const EXPECTED_W = 1024;
const EXPECTED_H = 1024;
const PNG_SIG = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

function fail(msg: string): never {
  process.stderr.write(`main.ts: error: ${msg}\n`);
  process.exit(1);
}

// CRC-32 (PNG polynomial 0xEDB88320), table built at startup.
const CRC_TABLE: number[] = (() => {
  const table: number[] = [];
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) {
      c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    }
    table.push(c >>> 0);
  }
  return table;
})();

function crc32(buf: Buffer): number {
  let c = 0xffffffff;
  for (let i = 0; i < buf.length; i++) {
    c = CRC_TABLE[(c ^ buf[i]) & 0xff] ^ (c >>> 8);
  }
  return (c ^ 0xffffffff) >>> 0;
}

function validatePng(buf: Buffer, name: string): void {
  if (buf.length === 0) {
    fail(`${name}: file is empty`);
  }
  if (buf.length >= MAX_BYTES) {
    fail(`${name}: ${buf.length} bytes is not under the 1 MiB limit`);
  }
  if (buf.length < 8 + 25) {
    fail(`${name}: too short to be a PNG with an IHDR chunk`);
  }
  if (!buf.subarray(0, 8).equals(PNG_SIG)) {
    fail(`${name}: bad PNG signature`);
  }
  // First chunk must be IHDR with length 13.
  const ihdrLen = buf.readUInt32BE(8);
  const ihdrType = buf.toString("ascii", 12, 16);
  if (ihdrType !== "IHDR") {
    fail(`${name}: first chunk is "${ihdrType}", expected "IHDR"`);
  }
  if (ihdrLen !== 13) {
    fail(`${name}: IHDR length is ${ihdrLen}, expected 13`);
  }
  const width = buf.readUInt32BE(16);
  const height = buf.readUInt32BE(20);
  if (width !== EXPECTED_W || height !== EXPECTED_H) {
    fail(`${name}: dimensions are ${width}x${height}, expected ${EXPECTED_W}x${EXPECTED_H}`);
  }
  const bitDepth = buf[24];
  const colourType = buf[25];
  if (bitDepth !== 8) {
    fail(`${name}: bit depth is ${bitDepth}, expected 8`);
  }
  if (colourType !== 2 && colourType !== 6) {
    fail(`${name}: colour type is ${colourType}, expected 2 (RGB) or 6 (RGBA)`);
  }
  // Verify the IHDR CRC-32 over chunk type + data.
  const storedCrc = buf.readUInt32BE(29);
  const computedCrc = crc32(buf.subarray(12, 29));
  if (storedCrc !== computedCrc) {
    fail(`${name}: IHDR CRC-32 mismatch (stored ${storedCrc}, computed ${computedCrc})`);
  }
  walkChunks(buf, name);
}

// Walk every chunk in the file: each chunk must be well-formed, its CRC-32
// must verify, the file must end with an IEND chunk, and no bytes may
// trail the IEND.
function walkChunks(buf: Buffer, name: string): void {
  let offset = 8; // skip the 8-byte signature
  let sawIend = false;
  while (offset < buf.length) {
    if (offset + 12 > buf.length) {
      fail(`${name}: truncated chunk header at offset ${offset}`);
    }
    const len = buf.readUInt32BE(offset);
    const type = buf.toString("ascii", offset + 4, offset + 8);
    const dataStart = offset + 8;
    const dataEnd = dataStart + len;
    if (dataEnd + 4 > buf.length) {
      fail(`${name}: chunk "${type}" at offset ${offset} overruns the file`);
    }
    const stored = buf.readUInt32BE(dataEnd);
    const computed = crc32(buf.subarray(offset + 4, dataEnd));
    if (stored !== computed) {
      fail(`${name}: CRC-32 mismatch in chunk "${type}" at offset ${offset}`);
    }
    offset = dataEnd + 4;
    if (type === "IEND") {
      sawIend = true;
      break;
    }
  }
  if (!sawIend) {
    fail(`${name}: no IEND chunk found`);
  }
  if (offset !== buf.length) {
    fail(`${name}: ${buf.length - offset} trailing byte(s) after IEND`);
  }
}

function main(): void {
  const here = dirname(fileURLToPath(import.meta.url));
  const src = join(here, "entry.png");
  let buf: Buffer;
  try {
    buf = readFileSync(src);
  } catch (e) {
    fail(`cannot read bundled entry.png at ${src}: ${(e as Error).message}`);
  }
  validatePng(buf, "entry.png");

  const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
  mkdirSync(outDir, { recursive: true });
  const dest = join(outDir, "entry.png");
  const tmp = join(outDir, `.entry.png.tmp-${process.pid}`);
  try {
    writeFileSync(tmp, buf);
    renameSync(tmp, dest);
  } catch (e) {
    try { unlinkSync(tmp); } catch { /* temp may not exist */ }
    fail(`cannot write output to ${dest}: ${(e as Error).message}`);
  }
  const outSize = statSync(dest).size;
  if (outSize !== buf.length) {
    fail(`copied file size ${outSize} does not match source size ${buf.length}`);
  }
  // Re-read the written file and validate it end to end, so a truncated or
  // corrupted copy can never be reported as a successful run.
  let written: Buffer;
  try {
    written = readFileSync(dest);
  } catch (e) {
    fail(`cannot re-read written output at ${dest}: ${(e as Error).message}`);
  }
  validatePng(written, "written entry.png");
  if (!written.equals(buf)) {
    fail(`written output differs byte for byte from the validated source`);
  }
  process.stdout.write(`main.ts: wrote ${dest} (${outSize} bytes, ${EXPECTED_W}x${EXPECTED_H})\n`);
}

main();
