// Entry for the make.fun bounty "Post a GTA 6 meme on X" (gta6-meme-x-01).
//
// The entry is the X post itself: a GTA 6 meme whose first picture is
// meme.png in this repository, posted from the public account @wrjoey.
// This program validates POST.json (which names that post) and copies it
// from the repository into the output directory, where the gate reads it.
// The house reads the post from X and builds the dossier the judge sees;
// nothing this program writes is judged.
//
// Validation mirrors the gate's own post_file / post_url checks, so a
// broken POST.json fails here, loudly, instead of silently shipping an
// entry the gate would refuse as invalid:
//   - POST.json must be at most 16384 bytes (the gate's post_file cap).
//   - It must parse as JSON and be an object with a string "url" key.
//   - The url must be an X post address, https://x.com/<handle>/status/<id>
//     (or the same on twitter.com, with optional www./mobile. prefix, the
//     /i/web/status/<id> form, and any query or fragment after it), with
//     digits only for the id. While the post has not been made yet the
//     placeholder "https://x.com/<handle>/status/<id>" is accepted with a
//     warning, so the entry can still be built and tested before posting;
//     replace it with the real post address before submitting.
// On any failure the program prints the reason, writes nothing to the
// output directory, and exits 1.
//
// Runs on Node 22, standard library only, no network, no wall clock:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

const botDir = process.env.MAKEFUN_BOT_DIR ?? "/bot";
const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

// The gate's post_file cap: POST.json must be a JSON object of at most
// 16384 bytes.
const MAX_POST_JSON_BYTES = 16384;

// The placeholder the kit ships, before the post exists.
const PLACEHOLDER_URL = "https://x.com/<handle>/status/<id>";

// The gate's post_url shape: an X post address on x.com or twitter.com,
// optional www. or mobile. prefix, /status/<digits> or /i/web/status/<digits>,
// digits only for the id, anything after it read past.
const POST_URL_PATTERN =
  /^https:\/\/(?:www\.|mobile\.)?(?:x\.com|twitter\.com)\/(?:i\/web\/status\/\d+|[A-Za-z0-9_]{1,15}\/status\/\d+)(?:[?#].*)?$/;

function fail(message: string): never {
  console.error(`POST.json validation failed: ${message}`);
  process.exit(1);
}

const postPath = join(botDir, "POST.json");

let raw: Buffer;
try {
  raw = readFileSync(postPath);
} catch (error) {
  console.error(
    `Could not read POST.json from ${botDir}: ${(error as Error).message}`,
  );
  process.exit(1);
}

if (raw.length > MAX_POST_JSON_BYTES) {
  fail(
    `POST.json is ${raw.length} bytes, over the gate's ${MAX_POST_JSON_BYTES}-byte cap.`,
  );
}

let parsed: unknown;
try {
  parsed = JSON.parse(raw.toString("utf8"));
} catch (error) {
  fail(`POST.json is not valid JSON: ${(error as Error).message}`);
}

if (parsed === null || typeof parsed !== "object" || Array.isArray(parsed)) {
  fail("POST.json must be a JSON object, not an array or a bare value.");
}

const url = (parsed as Record<string, unknown>).url;
if (typeof url !== "string") {
  fail('POST.json must hold a string "url" key.');
}

if (url === PLACEHOLDER_URL) {
  console.warn(
    "Warning: POST.json still holds the placeholder URL; the gate will refuse it. Replace it with the real post address before submitting.",
  );
} else if (!POST_URL_PATTERN.test(url)) {
  fail(
    `url ${JSON.stringify(url)} is not an X post address (expected https://x.com/<handle>/status/<id>).`,
  );
}

mkdirSync(outputDir, { recursive: true });

try {
  copyFileSync(postPath, join(outputDir, "POST.json"));
} catch (error) {
  console.error(
    `Could not copy POST.json from ${botDir}: ${(error as Error).message}`,
  );
  process.exit(1);
}

console.log(
  url === PLACEHOLDER_URL
    ? "POST.json validated (placeholder URL) and copied to output."
    : `POST.json validated and copied to output: ${url}`,
);
