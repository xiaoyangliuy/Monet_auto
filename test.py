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

def lsf_to_mtf(x,lsf,pixel_size=3.44,pad_factor=8,window="hann"):
    """Convert LSF to MTF.
    x: distance array in pixel unit
    lsf: line spread function array
    pixel_size: pixel size in um
    pad_factor: zero padding factor for FFT
    window: window function, "hann" or "none"
    return:
        freq: frequency array in cycles/mm
        mtf: modulation transfer function array
    """
    lsf = np.clip(lsf, 0.0, None)  # remove negative values
    if window == "hann":
        lsf = lsf * np.hanning(len(lsf))
    elif window == "hamming":
        lsf = lsf * np.hamming(len(lsf))
    area = np.trapz(lsf,x)
    if area <= 0:
        raise ValueError("LSF area is non-positive.")
    lsf = lsf / area  # normalize area to 1
    n = len(lsf)
    nz= int(max(pad_factor,1)*n)
    z = np.zeros(nz)
    z[:n] = lsf
    dx_um = pixel_size * (x[1]-x[0])  # um
    otf = np.fft.rfft(z)
    mtf = np.abs(otf)
    mtf /= mtf[0]  # normalize to 1 at zero frequency
    freq = np.fft.rfftfreq(nz, d=dx_um)  # cycles/um
    return freq, mtf

def freq_at_mtf(f, mtf, level=0.1):
    """Return frequency at given MTF level by linear interpolation."""
    if mtf[0] < level:
        return np.nan
    idx = np.where(mtf < level)[0]
    if len(idx) == 0 or idx[0] == 0:
        return np.nan
    k = idx[0]
    return np.interp(level, [mtf[k-1], mtf[k]], [f[k-1], f[k]])


lsf = dIdr(df['Gray_Value'].values, dr=1)
x = np.arange(len(lsf))
fwhm_value, xL, xR, i0 = fwhm(x, lsf)
print(f"FWHM: {fwhm_value:.2f} pixels, {fwhm_value * 3.44:.2f} um")
plt.figure(figsize=(6.3,6), dpi=120)
'''
#this is for plot LSF
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
'''
freq, mtf = lsf_to_mtf(x, lsf, pixel_size=3.44, pad_factor=8, window="hann")
f10 = freq_at_mtf(freq, mtf, level=0.1)
print(f"MTF10 = {f10:.2f} lp/um")
nyquist = 1/(2*mtf) #in um
plt.plot(freq, mtf,label="MTF",linewidth=1.8)
plt.axhline(0.1, linestyle=":", label="MTF = 0.10")
#plt.axvline(nyquist,linestyle=":")
#plt.xlim(0, min(freq[-1], nyquist*1.05))
#plt.ylim(0, 1.05)
plt.xlabel("Spatial frequency (lp/mm)")
plt.ylabel("MTF")

#plt.title("LSF and FWHM (per pixel)")
plt.legend()
plt.tight_layout()
plt.show()