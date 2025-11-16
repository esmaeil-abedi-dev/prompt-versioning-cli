/**
 * Prompt Versioning CLI - Response Parser
 * 
 * Parses agent responses from CLI output.
 * 
 * Copyright (c) 2025 Prompt Versioning Contributors
 * Licensed under MIT License
 */

import { AgentResponse } from './types';

/**
 * Parse agent response from CLI output.
 * 
 * Expected format:
 * ```
 * MESSAGE: <agent message>
 * COMMAND: <command name>
 * ARGS: <json args>
 * NEEDS_CONFIRMATION: true/false
 * ```
 */
export function parseAgentResponse(output: string): AgentResponse {
  const response: AgentResponse = {
    message: '',
  };
  
  const lines = output.split('\n');
  let currentSection: 'message' | 'command' | 'args' | null = null;
  const messageLines: string[] = [];
  
  for (const line of lines) {
    const trimmed = line.trim();
    
    // Check for section markers
    if (trimmed.startsWith('MESSAGE:')) {
      currentSection = 'message';
      const content = trimmed.substring(8).trim();
      if (content) {
        messageLines.push(content);
      }
      continue;
    }
    
    if (trimmed.startsWith('COMMAND:')) {
      currentSection = 'command';
      response.command = trimmed.substring(8).trim();
      continue;
    }
    
    if (trimmed.startsWith('ARGS:')) {
      currentSection = 'args';
      const argsContent = trimmed.substring(5).trim();
      try {
        response.commandArgs = JSON.parse(argsContent);
      } catch (e) {
        // If JSON parse fails, store as string
        response.commandArgs = { raw: argsContent };
      }
      continue;
    }
    
    if (trimmed.startsWith('NEEDS_CONFIRMATION:')) {
      response.needsConfirmation = trimmed.substring(19).trim().toLowerCase() === 'true';
      currentSection = null;
      continue;
    }
    
    // Accumulate lines for current section
    if (currentSection === 'message' && trimmed) {
      messageLines.push(trimmed);
    }
  }
  
  // If no structured format found, treat entire output as message
  if (messageLines.length === 0 && !response.command) {
    response.message = output.trim();
  } else {
    response.message = messageLines.join('\n');
  }
  
  return response;
}

/**
 * Parse error from CLI stderr output.
 */
export function parseError(stderr: string): string {
  // Extract meaningful error message
  const lines = stderr.split('\n').filter(l => l.trim());
  
  // Look for common error patterns
  for (const line of lines) {
    if (line.includes('Error:')) {
      return line.substring(line.indexOf('Error:') + 6).trim();
    }
    if (line.includes('error:')) {
      return line.substring(line.indexOf('error:') + 6).trim();
    }
    if (line.includes('Exception:')) {
      return line.substring(line.indexOf('Exception:') + 10).trim();
    }
  }
  
  // Return first non-empty line if no pattern matches
  return lines[0] || stderr;
}
