# Example: Support Bot Prompt

This example demonstrates using prompt versioning for a customer support chatbot.

## Setup

```bash
# Initialize repository
promptvc init

# Create initial prompt
cat > support-bot.yaml << 'EOF'
system: "You are a friendly customer support agent for TechCorp."
user_template: "Customer: {customer_name}\nIssue: {issue}"
temperature: 0.7
max_tokens: 500
EOF

# Commit first version
promptvc commit -m "Initial support bot prompt" -f support-bot.yaml
```

## Iteration 1: More Empathetic

```bash
# Update prompt to be more empathetic
cat > support-bot.yaml << 'EOF'
system: "You are a warm, empathetic customer support agent for TechCorp. Always acknowledge the customer's feelings."
user_template: "Customer: {customer_name}\nIssue: {issue}"
temperature: 0.7
max_tokens: 500
EOF

# Commit changes
promptvc commit -m "Made tone more empathetic" -f support-bot.yaml

# View differences
promptvc diff HEAD~1 HEAD
```

## Iteration 2: Add Context

```bash
# Add more context fields
cat > support-bot.yaml << 'EOF'
system: "You are a warm, empathetic customer support agent for TechCorp. Always acknowledge the customer's feelings."
user_template: |
  Customer: {customer_name}
  Account Tier: {tier}
  Issue: {issue}
  Previous Interactions: {history}
temperature: 0.7
max_tokens: 800
EOF

# Commit
promptvc commit -m "Added context fields and increased max_tokens" -f support-bot.yaml
```

## A/B Testing

```bash
# Tag baseline version
promptvc tag experiment-baseline --commit HEAD~2 \
  --metadata '{"accuracy": 0.75, "satisfaction": 3.8}'

# Tag empathy version
promptvc tag experiment-empathy --commit HEAD~1 \
  --metadata '{"accuracy": 0.78, "satisfaction": 4.2}'

# Tag current version
promptvc tag experiment-context \
  --metadata '{"accuracy": 0.82, "satisfaction": 4.5}'

# View all experiments
promptvc tags
```

## Rollback

```bash
# If current version has issues, rollback
promptvc checkout HEAD~1

# Verify rollback
promptvc status
```

## View History

```bash
# Full history
promptvc log

# Condensed history
promptvc log --oneline
```

## Generate Audit Report

```bash
# For compliance
promptvc audit --format csv -o support-bot-audit.csv
```

## Python Usage

```python
from prompt_versioning.core import PromptRepository

# Load repository
repo = PromptRepository(".")

# Get current version
current = repo.get_current_version()
print(f"Current prompt: {current.prompt.system}")

# Compare all experiment versions
tags = repo.list_tags()
for tag in tags:
    print(f"{tag.name}: {tag.metadata}")

# Find best performing version
best_tag = max(tags, key=lambda t: t.metadata.get("satisfaction", 0))
print(f"Best version: {best_tag.name}")

# Checkout best version
repo.checkout(best_tag.commit_hash)
```

## TypeScript Usage

```typescript
import { PromptRepository } from 'prompt-versioning-cli';

async function main() {
  const repo = new PromptRepository('.');
  
  // View history
  const versions = await repo.log();
  for (const v of versions) {
    console.log(`${v.commit.hash.slice(0, 7)}: ${v.commit.message}`);
  }
  
  // List experiments
  const tags = await repo.listTags();
  console.log('Experiments:', tags);
  
  // Get status
  const status = await repo.status();
  console.log(status);
}

main();
```
