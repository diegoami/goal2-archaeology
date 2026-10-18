#!/usr/bin/env node
// #262 (from goal2 PR 178): the OpenCode 2 operand guard's dependencies, byte for byte, offline. It never
// installs or fetches; set them up once per checkout with
//   npm ci --prefix tools/harness/opencode-guard --ignore-scripts --no-audit --no-fund
import { verifyGuardDependencies } from './lib/opencode-guard.mjs';
try {
  const dependencies = verifyGuardDependencies();
  console.log(`PASS trusted guard dependencies: ${Object.keys(dependencies).length} exact file hashes`);
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
