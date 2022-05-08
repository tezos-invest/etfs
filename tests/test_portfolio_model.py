import pytest
import pandas as pd
from pools.portfolio import RebalancedPortfolioModel


@pytest.fixture(scope='session')
def full_history(resources):
    return pd.read_pickle(resources / 'full-history.gz').rename(columns={'tag': 'token'})


def test_evaluation(full_history: pd.DataFrame):
    model = RebalancedPortfolioModel(full_history)

    emulation_result = model.emulate({
        'KT1PnUZCp3u2KzWr93pn4DD7HAJnm3rWVrgn:0':50,
        'KT1CS2xKGHNPTauSh5Re4qE3N9PCfG5u4dPx:0':20,
        'KT1K9gCRgaLRFKTErYt1wVxA3Frb9FjasjTV:null':10,
        'KT1K4jn23GonEmZot3pMGth7unnzZ6EaMVjY:0':10,
        'KT1LN4LPSqTMS7Sd2CJw4bbDGRkMv2t68Fy9:null':10,
    })
    print(emulation_result)
