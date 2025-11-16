/**
 * Prompt Versioning CLI - Repository Class
 * 
 * Main class for interacting with prompt repositories.
 * 
 * Copyright (c) 2025 Prompt Versioning Contributors
 * Licensed under MIT License
 */

import { executeCommand } from './executor';
import { parseLogOutput } from './parsers';
import { Commit, PromptData, Tag, Version } from './types';

/**
 * Main PromptRepository class - mirrors Python API.
 */
export class PromptRepository {
  constructor(private repoPath: string = '.') {}
  
  /**
   * Initialize a new prompt repository.
   */
  static async init(repoPath: string = '.'): Promise<PromptRepository> {
    await executeCommand(['init', '--path', repoPath]);
    return new PromptRepository(repoPath);
  }
  
  /**
   * Create a new commit.
   * 
   * @param message - Commit message
   * @param promptData - Prompt data to commit
   * @param author - Author name (defaults to 'system')
   * @returns Commit metadata
   * @throws Error if commit fails or data is invalid
   */
  async commit(
    message: string,
    promptData: PromptData,
    author: string = 'system'
  ): Promise<Commit> {
    // Validate inputs
    if (!message || message.trim().length === 0) {
      throw new Error('Commit message cannot be empty');
    }
    
    if (!promptData || Object.keys(promptData).length === 0) {
      throw new Error('Prompt data cannot be empty');
    }
    
    if (!author || author.trim().length === 0) {
      throw new Error('Author name cannot be empty');
    }
    
    // Write prompt data to temporary file
    const fs = await import('fs/promises');
    const os = await import('os');
    const path = await import('path');
    
    const tmpFile = path.join(os.tmpdir(), `prompt-${Date.now()}-${Math.random().toString(36).substring(7)}.json`);
    
    try {
      // Validate JSON serialization
      const jsonData = JSON.stringify(promptData, null, 2);
      await fs.writeFile(tmpFile, jsonData, 'utf-8');
      
      // Execute commit command
      const output = await executeCommand([
        'commit',
        '-m', message.trim(),
        '-f', tmpFile,
        '--author', author.trim(),
        '--path', this.repoPath,
      ]);
      
      // Parse output to extract commit hash
      // Format: [main abc123d] Message
      const match = output.match(/\[main\s+([a-f0-9]+)\]/);
      if (!match || !match[1]) {
        throw new Error('Failed to parse commit hash from output');
      }
      
      const hash = match[1];
      
      return {
        hash,
        message: message.trim(),
        author: author.trim(),
        timestamp: new Date(),
        promptHash: '',
        tags: [],
      };
    } catch (error) {
      // Re-throw with better error message
      if (error instanceof Error) {
        throw new Error(`Commit failed: ${error.message}`);
      }
      throw error;
    } finally {
      // Always clean up temp file
      try {
        await fs.unlink(tmpFile);
      } catch (cleanupError) {
        // Ignore cleanup errors
      }
    }
  }
  
