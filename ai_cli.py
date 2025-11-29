#!/usr/bin/env python3
"""
AI CLI - A modern terminal-based LLM interface
"""
import os
import sys
import json
import argparse
import re
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, List
import requests
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.live import Live
from rich.spinner import Spinner
from rich.text import Text
import io

try:
    from PIL import Image
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')
    LATEX_SUPPORT = True
except ImportError:
    LATEX_SUPPORT = False

try:
    import sympy
    from sympy.parsing.latex import parse_latex
    SYMPY_SUPPORT = True
except ImportError:
    SYMPY_SUPPORT = False

try:
    from pylatexenc.latex2text import LatexNodes2Text
    PYLATEXENC_SUPPORT = True
except ImportError:
    PYLATEXENC_SUPPORT = False

try:
    from rich.image import Image
    RICH_IMAGE_SUPPORT = True
except ImportError:
    RICH_IMAGE_SUPPORT = False

# Check for terminal image support
TERM = os.getenv('TERM', '')
KITTY_SUPPORT = 'kitty' in TERM or os.getenv('KITTY_WINDOW_ID')
ITERM_SUPPORT = os.getenv('TERM_PROGRAM') == 'iTerm.app'

# Configuration
CONFIG_DIR = Path.home() / ".config" / "ai-cli"
CONFIG_FILE = CONFIG_DIR / "config.json"
HISTORY_FILE = CONFIG_DIR / "history.json"

