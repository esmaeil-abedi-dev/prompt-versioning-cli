/**
 * Prompt Versioning CLI - TypeScript Type Definitions
 * 
 * Core type definitions for TypeScript bindings.
 * 
 * Copyright (c) 2025 Prompt Versioning Contributors
 * Licensed under MIT License
 */

/**
 * Prompt data structure matching Python Prompt model.
 */
export interface PromptData {
  system?: string;
  user_template?: string;
  assistant_prefix?: string;
  temperature?: number;
  max_tokens?: number;
  top_p?: number;
  frequency_penalty?: number;
  presence_penalty?: number;
  stop_sequences?: string[];
  [key: string]: any; // Allow additional fields
}

/**
 * Commit metadata.
 */
export interface Commit {
  hash: string;
  parentHash?: string;
  message: string;
  author: string;
  timestamp: Date;
  promptHash: string;
  tags: string[];
}

/**
 * Version combining commit and prompt.
 */
export interface Version {
  commit: Commit;
  prompt: PromptData;
}

/**
 * Experiment tag.
 */
export interface Tag {
  name: string;
  commitHash: string;
  metadata: Record<string, any>;
  createdAt: Date;
}

/**
 * LLM backend types.
 */
export type LLMBackend = 'openai' | 'anthropic' | 'ollama' | 'auto';

/**
 * Agent response.
 */
export interface AgentResponse {
  message: string;
  command?: string;
  commandArgs?: Record<string, any>;
  needsConfirmation?: boolean;
  error?: string;
}

/**
 * Agent configuration.
 */
export interface AgentConfig {
  backend?: LLMBackend;
  model?: string;
  repoPath?: string;
  conversationFile?: string;
}

/**
 * Diff result.
 */
export interface DiffResult {
  hasChanges: boolean;
  summary: string;
  changes: Array<{
    field: string;
    type: 'added' | 'removed' | 'modified';
    oldValue: any;
    newValue: any;
  }>;
}
