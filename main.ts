import { copyFileSync, mkdirSync, statSync } from 'node:fs';
import { join } from 'node:path';

// make.fun bounty gta6-meme-x-01 harness.
// Standard library only, no network. Copies POST.json to the output dir.
// Deterministic: the copied bytes are identical on every run.
const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

mkdirSync(OUTPUT_DIR, { recursive: true });
const src = join(BOT_DIR, 'POST.json');
const dst = join(OUTPUT_DIR, 'POST.json');
copyFileSync(src, dst);
console.log(`[gta6-meme-x-01] copied POST.json (${statSync(dst).size} bytes) -> ${OUTPUT_DIR}`);
