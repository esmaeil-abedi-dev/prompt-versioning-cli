/**
 * Prompt Versioning CLI - TypeScript Bindings
 * 
 * Provides TypeScript/Node.js bindings to the Python prompt versioning library.
 * Uses child_process to spawn Python CLI and parse output.
 * 
 * Copyright (c) 2025 Prompt Versioning Contributors
 * Licensed under MIT License
 */

// Re-export all types
export type {
  PromptData,
  Commit,
  Version,
  Tag,
  LLMBackend,
  AgentResponse,
  AgentConfig,
  DiffResult,
} from './types';

// Re-export executor utilities
export { executeCommand, checkPythonPackage } from './executor';

// Re-export parsers
export { parseLogOutput } from './parsers';
export { parseAgentResponse, parseError } from './response-parser';

// Re-export main classes
export { PromptRepository } from './repository';
export { PromptVCAgent } from './agent';

// Default export
export { PromptRepository as default } from './repository';
