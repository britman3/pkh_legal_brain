from typing import Dict

# Pricing per million tokens (USD)
ANTHROPIC_INPUT_PRICE = 3.00
ANTHROPIC_OUTPUT_PRICE = 15.00
OPENAI_INPUT_PRICE = 1.25
OPENAI_OUTPUT_PRICE = 10.00

def calculate_costs(usage_stats: Dict) -> Dict[str, float]:
    """
    Calculate costs in USD based on token usage.
    
    Returns:
        {
            'anthropic_cost': float,
            'openai_cost': float,
            'total_cost': float
        }
    """
    anthropic_input = usage_stats.get("anthropic_input_tokens", 0)
    anthropic_output = usage_stats.get("anthropic_output_tokens", 0)
    openai_input = usage_stats.get("openai_input_tokens", 0)
    openai_output = usage_stats.get("openai_output_tokens", 0)
    
    # Calculate costs (tokens / 1,000,000 * price)
    anthropic_cost = (
        (anthropic_input / 1_000_000 * ANTHROPIC_INPUT_PRICE) +
        (anthropic_output / 1_000_000 * ANTHROPIC_OUTPUT_PRICE)
    )
    
    openai_cost = (
        (openai_input / 1_000_000 * OPENAI_INPUT_PRICE) +
        (openai_output / 1_000_000 * OPENAI_OUTPUT_PRICE)
    )
    
    total_cost = anthropic_cost + openai_cost
    
    return {
        'anthropic_cost': round(anthropic_cost, 6),
        'openai_cost': round(openai_cost, 6),
        'total_cost': round(total_cost, 6)
    }