class AIClient:
    def __init__(self, api_key: str, model: str = "x-ai/grok-4.1-fast:free"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.console = Console()
        self.conversation_history: List[dict] = []
        
    def get_system_prompt(self) -> str:
        """Generate system prompt with file system context"""
        cwd = os.getcwd()
        try:
            files = os.listdir(cwd)
            files_list = "\n".join(f"- {f}" for f in files[:50])
            if len(files) > 50:
                files_list += f"\n... and {len(files) - 50} more files"
        except Exception as e:
            files_list = f"Error listing files: {e}"
        
        return f"""You are a helpful AI assistant with access to the user's file system.
Current working directory: {cwd}
Files in current directory:
{files_list}

You can help users with:
- Reading and analyzing files (use relative or absolute paths)
- Writing or modifying files
- Answering questions about their code and projects
- General programming and technical assistance

When suggesting file operations, provide clear commands or code snippets.

IMPORTANT: When writing mathematical expressions or formulas, always use LaTeX notation:
- For inline math: use single dollar signs like $x = 2$
- For display math: use double dollar signs like $$E = mc^2$$
Always wrap math in these delimiters so it renders properly."""

    def read_file(self, filepath: str) -> str:
        """Read a file from the filesystem"""
        try:
            path = Path(filepath).expanduser()
            if not path.is_absolute():
                path = Path.cwd() / path
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"
    
    def write_file(self, filepath: str, content: str) -> str:
        """Write content to a file"""
        try:
            path = Path(filepath).expanduser()
            if not path.is_absolute():
                path = Path.cwd() / path
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully wrote to {path}"
        except Exception as e:
            return f"Error writing file: {e}"
    
    def send_message(self, message: str, stream: bool = True) -> str:
        """Send a message to the AI and get response"""
        self.conversation_history.append({
            "role": "user",
            "content": message
        })
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()}
        ] + self.conversation_history
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/ai-cli",
            "X-Title": "AI CLI"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "stream": stream
        }
        
        try:
            if stream:
                return self._stream_response(headers, data)
            else:
                response = requests.post(self.base_url, headers=headers, json=data, timeout=60)
                response.raise_for_status()
                result = response.json()
                assistant_message = result['choices'][0]['message']['content']
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_message
                })
                return assistant_message
        except Exception as e:
            return f"Error communicating with AI: {e}"
    
    def _stream_response(self, headers: dict, data: dict) -> str:
        """Stream response from AI"""
        response = requests.post(
            self.base_url,
            headers=headers,
            json=data,
            stream=True,
            timeout=60
        )
        response.raise_for_status()
        
        full_response = ""
        
        with Live("", console=self.console, refresh_per_second=10, transient=True) as live:
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data_str = line[6:]
                        if data_str == '[DONE]':
                            break
                        try:
                            chunk = json.loads(data_str)
                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                delta = chunk['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                if content:
                                    full_response += content
                                    live.update(Text(full_response))
                        except json.JSONDecodeError:
                            continue
        
        self.conversation_history.append({
            "role": "assistant",
            "content": full_response
        })
        
        return full_response
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def render_latex(self, text: str) -> str:
        """Convert LaTeX math to Unicode text with improved fallback"""
        def unicode_replace(latex: str) -> str:
            """Advanced LaTeX to unicode approximations"""
            result = latex.strip(' {}')
            
            # Greek letters (lower/upper)
            greek = {
                r'\\alpha': 'α', r'\\Alpha': 'Α',
                r'\\beta': 'β', r'\\Beta': 'Β',
                r'\\gamma': 'γ', r'\\Gamma': 'Γ',
                r'\\delta': 'δ', r'\\Delta': 'Δ',
                r'\\epsilon': 'ε', r'\\varepsilon': 'ε', r'\\Epsilon': 'Ε',
                r'\\zeta': 'ζ', r'\\eta': 'η', r'\\theta': 'θ', r'\\vartheta': 'ϑ',
                r'\\iota': 'ι', r'\\kappa': 'κ', r'\\lambda': 'λ', r'\\Lambda': 'Λ',
                r'\\mu': 'μ', r'\\nu': 'ν', r'\\xi': 'ξ', r'\\Xi': 'Ξ',
                r'\\pi': 'π', r'\\Pi': 'Π', r'\\rho': 'ρ', r'\\sigma': 'σ',
                r'\\tau': 'τ', r'\\upsilon': 'υ', r'\\Upsilon': 'Υ',
                r'\\phi': 'φ', r'\\varphi': 'ϕ', r'\\Phi': 'Φ',
                r'\\chi': 'χ', r'\\psi': 'ψ', r'\\Psi': 'Ψ', r'\\omega': 'ω', r'\\Omega': 'Ω',
            }
            for pat, rep in greek.items():
                result = re.sub(pat, rep, result)
            
            # Symbols
            symbols = {
                r'\\infty': '∞', r'\\pm': '±', r'\\mp': '∓',
                r'\\sum': '∑', r'\\prod': '∏', r'\\int': '∫',
                r'\\partial': '∂', r'\\nabla': '∇', r'\\sqrt': '√',
                r'\\approx': '≈', r'\\neq': '≠', r'\\le': '≤', r'\\ge': '≥',
                r'\\times': '×', r'\\div': '÷', r'\\to': '→', r'\\leftarrow': '←',
            }
            for pat, rep in symbols.items():
                result = re.sub(pat, rep, result)
            
            # Fractions
            result = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'\1/\2', result)
            
            # Superscripts/subscripts with braces
            def superscript_digits(match):
                digits = match.group(1)
                return ''.join(chr(0x2070 + int(d)) for d in digits)
            def subscript_digits(match):
                digits = match.group(1)
                return ''.join(chr(0x2080 + int(d)) for d in digits)
            
            result = re.sub(r'\^ *\{ *(\d+) *\}', superscript_digits, result)
            result = re.sub(r'\_ *\{ *(\d+) *\}', subscript_digits, result)
            
            # Plain ^n (no braces)
            result = re.sub(r'\^ *(\d+)', superscript_digits, result)
            result = re.sub(r'\_ *(\d+)', subscript_digits, result)
            
            # Common powers
            result = result.replace('^2', '²').replace('^3', '³').replace('^-1', '⁻¹')
            
            return result

        def replace_math(match):
            latex = match.group(1).strip()
            if PYLATEXENC_SUPPORT:
                try:
                    l2t = LatexNodes2Text()
                    pylatex_result = l2t.latex_to_text(latex)
                    return pylatex_result
                except:
                    pass
            
            converted = unicode_replace(latex)
            # sympy enhancement if parses and better
            try:
                if SYMPY_SUPPORT:
                    expr = parse_latex(latex)
                    sympy_result = sympy.pretty(expr, use_unicode=True, wrap_line=False).replace('\n', ' ')
                    if len(sympy_result) > len(converted) * 1.2:
                        return sympy_result
            except:
                pass
            return converted

        patterns = [
            r'\$\$(.+?)\$\$',
            r'\$([^$\n]+?)\$',
            r'\\\[(.+?)\\\]',
            r'\\\((.+?)\\\)',
        ]
        for pat in patterns:
            text = re.sub(pat, replace_math, text, flags=re.DOTALL)
        return text

    def render_math_to_image(self, latex: str, inline: bool = True) -> Optional[bytes]:
        """Render LaTeX math to PNG image bytes using matplotlib"""
        try:
            fig, ax = plt.subplots(figsize=(5 if inline else 12, 0.6 if inline else 1.2))
            ax.axis('off')
            math_delim = "$" if inline else "$$"
            ax.text(0.5, 0.5, math_delim + latex + math_delim, fontsize=14 if inline else 22,
                    ha='center', va='center', transform=ax.transAxes)
            buf = io.BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.02,
                        transparent=True, dpi=120)
            plt.close(fig)
            buf.seek(0)
            return buf.getvalue()
        except Exception:
            return None

    def render_response(self, text: str) -> None:
        """Render text with LaTeX math rendered as images in supported terminals"""
        console = self.console
        supports_images = KITTY_SUPPORT or ITERM_SUPPORT
        if not LATEX_SUPPORT or not supports_images or not RICH_IMAGE_SUPPORT:
            rendered = self.render_latex(text)
            md = Markdown(rendered)
            console.print(md)
            return

        pos = 0
        patterns = [
            (re.compile(r'(?<!\\)\$\$([^\$]*?)(?<!\\)\$\$', re.DOTALL), False),
            (re.compile(r'(?<!\\)\$([^$\n\r]*?)(?<!\\)\$', re.MULTILINE), True),
            (re.compile(r'\\\[(.+?)\\\]', re.DOTALL), False),
            (re.compile(r'\\\((.+?)\\\)', re.DOTALL), True),
        ]
        text_len = len(text)
        while pos < text_len:
            match = None
            min_start = text_len
            best_is_inline = False
            for pat, is_inline_flag in patterns:
                m = pat.search(text, pos)
                if m and m.start() < min_start:
                    min_start = m.start()
                    match = m
                    best_is_inline = is_inline_flag
            if match is None:
                remaining = text[pos:]
                if remaining.strip():
                    console.print(Markdown(remaining))
                break
            # non-math
            nonmath = text[pos:match.start()]
            if nonmath.strip():
                try:
                    console.print(Markdown(nonmath))
                except:
                    console.print(Text(nonmath))
            # math
            latex = match.group(1).strip()
            img_bytes = self.render_math_to_image(latex, best_is_inline)
            if img_bytes:
                width = 50 if best_is_inline else 80
                img = Image(img_bytes, width=width)
                console.print(img)
            else:
                console.print(f"${latex}$")
            pos = match.end()

