"""
Agent command - LLM-powered conversational interface.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from pathlib import Path
from typing import Optional

import click

from ..utils import error, execute_shell_command


@click.command()
@click.argument("query", nargs=-1, required=False)
@click.option(
    "--backend",
    type=click.Choice(["openai", "anthropic", "ollama", "auto"], case_sensitive=False),
    default="auto",
    help="LLM backend to use",
)
@click.option("--model", help="Model name (e.g., gpt-4, claude-3-5-sonnet-20241022)")
@click.option("--interactive", "-i", is_flag=True, help="Start interactive REPL mode")
@click.option("--save-conversation", help="Save conversation to file on exit")
@click.option("--load-conversation", help="Resume conversation from file")
@click.option("--path", default=".", help="Repository path")
def agent(
    query: tuple,
    backend: str,
    model: Optional[str],
    interactive: bool,
    save_conversation: Optional[str],
    load_conversation: Optional[str],
    path: str,
):
    """
    🤖 LLM-powered conversational interface for prompt versioning.

    Examples:
        promptvc agent "initialize the project"
        promptvc agent "commit this prompt with message 'improved clarity'"
        promptvc agent --interactive  # Start REPL mode
    """
    try:
        from ...agent import AnthropicBackend, OllamaBackend, OpenAIBackend, PromptVCAgent
    except ImportError:
        error(
            "LLM agent requires additional dependencies\n"
            "Install with: pip install prompt-versioning-cli[agent]"
        )

    try:
        # Initialize backend
        llm_backend = None
        if backend != "auto":
            if backend == "openai":
                llm_backend = OpenAIBackend(model=model or "gpt-4")
            elif backend == "anthropic":
                llm_backend = AnthropicBackend(model=model or "claude-3-5-sonnet-20241022")
            elif backend == "ollama":
                llm_backend = OllamaBackend(model=model or "llama3.2")

        # Load or create agent
        if load_conversation and Path(load_conversation).exists():
            agent_obj = PromptVCAgent.load_conversation(
                Path(load_conversation), backend=llm_backend, repo_path=path
            )
            click.echo(f"✓ Resumed conversation from {load_conversation}")
        else:
            agent_obj = PromptVCAgent(backend=llm_backend, repo_path=path)

        # Show backend info
        backend_name = type(agent_obj.backend).__name__.replace("Backend", "")
        click.echo(f"🤖 Agent active (using {backend_name})\n")

        # Single query mode
        if query:
            user_input = " ".join(query)
            response = agent_obj.process_message(user_input)

            # Display response
            click.echo(response.message)

            # Execute command if present
            if response.command:
                if response.needs_confirmation:
                    click.echo(f"\n⚠️  Execute: {response.command}")
                    if not click.confirm("Proceed?", default=True):
                        click.echo("Cancelled.")
                        return

                click.echo(f"\n▶ Executing: {response.command}")
                execute_shell_command(response.command)

            return

        # Interactive REPL mode
        if interactive or not query:
            _run_interactive_agent(agent_obj, path)

            # Save conversation on exit
            if save_conversation:
                agent_obj.save_conversation(Path(save_conversation))
                click.echo(f"\n✓ Saved conversation to {save_conversation}")

    except RuntimeError as e:
        error(str(e))


def _run_interactive_agent(agent_obj, repo_path: str):
    """Run interactive REPL mode for the agent."""
    click.echo("Interactive mode (type 'exit', 'quit', or press Ctrl+C to exit)\n")

    while True:
        try:
            user_input = click.prompt("You", type=str, prompt_suffix=" → ").strip()

            if user_input.lower() in ["exit", "quit", "bye"]:
                click.echo("Goodbye! 👋")
                break

            if not user_input:
                continue

            # Process message
            response = agent_obj.process_message(user_input)

            # Display response
            click.echo(f"\n🤖 Assistant:\n{response.message}\n")

            # Handle command execution
            if response.command:
                if response.needs_confirmation:
                    if not click.confirm(f"Execute: {response.command}?", default=True):
                        click.echo("Skipped.\n")
                        continue

                click.echo(f"▶ Executing: {response.command}\n")
                execute_shell_command(response.command)
                click.echo()

            if response.error:
                click.echo(f"⚠️  Warning: {response.error}\n", err=True)

        except (KeyboardInterrupt, EOFError):
            click.echo("\nGoodbye! 👋")
            break
        except Exception as e:
            click.echo(f"\n✗ Error: {e}\n", err=True)
