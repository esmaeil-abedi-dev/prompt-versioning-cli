/**
 * Prompt Versioning CLI - Output Parsers
 * 
 * Utilities for parsing CLI command output.
 * 
 * Copyright (c) 2025 Prompt Versioning Contributors
 * Licensed under MIT License
 */

import { Version } from './types';

/**
 * Parse commit output from log command.
 */
export function parseLogOutput(output: string): Version[] {
  const versions: Version[] = [];
  const commitBlocks = output.split('\ncommit ').filter(b => b.trim());
  
  for (const block of commitBlocks) {
    const lines = block.split('\n');
    const hash = lines[0].trim();
    
    let author = 'system';
    let message = '';
    let timestamp = new Date();
    
    for (let i = 1; i < lines.length; i++) {
      const line = lines[i].trim();
      if (line.startsWith('Author:')) {
        author = line.substring(7).trim();
      } else if (line.startsWith('Date:')) {
        timestamp = new Date(line.substring(5).trim());
      } else if (line && !line.startsWith('Tags:')) {
        message = line;
        break;
      }
    }
    
    versions.push({
      commit: {
        hash,
        message,
        author,
        timestamp,
        promptHash: '',
        tags: [],
      },
      prompt: {},
    });
  }
  
  return versions;
}
