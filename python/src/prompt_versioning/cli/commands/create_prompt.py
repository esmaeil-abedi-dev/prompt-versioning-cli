"""
Create prompt command - Interactive prompt file creation.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from pathlib import Path
from typing import Optional

import click
import yaml

from ..utils import error, success


@click.command(name="create-prompt")
@click.argument("file_path", required=False)
@click.option("--system", help="System message")
@click.option("--user-template", help="User template message")
@click.option("--temperature", type=float, help="Temperature (0.0-2.0)")
@click.option("--max-tokens", type=int, help="Maximum tokens")
@click.option("--top-p", type=float, help="Top-p sampling (0.0-1.0)")
@click.option("--stop-sequences", help="Stop sequences (comma-separated)")
@click.option(
    "--append",
    is_flag=True,
    help="Append to existing file instead of creating new",
)
def create_prompt(
    file_path: Optional[str],
    system: Optional[str],
    user_template: Optional[str],
    temperature: Optional[float],
    max_tokens: Optional[int],
    top_p: Optional[float],
    stop_sequences: Optional[str],
    append: bool,
):
    """
    🎨 Create or update prompt YAML files interactively.

    This command helps you create properly formatted prompt YAML files.
    Provide a file path as an argument, then answer interactive questions
    for each field. You can also use flags to skip interactive mode.

    Examples:
        promptvc create-prompt prompts/support-bot.yaml
        promptvc create-prompt my-prompt.yaml --system "You are helpful"
        promptvc create-prompt --system "You are helpful" --temperature 0.7
    """
    try:
        # Determine file path
        file = file_path
        if not file:
            file = click.prompt(
                "Prompt file path",
                default="prompts/prompt.yaml",
                type=str,
            )

        file_path_obj = Path(file)

        # Check if file exists and handle append mode
        existing_data = {}
        if file_path_obj.exists():
            if append:
                with open(file_path_obj) as f:
                    existing_data = yaml.safe_load(f) or {}
                click.echo(f"📝 Appending to existing file: {file_path_obj}")
            else:
                if not click.confirm(
                    f"File {file_path_obj} already exists. Overwrite?",
                    default=False,
                ):
                    click.echo("Cancelled.")
                    return

        # Collect prompt data
        prompt_data = existing_data.copy()

        # Check if any flags were provided (non-interactive mode)
        has_flags = any([system, user_template, temperature is not None,
                        max_tokens is not None, top_p is not None, stop_sequences])

        if has_flags:
            # Use provided options only (non-interactive mode)
            if system:
                prompt_data["system"] = system
            if user_template:
                prompt_data["user_template"] = user_template
            if temperature is not None:
                prompt_data["temperature"] = temperature
            if max_tokens is not None:
                prompt_data["max_tokens"] = max_tokens
            if top_p is not None:
                prompt_data["top_p"] = top_p
            if stop_sequences:
                prompt_data["stop_sequences"] = [s.strip() for s in stop_sequences.split(",")]

            if not prompt_data:
                error("No prompt data provided. Provide at least --system or --user-template.")

        else:
            # Interactive mode - ask for each field
            click.echo("\n🎨 Creating prompt file interactively...")
            click.echo("   (Press Enter to skip optional fields)\n")

            # System message
            system_msg = existing_data.get("system", "")
            if system_msg:
                click.echo(f"Current system message: {system_msg[:50]}...")
            system_input = click.prompt(
                "System message",
                default=system_msg,
                type=str,
                show_default=False,
            )
            if system_input:
                prompt_data["system"] = system_input

            # User template
            user_tpl = existing_data.get("user_template", "")
            if user_tpl:
                click.echo(f"Current user template: {user_tpl[:50]}...")
            user_input = click.prompt(
                "User template (use {variable} for placeholders)",
                default=user_tpl,
                type=str,
                show_default=False,
            )
            if user_input:
                prompt_data["user_template"] = user_input

            # Model configuration
            click.echo("\n⚙️  Model Configuration (optional):")

            temp = existing_data.get("temperature")
            if temp is not None:
                temp_input = click.prompt(
                    "Temperature (0.0-2.0)",
                    default=temp,
                    type=float,
                    show_default=True,
                )
            else:
                temp_input = click.prompt(
                    "Temperature (0.0-2.0, press Enter to skip)",
                    default="",
                    type=str,
                    show_default=False,
                )
                temp_input = float(temp_input) if temp_input else None

            if temp_input is not None:
                prompt_data["temperature"] = temp_input

            max_tok = existing_data.get("max_tokens")
            if max_tok is not None:
                tok_input = click.prompt(
                    "Max tokens",
                    default=max_tok,
                    type=int,
                    show_default=True,
                )
            else:
                tok_input = click.prompt(
                    "Max tokens (press Enter to skip)",
                    default="",
                    type=str,
                    show_default=False,
                )
                tok_input = int(tok_input) if tok_input else None

            if tok_input is not None:
                prompt_data["max_tokens"] = tok_input

            top_p_val = existing_data.get("top_p")
            if top_p_val is not None:
                top_p_input = click.prompt(
                    "Top-p (0.0-1.0)",
                    default=top_p_val,
                    type=float,
                    show_default=True,
                )
            else:
                top_p_input = click.prompt(
                    "Top-p (0.0-1.0, press Enter to skip)",
                    default="",
                    type=str,
                    show_default=False,
                )
                top_p_input = float(top_p_input) if top_p_input else None

            if top_p_input is not None:
                prompt_data["top_p"] = top_p_input

            # Stop sequences
            stop_seqs = existing_data.get("stop_sequences", [])
            if stop_seqs and isinstance(stop_seqs, list):
                click.echo(f"Current stop sequences: {', '.join(stop_seqs)}")
            stop_input = click.prompt(
                "Stop sequences (comma-separated, press Enter to skip)",
                default="",
                type=str,
                show_default=False,
            )
            if stop_input:
                prompt_data["stop_sequences"] = [s.strip() for s in stop_input.split(",")]
            elif not stop_seqs:
                # Remove if empty
                prompt_data.pop("stop_sequences", None)

        # Validate minimum required fields
        if "system" not in prompt_data and "user_template" not in prompt_data:
            error("Prompt must have at least 'system' or 'user_template' field")

        # Create directory if it doesn't exist
        file_path_obj.parent.mkdir(parents=True, exist_ok=True)

        # Write to file
        with open(file_path_obj, "w") as f:
            yaml.dump(prompt_data, f, default_flow_style=False, sort_keys=False)

        success(f"Prompt file {'updated' if append else 'created'}: {file_path_obj}")

        # Show preview
        click.echo("\n📄 File contents:")
        click.echo("-" * 50)
        with open(file_path_obj) as f:
            click.echo(f.read())
        click.echo("-" * 50)

    except KeyboardInterrupt:
        click.echo("\n\nCancelled.")
    except Exception as e:
        error(f"Failed to create prompt: {e}")
