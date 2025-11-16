/**
 * Prompt Versioning CLI - Command Executor
 * 
 * Handles execution of Python CLI commands via child_process.
 * 
 * Copyright (c) 2025 Prompt Versioning Contributors
 * Licensed under MIT License
 */

import { spawn } from 'child_process';
import { promisify } from 'util';
import { exec as execCallback } from 'child_process';

const exec = promisify(execCallback);

/**
 * Execute a promptvc command and return parsed output.
 */
export async function executeCommand(args: string[]): Promise<string> {
  return new Promise((resolve, reject) => {
    const proc = spawn('promptvc', args);
    
    let stdout = '';
    let stderr = '';
    
    proc.stdout.on('data', (data) => {
      stdout += data.toString();
    });
    
    proc.stderr.on('data', (data) => {
      stderr += data.toString();
    });
    
    proc.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(stderr || `Command failed with code ${code}`));
      } else {
        resolve(stdout.trim());
      }
    });
  });
}

/**
 * Check if Python package is installed.
 */
export async function checkPythonPackage(): Promise<boolean> {
  try {
    await exec('promptvc --version');
    return true;
  } catch {
    return false;
  }
}
