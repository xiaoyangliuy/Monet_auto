import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

os.chdir(r"C:\Research\OneDrive - Argonne National Laboratory\anl\1_Imaging_eberlight\manuscript\7bm_auto")
fn = "slanted_edge_line.csv"
df = pd.read_csv(fn)
def dIdr(esf, dr=1.0):
    """Return LSF = dI/dr for ESF samples spaced by dr."""
    esf = np.asarray(esf, float)
    lsf = np.gradient(esf, dr)
    if lsf[np.argmax(np.abs(lsf))] < 0:
        lsf = -lsf
    return lsf
def fwhm(x, y):
    yabs = np.abs(y)
    i0 = int(np.argmax(yabs))          # index of the dominant |peak|
    hm = 0.5 * yabs[i0]                # half maximum

    # left crossing
    il = i0
    while il > 0 and yabs[il] > hm:
        il -= 1
    if il == i0:
        xL = x[i0]
    else:
        xL = np.interp(hm, [yabs[il], yabs[il+1]], [x[il], x[il+1]])

    # right crossing
    ir = i0
    n = len(x)
    while ir < n-1 and yabs[ir] > hm:
        ir += 1
    if ir == i0:
        xR = x[i0]
    else:
        xR = np.interp(hm, [yabs[ir-1], yabs[ir]], [x[ir-1], x[ir]])

    return xR - xL, xL, xR, i0
lsf = dIdr(np.sort(df['Gray_Value'].values), dr=1)
x = np.arange(len(lsf))
fwhm_value, xL, xR, i0 = fwhm(x, lsf)
print(f"FWHM: {fwhm_value:.2f} pixels, {fwhm_value * 3.44:.2f} um")
plt.figure(figsize=(6.3,6), dpi=120)
plt.plot(x*3.44, lsf, label="LSF = dI/dr (per pixel)",linewidth=1.8)
plt.axhline(np.sign(lsf[i0]) * 0.5 * abs(lsf[i0]), linestyle="--")
#plt.axvline(xL, linestyle=":")
#plt.axvline(xR, linestyle=":")
ax = plt.gca()
sf = ScalarFormatter(useMathText=True)
ax.tick_params(axis='both', which='major', labelsize=12)
sf.set_powerlimits((-3,3))
ax.yaxis.set_major_formatter(sf)
ax.set_xlabel("Distance ($\mu$m)",fontsize=12)
ax.set_ylabel("Amplitude",fontsize=12)
#plt.title("LSF and FWHM (per pixel)")
#plt.legend()
plt.tight_layout()
plt.show()