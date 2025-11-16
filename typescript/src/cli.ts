#!/usr/bin/env node

/**
 * Node.js CLI wrapper for prompt-versioning-cli.
 * 
 * This simply spawns the Python CLI, providing a seamless experience
 * for Node.js users who have installed via npm.
 * 
 * Copyright (c) 2025 Prompt Versioning Contributors
 * Licensed under MIT License
 */

import { spawn } from 'child_process';

// Pass all arguments to Python CLI
const proc = spawn('promptvc', process.argv.slice(2), {
  stdio: 'inherit',
});

proc.on('exit', (code) => {
  process.exit(code || 0);
});