  /**
   * Get commit history.
   * 
   * @param maxCount - Maximum number of commits to return
   * @returns Array of versions with commit and prompt data
   * @throws Error if command fails
   */
  async log(maxCount?: number): Promise<Version[]> {
    const args = ['log', '--path', this.repoPath];
    
    if (maxCount !== undefined) {
      if (maxCount <= 0) {
        throw new Error('maxCount must be greater than 0');
      }
      args.push('--max-count', maxCount.toString());
    }
    
    try {
      const output = await executeCommand(args);
      return parseLogOutput(output);
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to get log: ${error.message}`);
      }
      throw error;
    }
  }
  
  /**
   * Compare two commits.
   * 
   * @param commit1 - First commit hash or reference
   * @param commit2 - Second commit hash or reference
   * @returns Diff output
   * @throws Error if commits are invalid or command fails
   */
  async diff(commit1: string, commit2: string): Promise<string> {
    // Validate inputs
    if (!commit1 || commit1.trim().length === 0) {
      throw new Error('commit1 cannot be empty');
    }
    
    if (!commit2 || commit2.trim().length === 0) {
      throw new Error('commit2 cannot be empty');
    }
    
    try {
      const output = await executeCommand([
        'diff',
        commit1.trim(),
        commit2.trim(),
        '--path', this.repoPath,
      ]);
      return output;
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to diff commits: ${error.message}`);
      }
      throw error;
    }
  }
  
  /**
   * Checkout a specific commit.
   * 
   * @param commitRef - Commit hash or reference to checkout
   * @returns Version information
   * @throws Error if commit reference is invalid or command fails
   */
  async checkout(commitRef: string): Promise<Version> {
    // Validate input
    if (!commitRef || commitRef.trim().length === 0) {
      throw new Error('Commit reference cannot be empty');
    }
    
    try {
      await executeCommand([
        'checkout',
        commitRef.trim(),
        '--path', this.repoPath,
      ]);
      
      // Return a placeholder version
      // In production, should parse output for full data
      return {
        commit: {
          hash: commitRef.trim(),
          message: '',
          author: 'system',
          timestamp: new Date(),
          promptHash: '',
          tags: [],
        },
        prompt: {},
      };
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to checkout ${commitRef}: ${error.message}`);
      }
      throw error;
    }
  }
  
  /**
   * Create an experiment tag.
   * 
   * @param name - Tag name
   * @param metadata - Optional metadata to attach to tag
   * @param commitRef - Optional commit reference (defaults to HEAD)
   * @returns Tag information
   * @throws Error if tag name is invalid or command fails
   */
  async tag(
    name: string,
    metadata?: Record<string, any>,
    commitRef?: string
  ): Promise<Tag> {
    // Validate input
    if (!name || name.trim().length === 0) {
      throw new Error('Tag name cannot be empty');
    }
    
    // Validate tag name format
    if (!/^[a-zA-Z0-9_-]+$/.test(name.trim())) {
      throw new Error('Tag name can only contain alphanumeric characters, hyphens, and underscores');
    }
    
    const args = ['tag', name.trim(), '--path', this.repoPath];
    
    if (commitRef) {
      if (commitRef.trim().length === 0) {
        throw new Error('Commit reference cannot be empty');
      }
      args.push('--commit', commitRef.trim());
    }
    
    if (metadata) {
      try {
        args.push('--metadata', JSON.stringify(metadata));
      } catch (error) {
        throw new Error('Failed to serialize metadata to JSON');
      }
    }
    
    try {
      await executeCommand(args);
      
      return {
        name: name.trim(),
        commitHash: commitRef?.trim() || '',
        metadata: metadata || {},
        createdAt: new Date(),
      };
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to create tag: ${error.message}`);
      }
      throw error;
    }
  }
  
  /**
   * Generate audit log.
   * 
   * @param format - Output format ('json' or 'csv')
   * @returns Formatted audit log
   * @throws Error if format is invalid or command fails
   */
  async auditLog(format: 'json' | 'csv' = 'json'): Promise<string> {
    if (format !== 'json' && format !== 'csv') {
      throw new Error('Format must be either "json" or "csv"');
    }
    
    try {
      const output = await executeCommand([
        'audit',
        '--format', format,
        '--path', this.repoPath,
      ]);
      return output;
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to generate audit log: ${error.message}`);
      }
      throw error;
    }
  }
  
  /**
   * Get repository status.
   * 
   * @returns Repository status information
   * @throws Error if command fails
   */
  async status(): Promise<string> {
    try {
      const output = await executeCommand([
        'status',
        '--path', this.repoPath,
      ]);
      return output;
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to get status: ${error.message}`);
      }
      throw error;
    }
  }
  
  /**
   * List all tags.
   * 
   * @returns Array of tag names
   * @throws Error if command fails
   */
  async listTags(): Promise<string[]> {
    try {
      const output = await executeCommand([
        'tags',
        '--path', this.repoPath,
      ]);
      
      // Parse tag names from output
      const lines = output.split('\n').filter(l => l.trim());
      return lines.map(line => line.split('->')[0].trim());
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to list tags: ${error.message}`);
      }
      throw error;
    }
  }
}
