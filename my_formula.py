"""YOUR MATHEMATICAL CANVAS.

Change the NumPy formulas inside rgb(x, y), save, and run:
    python render_my_formula.py

x, y are grids of pixel coordinates from -1.15 to 1.15. Any NumPy
functions can be used. Return three arrays for red, green, blue (0..255).
"""
import numpy as np


def rgb(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    # Try changing 11 to 7, 13, 17... to redesign the flower's petals.
    r = np.sqrt(x*x + y*y)
    theta = np.arctan2(y, x)
    petals = np.cos(11*theta + 3.8*r)
    edge = 0.68 + 0.17*petals + 0.04*np.cos(33*theta - 6*r)
    bloom = np.exp(-((r - edge)/0.075)**2)
    folds = (0.65 + 0.35*np.sin(51*r + 10*theta + 2*np.sin(11*theta)))
    strands = np.exp(-((r - 0.52 - 0.12*np.sin(11*theta+8*r)) / 0.11)**2)
    heart = np.exp(-(r/0.19)**2) * (0.7 + .3*np.cos(25*r))
    glow = bloom * folds + 0.45*strands + .48*heart
    aura = np.exp(-((r-.60)/.40)**2) * .10

    # THESE THREE EQUATIONS CONTROL THE PIXEL COLORS.
    red = 5 + 238*glow + 115*aura
    green = 3 + 115*glow + 45*aura + 85*heart
    blue = 18 + 225*glow*(.55+.45*np.cos(theta*3+2*r)) + 145*aura
    return red, green, blue
