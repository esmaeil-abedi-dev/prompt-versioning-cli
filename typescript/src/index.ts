/**
 * Main TypeScript exports for prompt-versioning-cli.
 * 
 * Copyright (c) 2025 Prompt Versioning Contributors
 * Licensed under MIT License
 */

// Re-export everything from bindings (which is now a barrel export)
export {
  PromptRepository,
  PromptVCAgent,
  checkPythonPackage,
  executeCommand,
  parseLogOutput,
  parseAgentResponse,
  parseError,
  type PromptData,
  type Commit,
  type Version,
  type Tag,
  type LLMBackend,
  type AgentResponse,
  type AgentConfig,
  type DiffResult,
} from './bindings';

export { PromptRepository as default } from './bindings';
