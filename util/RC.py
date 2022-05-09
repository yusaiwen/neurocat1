import click

from rich.highlighter import RegexHighlighter
from rich.panel import Panel
from rich.table import Table
from rich.theme import Theme
from rich.color import Color
from rich.text import Text
from rich.console import Console

from typing import TYPE_CHECKING, List, NoReturn, Optional, Tuple

def blend_text(
    message: str, color1: Tuple[int, int, int], color2: Tuple[int, int, int]
) -> Text:
    """Blend text from one color to another."""
    text = Text(message)
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    dr = r2 - r1
    dg = g2 - g1
    db = b2 - b1
    size = len(text)
    for index in range(size):
        blend = index / size
        color = f"#{int(r1 + dr * blend):2X}{int(g1 + dg * blend):2X}{int(b1 + db * blend):2X}"
        text.stylize(color, index, index + 1)
    return text

class RichCommand(click.Command):
    """Override Clicks help with a Richer version."""

    def format_help(self, ctx, formatter):
        class OptionHighlighter(RegexHighlighter):
            highlights = [
                r"(?P<switch>\-\w)",
                r"(?P<option>\-\-[\w\-]+)",
            ]

        highlighter = OptionHighlighter()

        console = Console(
            theme=Theme(
                {
                    "option": "bold cyan",
                    "switch": "bold green",
                }
            ),
            highlighter=highlighter,
        )

        console.print(
            f"[b]{NAME}[/b] [magenta]v{VERSION}[/] {MEME}\n\n[dim]{ACCOUNT}.\n",
            justify="center",
        )

        console.print(
            f"Usage: [b]{COMMAND_NAME}[/b] [b][OPTIONS][/] \n"
        )

        options_table = Table(highlight=True, box=None, show_header=False)
        
        for param in self.get_params(ctx)[0:]:
            if len(param.opts) == 2:
                opt1 = highlighter(param.opts[1])
                opt2 = highlighter(param.opts[0])
            else:
                opt2 = highlighter(param.opts[0])
                opt1 = Text("")

            if type(param.type) == click.types.Choice:
                opt2 += Text(" "+"|".join(param.type.to_info_dict().get('choices')), style="bold yellow")

            options = Text(" ".join(reversed(param.opts)))
            help_record = param.get_help_record(ctx)
            if help_record is None:
                help = ""
            else:
                help = Text.from_markup(param.get_help_record(ctx)[-1], emoji=False)
                if param.show_default:
                    help += Text(f"Default: {param.default}", style="dim")
                

            if param.metavar:
                options += f" {param.metavar}"

            
            #     options += f" {param.default}"
                    

            options_table.add_row(opt1, opt2, highlighter(help))

        console.print(
            Panel(
                options_table, border_style="dim", title="Options", title_align="left"
            )
        )

        console.print(
            blend_text(
                "🇨🇳  Made by Seven Yu with ♥\n🏠 yusaisai.top\n💌 yusaiwen@mail.bnu.edu.cn",
                Color.parse("#b169dd").triplet,
                Color.parse("#542c91").triplet,
            ),
            justify="left",
            style="bold",
        )