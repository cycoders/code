import click
import yaml
from pathlib import Path
from rich import print, console
from rich.table import Table
from rich.prompt import FloatPrompt, Confirm
from rich.panel import Panel

from .power_analysis import compute_power_analysis
from .visualizer import power_curve_plot

console = console.Console()

@click.group()
@click.version_option(__version__)
def cli():
    """Statistical Power Analyzer: Plan A/B tests with precise power calculations."""
    pass

@cli.command()
@click.option('--test-type', 'test_type',
              type=click.Choice(['ttest-ind', 'ttest-paired', 'prop-ztest', 'anova-2']),
              default='ttest-ind', metavar='TYPE',
              help='Statistical test type')
@click.option('--effect-size', type=float, metavar='D',
              help='Cohen\'s d or effect size')
@click.option('--nobs', type=float, metavar='N',
              help='Sample size per group (nobs1)')
@click.option('--power', type=float, metavar='PWR',
              help='Desired power (0-1)')
@click.option('--alpha', type=float, default=0.05, metavar='ALPHA',
              help='Significance level (default: 0.05)')
@click.option('--ratio', type=float, default=1.0, metavar='R',
              help='Group size ratio nobs2/nobs1 (default: 1.0)')
@click.option('--alternative', type=click.Choice(['two-sided', 'larger', 'smaller']),
              default='two-sided', help='Test alternative')
@click.option('--prop1', type=float, metavar='P1',
              help='Baseline proportion (for prop-ztest)')
@click.option('--prop2', type=float, metavar='P2',
              help='Variant proportion (for prop-ztest)')
@click.option('--solve-for', type=click.Choice(['power', 'nobs', 'effect_size']),
              default='power', help='Parameter to solve for')
@click.option('--config', type=click.File('r'), metavar='YAML',
              help='YAML config file')
@click.option('--interactive', is_flag=True, help='Interactive prompts')
@click.option('--output', type=click.Choice(['table', 'json']), default='table')
def analyze(test_type, effect_size, nobs, power, alpha, ratio, alternative, prop1, prop2, solve_for, config, interactive, output):
    """Compute power analysis."""
    params = {
        'test_type': test_type,
        'effect_size': effect_size,
        'nobs1': nobs,
        'power': power,
        'alpha': alpha,
        'ratio': ratio,
        'alternative': alternative,
        'prop1': prop1,
        'prop2': prop2,
        'solve_for': solve_for,
    }

    if config:
        cfg = yaml.safe_load(config)
        for k, v in cfg.items():
            if k in params:
                params[k] = v

    if interactive:
        print(Panel("Interactive Power Analysis", style="bold blue"))
        params['test_type'] = click.prompt("Test type", type=click.Choice(['ttest-ind', 'ttest-paired', 'prop-ztest', 'anova-2']), default=test_type)
        if params['test_type'] == 'prop-ztest':
            params['prop1'] = FloatPrompt("Baseline proportion (prop1)", default=0.1)
            params['prop2'] = FloatPrompt("Variant proportion (prop2)", default=0.12)
        else:
            params['effect_size'] = FloatPrompt("Effect size (Cohen's d)", default=0.5)
        params['power'] = FloatPrompt("Target power", default=0.8)
        params['alpha'] = FloatPrompt("Alpha", default=0.05)
        params['ratio'] = FloatPrompt("Group ratio", default=1.0)
        params['solve_for'] = click.prompt("Solve for", type=click.Choice(['power', 'nobs', 'effect_size']), default='nobs')

    try:
        result = compute_power_analysis(**params)
    except ValueError as e:
        console.print(f"[red]Error: {e}", file=console.stderr)
        raise click.Abort()

    if output == 'json':
        import json
        print(json.dumps(result, indent=2))
    else:
        table = Table(title="Power Analysis Results")
        table.add_column("Metric")
        table.add_column("Value")
        for k, v in result.items():
            table.add_row(k.replace('_', ' ').title(), f"{v:.4f}")
        console.print(table)

        if 'mde' in result:
            console.print(f"[bold green]Minimum Detectable Effect (MDE): {result['mde']:.4f}")

@cli.command()
@click.option('--test-type', default='ttest-ind', metavar='TYPE',
              type=click.Choice(['ttest-ind', 'ttest-paired', 'prop-ztest']))
@click.option('--effect-size', type=float, required=True, metavar='D')
@click.option('--alpha', default=0.05)
@click.option('--ratio', default=1.0)
@click.option('--alternative', default='two-sided')
@click.option('--x-vs', type=click.Choice(['nobs', 'effect_size']), default='nobs',
              help='X-axis: sample size or effect size')
@click.option('--output', '-o', required=True, type=click.Path(dir_okay=False, ext=['.png', '.pdf']))
@click.option('--config', type=click.File('r'))
def plot(test_type, effect_size, alpha, ratio, alternative, x_vs, output, config):
    """Generate power curve plot."""
    if config:
        cfg = yaml.safe_load(config)
        effect_size = cfg.get('effect_size', effect_size)
        alpha = cfg.get('alpha', alpha)
    console.print(f"Generating [bold]{output}[/bold]...")
    power_curve_plot(test_type, effect_size, alpha, ratio, alternative, x_vs, str(output))
    console.print("[green]✓ Plot saved!")

if __name__ == '__main__':
    cli()
