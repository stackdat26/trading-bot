# models/markov.py
# =============================================
# Time-Inhomogeneous Markov Chain
#
# Standard Markov: fixed transition probabilities
# Your version: probabilities UPDATE with market conditions
#
# How it works:
# 1. Classify each past candle into a market "state"
# 2. Count how often state X transitions to state Y
# 3. Build a probability matrix from those counts
# 4. Update the matrix as new data comes in
# 5. Use the matrix to boost or reduce your signal confidence
# =============================================

import numpy as np
import pandas as pd
from config.settings import MARKET_STATES


def classify_state(rsi: float, atr: float, avg_atr: float, close: float, ema: float) -> str:
    """
    Classifies the current market into one of the defined states.

    Args:
        rsi:     Current RSI value
        atr:     Current ATR value
        avg_atr: Average ATR over recent period (for comparison)
        close:   Current close price
        ema:     Current EMA20 value

    Returns:
        A state string from MARKET_STATES
    """
    if rsi > 70:
        return "OVERBOUGHT"
    elif rsi < 30:
        return "OVERSOLD"
    elif atr > avg_atr * 1.5:
        return "HIGH_VOL"
    elif close > ema and 40 <= rsi <= 60:
        return "BULLISH"
    elif close < ema and 40 <= rsi <= 60:
        return "BEARISH"
    else:
        return "SIDEWAYS"


def build_transition_matrix(state_sequence: list) -> np.ndarray:
    """
    Builds a transition probability matrix from a sequence of states.

    Example: If we were in BULLISH 10 times, and 7 times the next
    state was also BULLISH and 3 times it was OVERBOUGHT, then:
    P(BULLISH → BULLISH) = 0.7
    P(BULLISH → OVERBOUGHT) = 0.3

    Args:
        state_sequence: List of state strings in chronological order

    Returns:
        2D numpy array of transition probabilities
    """
    n = len(MARKET_STATES)
    state_index = {state: i for i, state in enumerate(MARKET_STATES)}

    # Count matrix — how often did state i transition to state j?
    counts = np.zeros((n, n))

    for i in range(len(state_sequence) - 1):
        from_state = state_sequence[i]
        to_state   = state_sequence[i + 1]

        if from_state in state_index and to_state in state_index:
            row = state_index[from_state]
            col = state_index[to_state]
            counts[row][col] += 1

    # Normalise each row to get probabilities (must sum to 1)
    row_sums = counts.sum(axis=1, keepdims=True)

    # Avoid dividing by zero — if a state never appeared, use uniform distribution
    row_sums[row_sums == 0] = 1
    matrix = counts / row_sums

    return matrix


def get_transition_probability(matrix: np.ndarray, from_state: str, to_state: str) -> float:
    """
    Looks up the probability of moving from one state to another.

    Args:
        matrix:     The transition matrix from build_transition_matrix()
        from_state: The current market state
        to_state:   The state you're predicting (e.g. "BULLISH" for a buy signal)

    Returns:
        Probability as a float between 0 and 1
    """
    state_index = {state: i for i, state in enumerate(MARKET_STATES)}

    if from_state not in state_index or to_state not in state_index:
        return 0.5  # Unknown → neutral

    row = state_index[from_state]
    col = state_index[to_state]

    return matrix[row][col]


def build_state_history(df_15m: pd.DataFrame, avg_atr: float) -> list:
    """
    Classifies every candle in a DataFrame into a market state.
    Used to build the transition matrix.

    Args:
        df_15m:   DataFrame of 15min candles with RSI, ATR, EMA already calculated
        avg_atr:  Average ATR (to compare against current ATR for HIGH_VOL)

    Returns:
        List of state strings in chronological order
    """
    states = []

    for i in range(len(df_15m)):
        row = df_15m.iloc[i]

        # Skip if any value is NaN (happens at start due to rolling calculations)
        if pd.isna(row.get("rsi")) or pd.isna(row.get("atr")) or pd.isna(row.get("ema")):
            continue

        state = classify_state(
            rsi     = row["rsi"],
            atr     = row["atr"],
            avg_atr = avg_atr,
            close   = row["close"],
            ema     = row["ema"],
        )
        states.append(state)

    return states