class Config:
    @staticmethod
    def load() -> dict:
        """Load configuration from file"""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {}
    
    @staticmethod
    def save(config: dict):
        """Save configuration to file"""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    
    @staticmethod
    def get_api_key() -> Optional[str]:
        """Get API key from config or environment"""
        config = Config.load()
        return config.get('api_key') or os.getenv('OPENROUTER_API_KEY')
    
    @staticmethod
    def set_api_key(api_key: str):
        """Set API key in config"""
        config = Config.load()
        config['api_key'] = api_key
        Config.save(config)

def interactive_mode(client: AIClient):
    """Run in interactive chat mode"""
    console = Console()
    
    console.print(Panel.fit(
        "[bold cyan]AI CLI - Interactive Mode[/bold cyan]\n"
        "Type your messages and press Enter. Commands:\n"
        "  [yellow]/clear[/yellow] - Clear conversation history\n"
        "  [yellow]/exit[/yellow] or [yellow]/quit[/yellow] - Exit\n"
        "  [yellow]/read <file>[/yellow] - Read a file\n"
        "  [yellow]/write <file>[/yellow] - Write to a file (next message is content)",
        border_style="cyan"
    ))
    
    write_mode = None
    
    while True:
        try:
            user_input = Prompt.ask("\n[bold green]You[/bold green]")
            
            if not user_input.strip():
                continue
            
            if user_input.startswith('/'):
                cmd_parts = user_input.split(maxsplit=1)
                cmd = cmd_parts[0].lower()
                
                if cmd in ['/exit', '/quit']:
                    console.print("[yellow]Goodbye![/yellow]")
                    break
                elif cmd == '/clear':
                    client.clear_history()
                    console.print("[yellow]Conversation history cleared.[/yellow]")
                    continue
                elif cmd == '/read' and len(cmd_parts) > 1:
                    filepath = cmd_parts[1]
                    content = client.read_file(filepath)
                    console.print(Panel(content, title=f"[cyan]{filepath}[/cyan]", border_style="blue"))
                    continue
                elif cmd == '/write' and len(cmd_parts) > 1:
                    write_mode = cmd_parts[1]
                    console.print(f"[yellow]Next message will be written to {write_mode}[/yellow]")
                    continue
                else:
                    console.print("[red]Unknown command[/red]")
                    continue
            
            if write_mode:
                result = client.write_file(write_mode, user_input)
                console.print(f"[green]{result}[/green]")
                write_mode = None
                continue
            
            client.console.print("\n[bold cyan]AI:[/bold cyan]")
            
            response = client.send_message(user_input, stream=True)
            
            client.render_response(response)
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Use /exit to quit[/yellow]")
        except EOFError:
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

def main():
    parser = argparse.ArgumentParser(description="AI CLI - Modern terminal-based LLM interface")
    parser.add_argument('prompt', nargs='*', help='Prompt to send to AI')
    parser.add_argument('--setup', action='store_true', help='Setup API key')
    parser.add_argument('--model', default='x-ai/grok-4.1-fast:free', help='Model to use')
    
    args = parser.parse_args()
    console = Console()
    
    if args.setup:
        api_key = Prompt.ask("[cyan]Enter your OpenRouter API key[/cyan]", password=True)
        Config.set_api_key(api_key)
        console.print("[green]API key saved successfully![/green]")
        return
    
    api_key = Config.get_api_key()
    if not api_key:
        console.print("[red]No API key found![/red]")
        console.print("Set your API key using one of these methods:")
        console.print("1. Run: [cyan]ai --setup[/cyan]")
        console.print("2. Set environment variable: [cyan]export OPENROUTER_API_KEY='your-key'[/cyan]")
        console.print("\nGet your API key at: [blue]https://openrouter.ai/keys[/blue]")
        sys.exit(1)
    
    client = AIClient(api_key, model=args.model)
    
    if args.prompt:
        prompt = ' '.join(args.prompt)
        client.console.print(f"[bold green]You:[/bold green] {prompt}\n")
        client.console.print("[bold cyan]AI:[/bold cyan]")
        
        response = client.send_message(prompt, stream=True)
        
        client.render_response(response)
    else:
        interactive_mode(client)

if __name__ == "__main__":
    main()
