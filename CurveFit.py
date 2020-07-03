
import numpy as np
from scipy.optimize import curve_fit

# CurveFit:
# contains all functions used to generate a regression line given a set of data points
# functions are called in R2byScalePlot and RegressionPlot class functions.

# Regression line is determined recursively using the curve_fit function from scipy library.
# this value can be changed in the Curve Fit dialog by the user. I set the default to be 1000 based on trial and error.
# this can actually have a significant impact with R^2 values by changing them from undefined / zero all the way to 0.3+
# depending on the scale
maxfev = 1000

# below are the functions for each curve type easy to add new functions or in the future have user defined functions
# -----------------------------Proportional Fit Functions---------------------------------------------------------------
def prop_fit(x, a): return a*x
def prop_data(x, y): return curve_fit(prop_fit, x, y, maxfev=get_maxfev())
# ------------------------------Linear Fit Functions--------------------------------------------------------------------
def linear_fit(x, a, b): return a*x + b
def linear_data(x, y): return curve_fit(linear_fit, x, y, maxfev=get_maxfev())
# ------------------------------Quadratic Fit Functions-----------------------------------------------------------------
def quad_fit(x, a, b, c): return a*x**2 + b*x + c
def quad_data(x, y): return curve_fit(quad_fit, x, y, maxfev=get_maxfev())
# ------------------------------Cubic Fit Functions---------------------------------------------------------------------
def cubic_fit(x, a, b, c, d): return a*x**3 + b*x**2 + c*x + d
def cubic_data(x, y): return curve_fit(cubic_fit, x, y, maxfev=get_maxfev())
# ---------------------------------Quartic Fit Functions----------------------------------------------------------------
def quartic_fit(x, a, b, c, d, e): return a*x**4 + b*x**3 + c*x**2 + d*x + e
def quartic_data(x, y): return curve_fit(quartic_fit, x, y, maxfev=get_maxfev())
# ------------------------------- Quintic Fit Functions-----------------------------------------------------------------
def quintic_fit(x, a, b, c, d, e, f): return a*x**5 + b*x**4 + c*x**3 + d*x**2 + e*x + f
def quintic_data(x, y): return curve_fit(quintic_fit, x, y, maxfev=get_maxfev())
# -------------------------------------Power Fit Functions -----------------------------------------------------------
def power_fit(x, a, b): return a*x**b
def power_data(x, y): return curve_fit(power_fit, x, y, maxfev=get_maxfev())
# -------------------------------------Inverse Fit Functions-------------------------------------------------------
def inverse_fit(x, a): return a/x
def inverse_data(x, y): return curve_fit(inverse_fit, x, y, maxfev=get_maxfev())
# ---------------------------------------Inverse Squared Fit Functions -------------------------------------------------
def insq_fit(x, a): return a/(x**2)
def insq_data(x, y): return curve_fit(insq_fit, x, y, maxfev=get_maxfev())
# ---------------------------------------------Natural Exponent Fit Functions-------------------------------------------
def nexp_fit(x, a, b, c): return a*np.exp(-1*b*x) + c
def nexp_data(x, y): return curve_fit(nexp_fit, x, y, maxfev=get_maxfev())
# ----------------------------------------Natural Log Fit--------------------------------------------------------------
def ln_fit(x, a, b): return a*np.log(b*x)  # second term is base in log()
def ln_data(x, y): return curve_fit(ln_fit, x, y, maxfev=get_maxfev())
# --------------------------------------Base-10 Exponent----------------------------------------------------------------
# doesnt even work smh
def b10exp_fit(x, a, b, c): return a*(10**(b*x)) + c
def b10exp_data(x, y): return curve_fit(b10exp_fit, x, y, maxfev=get_maxfev())
# ---------------------------------------Base-10 Logarithm--------------------------------------------------------------
def b10log_fit(x, a, b): return a*np.log10(b*x)
def b10log_data(x, y): return curve_fit(b10log_fit, x, y, maxfev=get_maxfev())
# ---------------------------------------Inverse Exponent Fit-----------------------------------------------------------
def invexp_fit(x, a, b, c): return a*(1-np.exp(-1*b*x)) + c
def invexp_data(x, y): return curve_fit(invexp_fit, x, y, maxfev=get_maxfev())
# ---------------------------------------Sine Fit------------------------------------------------------------------
def sine_fit(x, a, b, c, d): return a*np.sin(b*x + c) + d
def sine_data(x, y): return curve_fit(sine_fit, x, y, maxfev=get_maxfev())
# -------------------------------------Cosine Fit----------------------------------------------------
def cosine_fit(x, a, b, c, d): return a*np.cos(b*x + c) + d
def cosine_data(x, y): return curve_fit(cosine_fit, x, y, maxfev=get_maxfev())
# -------------------------------------Cosine Squared Fit--------------------------------------------------------
# not sure if theres a point to this it doesnt even work smh
def cossqrd_fit(x, a, b, c, d): return a*np.square(np.cos(b*x + c)) + d
def cossqrd_data(x, y): return curve_fit(cossqrd_fit, x, y, maxfev=get_maxfev())
# ---------------------------------- Gaussian Fit ----------------------------------------------------------------
def gauss_fit(x, a, b, c, d): return a*np.exp(-1*((x-b)**2)/(c**2)) + d
def gauss_data(x, y): return curve_fit(gauss_fit, x, y, maxfev=get_maxfev())
# ---------------------------------------R^2 CALCULATION----------------------------------------------------------------
# function to calculate the R^2 value of a regression line
def r_squared(y, func):

    # forumla for R^2 calculation
    residuals = y - np.array(func)
    # residual sum of squares
    ss_res = np.sum(residuals**2)
    ss_total = np.sum((y - np.mean(y))**2)

    # depending on the data, the regression function can yield results > 1 or ss_total = 0 so R^2 would be undefined
    # this returns nan so in each of these cases the R^2 value is set to be 0
    if ss_total == 0:
        return 0
    elif (ss_res / ss_total) > 1:
        return 0
    else:
        return np.sqrt(1 - (ss_res / ss_total))

def get_maxfev(): return maxfev
def set_maxfev(maxfev): maxfev = maxfev
