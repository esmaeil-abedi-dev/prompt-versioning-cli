/**
 * Prompt Versioning CLI - Agent Class
 * 
 * LLM-powered conversational agent for prompt versioning.
 * Provides natural language interface to promptvc commands.
 * 
 * Copyright (c) 2025 Prompt Versioning Contributors
 * Licensed under MIT License
 */

import { spawn } from 'child_process';
import { executeCommand } from './executor';
import { parseAgentResponse, parseError } from './response-parser';
import { AgentConfig, AgentResponse } from './types';

/**
 * LLM-powered conversational agent for prompt versioning.
 * 
 * Provides natural language interface to promptvc commands.
 */
export class PromptVCAgent {
  constructor(private config: AgentConfig = {}) {
    this.config.repoPath = this.config.repoPath || '.';
    this.config.backend = this.config.backend || 'auto';
  }
  
  /**
   * Process a natural language query.
   * 
   * @param userInput - The natural language query
   * @param options - Query options
   * @returns Parsed agent response with command information
   * @throws Error if backend is not configured properly
   */
  async query(userInput: string, options: {
    interactive?: boolean;
    autoExecute?: boolean;
  } = {}): Promise<AgentResponse> {
    // Validate input
    if (!userInput || userInput.trim().length === 0) {
      throw new Error('User input cannot be empty');
    }
    
    // Build command arguments
    const args = ['agent', userInput.trim(), '--path', this.config.repoPath!];
    
    if (this.config.backend && this.config.backend !== 'auto') {
      args.push('--backend', this.config.backend);
    }
    
    if (this.config.model) {
      args.push('--model', this.config.model);
    }
    
    if (this.config.conversationFile) {
      args.push('--load-conversation', this.config.conversationFile);
    }
    
    if (options.autoExecute) {
      args.push('--auto-execute');
    }
    
    // Execute command and parse response
    try {
      const output = await executeCommand(args);
      const response = parseAgentResponse(output);
      
      // Validate response structure
      if (!response.message && !response.command) {
        throw new Error('Invalid response from agent: no message or command');
      }
      
      return response;
    } catch (error) {
      // Parse error message
      const errorMessage = error instanceof Error ? error.message : String(error);
      const parsedError = parseError(errorMessage);
      
      return {
        message: '',
        error: parsedError,
      };
    }
  }
  
  /**
   * Start interactive REPL mode.
   * 
   * Note: This spawns a new process and blocks. Best used from CLI.
   * 
   * @throws Error if process fails to start or exits with error code
   */
  async startInteractive(): Promise<void> {
    // Build command arguments
    const args = ['agent', '--interactive', '--path', this.config.repoPath!];
    
    if (this.config.backend && this.config.backend !== 'auto') {
      args.push('--backend', this.config.backend);
    }
    
    if (this.config.model) {
      args.push('--model', this.config.model);
    }
    
    if (this.config.conversationFile) {
      args.push('--save-conversation', this.config.conversationFile);
    }
    
    // Execute in interactive mode (doesn't capture output)
    const proc = spawn('promptvc', args, {
      stdio: 'inherit',
    });
    
    return new Promise((resolve, reject) => {
      proc.on('error', (error: Error) => {
        reject(new Error(`Failed to start agent process: ${error.message}`));
      });
      
      proc.on('close', (code: number | null) => {
        if (code === 0 || code === null) {
          resolve();
        } else {
          reject(new Error(`Agent exited with code ${code}`));
        }
      });
    });
  }
  
  /**
   * Save conversation to file.
   * 
   * @param filepath - Path to save conversation file
   * @throws Error if filepath is invalid
   */
  async saveConversation(filepath: string): Promise<void> {
    if (!filepath || filepath.trim().length === 0) {
      throw new Error('Filepath cannot be empty');
    }
    
    // Validate file extension
    if (!filepath.endsWith('.json')) {
      throw new Error('Conversation file must have .json extension');
    }
    
    this.config.conversationFile = filepath.trim();
  }
  
  /**
   * Load conversation from file.
   * 
   * @param filepath - Path to conversation file
   * @param config - Additional agent configuration
   * @returns New PromptVCAgent instance with loaded conversation
   * @throws Error if filepath is invalid or file doesn't exist
   */
  static async loadConversation(
    filepath: string,
    config: Partial<AgentConfig> = {}
  ): Promise<PromptVCAgent> {
    if (!filepath || filepath.trim().length === 0) {
      throw new Error('Filepath cannot be empty');
    }
    
    // Validate file extension
    if (!filepath.endsWith('.json')) {
      throw new Error('Conversation file must have .json extension');
    }
    
    // Check if file exists
    try {
      const fs = await import('fs/promises');
      await fs.access(filepath.trim());
    } catch (error) {
      throw new Error(`Conversation file not found: ${filepath}`);
    }
    
    return new PromptVCAgent({
      ...config,
      conversationFile: filepath.trim(),
    });
  }
}
