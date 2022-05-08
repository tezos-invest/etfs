import pandas as pd


class RebalancedPortfolioModel:
    def __init__(self, tokens_data: pd.DataFrame, rebalance_period=1):
        self.tokens_data = tokens_data
        self.rebalance_period = rebalance_period

    def emulate(self, portfolio_weights: dict):
        if set(portfolio_weights.keys()) != set(self.tokens_data.token.unique()):
            raise ValueError(
                f"can't emulate portfolio: "
                f"required tokens = {portfolio_weights.keys()}, "
                f"dataset tokens = {self.tokens_data.token.unique()}"
            )

        total_weights = sum(portfolio_weights.values())
        portfolio_weights = {k: w / total_weights for k, w in portfolio_weights.items()}

        emulation_state = {
            'portfolio': dict(),
            'rebalance-day': None,
            'current-prices': dict(),
            'start-day': None,
            'day': None,
            'weights': portfolio_weights,
            'portfolio-totals': [],
        }

        for day, token, price in self.tokens_data[['day', 'token', 'close']].values:
            emulation_state['current-prices'][token] = price
            emulation_state['day'] = day
            if len(emulation_state['current-prices']) == len(portfolio_weights):
                rebalanced = self.do_rebalance(emulation_state)
                if rebalanced:
                    emulation_state['start-day'] = emulation_state['start-day'] or day

        return emulation_state

    def do_rebalance(self, emulation_result):
        rebalance_day = emulation_result['rebalance-day']
        day = emulation_result['day']
        portfolio = emulation_result['portfolio']
        current_prices = emulation_result['current-prices']
        weights = emulation_result['weights']

        need_rebalance = rebalance_day is None or day - rebalance_day > self.rebalance_period

        if need_rebalance:
            if portfolio:
                total = sum(v * current_prices[k] for k, v in portfolio.items())
            else:
                total = 1

            new_portfolio = dict()

            for token, token_weight in weights.items():
                token_sum = total * token_weight
                tokens_count = token_sum / current_prices[token]

                new_portfolio[token] = tokens_count

            emulation_result['portfolio'] = new_portfolio

            emulation_result['portfolio-totals'].append({
                'day': day,
                'price':total,
            })

            return True

        return False
