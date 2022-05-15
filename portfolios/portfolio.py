import numpy as np
import pandas as pd
from optimization.mocma import Optimizer, is_pareto_efficient
import json
import logging



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
            if price > 0:
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

        need_rebalance = rebalance_day is None or (day - rebalance_day).days > self.rebalance_period

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
                'price': total,
            })
            emulation_result['rebalance-day'] = day

            return True

        return False


def volatility(day_prices, full_period_len=252):
    """
    https://www.macroption.com/historical-volatility-calculation/
    https://dynamiproject.files.wordpress.com/2016/01/measuring_historic_volatility.pdf

    :param day_prices: отсортированные по дням дневные close цены
    :param period_len:
    :param full_period_len:

    """
    # sigma = np.sqrt(365) * series['close'].std()
    returns = np.log(day_prices[1:] / day_prices[:-1])
    daily_std = np.std(returns)

    # annualized daily standard deviation
    sigma = daily_std * full_period_len ** 0.5

    return sigma


class MarkovitzOptimization:
    def __init__(self, tokens_data: pd.DataFrame, rebalance_period=1, num_steps=10, population_size=10, num_samples = 10):
        self.portfolio_model = RebalancedPortfolioModel(tokens_data, rebalance_period)
        self.tokens = sorted(self.portfolio_model.tokens_data.token.unique())
        self.num_steps = num_steps
        self.population_size = population_size
        self.num_samples = num_samples

    def evaluate_params(self, arr: np.ndarray):
        normalized_weights = np.round(100 * arr / arr.sum())
        token_weights = dict(zip(self.tokens, map(int, normalized_weights)))
        emulation_result = self.portfolio_model.emulate(token_weights)
        day_total = emulation_result['portfolio-totals']
        totals = np.asarray([d['price'] for d in day_total])

        if len(totals):
            risk = volatility(totals)
            res_return = (totals[-1] - totals[0]) / totals[0]

            res =  {
                'profit_percent': res_return,
                'volatility': -risk,
                'weights': token_weights,
                'result': emulation_result,
            }

            logging.info(json.dumps({k:v for k,v in res.items() if k in {'profit_percent','volatility','weights'}}))
            return res
        else:
            return {
                'profit_percent': -1,
                'volatility': -1,
            }

    def do_optimize(self):
        optimizer = Optimizer(len(self.tokens), 2, self.evaluate_params, population_size=self.population_size)
        optimizer.run(self.num_steps)

        history = optimizer.history()

        points, metrics = zip(*history)

        # drop unefficient points
        points_df = pd.DataFrame(map(lambda x: x.metrics, metrics))

        predicate = points_df['profit_percent'] > 0

        points_df = points_df[predicate].copy()

        pareto_data = points_df[['profit_percent', 'volatility']].values
        # Оставляем только эффективные по парето точки
        pareto_mask = is_pareto_efficient(pareto_data)

        pareto_points = points_df[pareto_mask].copy()
        pareto_points['volatility'] = -pareto_points['volatility']
        if self.num_samples<len(pareto_points):
            pareto_points = pareto_points.sample(self.num_samples)
        pareto_points = pareto_points.sort_values('profit_percent', ascending = True)
        return pareto_points
