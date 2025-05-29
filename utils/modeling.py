import pandas as pd
from scipy.optimize import curve_fit
import numpy as np

def piecewise_linear(t, t1, t2, t3, y0, s1, s2):
    """
    Piecewise linear viral kinetics:
    y = y0 (baseline)
      + s1 * (t - t1) if t1 < t < t2 (rise)
      + s2 * (t - t2) if t2 < t < t3 (fall)
      + 0 otherwise
    All lines are connected.
    """
    y = np.full_like(t, y0)
    y += np.where(t >= t1, s1 * (np.minimum(t, t2) - t1), 0)
    y += np.where(t >= t2, s2 * (np.minimum(t, t3) - t2), 0)
    return y


def fit_piecewise(df_person):
    t = df_person["TimeDays"].values
    y = df_person["Log10VL"].values

    # Reasonable initial guesses
    t1_init = np.percentile(t, 10)
    t2_init = np.percentile(t, 40)
    t3_init = np.percentile(t, 80)
    y0_init = np.min(y)
    s1_init = 1.0
    s2_init = -1.0

    p0 = [t1_init, t2_init, t3_init, y0_init, s1_init, s2_init]

    try:
        popt, _ = curve_fit(piecewise_linear, t, y, p0=p0)
        return popt
    except RuntimeError:
        return None