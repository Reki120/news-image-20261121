/**
 * Entry point for the news-image-20261121 make.fun submission.
 *
 * The deliverable of this entry is entry.png, a 1024x1024 front-page image
 * summarising the world news of 21 November 2026. This script validates
 * that image (PNG signature and IHDR dimensions), then publishes it into
 * the output directory with an atomic rename and verifies the published
 * copy byte for byte against the source before reporting success.
 */

import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, renameSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const EXPECTED_WIDTH = 1024;
const EXPECTED_HEIGHT = 1024;
const OUTPUT_DIR = "/output";
const OUTPUT_NAME = "entry.png";

// The eight bytes every PNG file starts with.
const PNG_MAGIC = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];

function fail(message: string): never {
  console.error(`main: error: ${message}`);
  process.exit(1);
}

/** Return the pixel size declared in the PNG IHDR chunk. */
function pngDimensions(buf: Buffer): { width: number; height: number } {
  if (buf.length < 24) {
    fail(`file is only ${buf.length} bytes, too small to be a PNG`);
  }
  for (let i = 0; i < PNG_MAGIC.length; i++) {
    if (buf[i] !== PNG_MAGIC[i]) {
      fail("file does not start with the PNG signature");
    }
  }
  if (buf.toString("ascii", 12, 16) !== "IHDR") {
    fail("first PNG chunk is not IHDR");
  }
  return { width: buf.readUInt32BE(16), height: buf.readUInt32BE(20) };
}

function main(): void {
  const here = dirname(fileURLToPath(import.meta.url));
  const sourcePath = join(here, OUTPUT_NAME);
  if (!existsSync(sourcePath)) {
    fail(`expected image not found next to this script: ${sourcePath}`);
  }

  const source = readFileSync(sourcePath);
  const { width, height } = pngDimensions(source);
  if (width !== EXPECTED_WIDTH || height !== EXPECTED_HEIGHT) {
    fail(`image is ${width}x${height}, expected ${EXPECTED_WIDTH}x${EXPECTED_HEIGHT}`);
  }

  mkdirSync(OUTPUT_DIR, { recursive: true });
  const finalPath = join(OUTPUT_DIR, OUTPUT_NAME);
  const stagingPath = join(OUTPUT_DIR, `.entry-${process.pid}.tmp`);
  writeFileSync(stagingPath, source);
  renameSync(stagingPath, finalPath);

  const published = readFileSync(finalPath);
  const digest = (buf: Buffer): string => createHash("sha256").update(buf).digest("hex");
  const sourceDigest = digest(source);
  if (published.length !== source.length || digest(published) !== sourceDigest) {
    fail("published copy differs from the source image");
  }

  console.log(
    `main: published ${OUTPUT_NAME} (${source.length} bytes, ${width}x${height}) ` +
      `to ${finalPath}, sha256 ${sourceDigest}`,
  );
}

main();
