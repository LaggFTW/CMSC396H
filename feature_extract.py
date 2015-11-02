import numpy
from numpy.fft import fft, ifft
from scipy import stats

# performs autocorrelation on the input list
# outputs the following statistics in an array (as requested):
#   offset locations of max/min ('max_off'/'min_off'), and their values ('max'/'min')
#       set: offsets = True
#   statistics for the absolute value autocorrelation result ('mean','median','var','skew','kurtosis')
#       set: stats = True
# final result is ordered as follows:
#   [max_off, max, min_off, min, mean, median, var, skew, kurtosis]
def extract_ac_features(li, offsets=True, stats=False):
    x = numpy.array(li, dtype='f')
    n = x.size
    x = autocorre(x)
    result = []
    if offsets:
        (mx, mn) = ac_offsets(x)
        result.extend([(float(mx) / n), x[mx], (float(mn) / n), x[mn]])
    if stats:
        result.extend(gen_stats(numpy.absolute(x[1:n]), maxmin=False))
    return result

# performs cross-correlation on the input lists
# outputs the following statistics in an array (as requested):
#   offset locations of max/min ('max_off'/'min_off'), and their values ('max'/'min')
#       set: offsets = True
#   statistics for the absolute value cross-correlation result ('mean','median','var','skew','kurtosis')
#       set: stats = True
# final result is ordered as follows:
#   [max_off, max, min_off, min, mean, median, var, skew, kurtosis]
def extract_xc_features(li1, li2, offsets=True, stats=False):
    (x,y) = gen_nparr(list(li1), list(li2))
    n = x.size
    x = xcorre(x,y)
    result = []
    if offsets:
        (mx, mn) = xc_offsets(x)
        result.extend([(float(mx) / n), x[mx], (float(mn) / n), x[mn]])
    if stats:
        result.extend(gen_stats(numpy.absolute(x), maxmin=False))
    return result

# generates the seven statistics of the numpy array
def gen_stats(arr, maxmin=True):
    to_ret = [numpy.mean(arr), numpy.median(arr), numpy.var(arr)]
    if maxmin:
        to_ret.extend([numpy.min(arr), numpy.max(arr)])
    to_ret.extend([stats.skew(arr), stats.kurtosis(arr)])
    return to_ret

# generates a numpy array for the given list
# if two lists are given, generates a 2-tuple of numpy arrays, each with size
# equal to maximum between the two lists (pads zeros at the end of the shorter list)
# note that the list inputs become zero-padded similarly a side-effect
def gen_nparr(li1, li2=None):
    if li2 is None:
        return numpy.array(li1, dtype='f')
    else:
        size = max(len(li1), len(li2))
        li1.extend([0]*(size-len(li1)))
        li2.extend([0]*(size-len(li2)))
        return (numpy.array(li1, dtype='f'), numpy.array(li2, dtype='f'))

# computes circular autocorrelation
# normalizes the final range of values to be between -1 and 1
# arguments:
# x - numpy array containing the signal input
def autocorre(x):
    x_2norm = x.dot(x)
    if x_2norm > 0:
        fx = fft(x)
        return (ifft(fx * fx.conj()).real) / x_2norm
    else:
        return x

# computes circular cross-correlation
# before computation, normalizes x and y by their mean and standard deviations
# normalizes the final range of values between -1 and 1
# arguments:
# x,y - numpy arrays containing the signal input, of equal size
def xcorre(x, y):
    x = (x - numpy.mean(x))
    stdx = numpy.std(x)
    y = (y - numpy.mean(y))
    stdy = numpy.std(y)
    x = x / stdx if stdx != 0 else x
    y = y / stdy if stdy != 0 else y
    return (ifft(fft(x) * fft(y).conj()).real) / x.size

# generates max/min + offsets for an autocorrelation result
# omits zero-offset element
# note: for the final statistics output, these offsets should be normalized:
#   offset_norm = float(offset) / array_size
# TODO: perhaps do this up to k-th order as well?
def ac_offsets(x):
    a = x[1:x.size]
    return (numpy.argmax(a) + 1, numpy.argmin(a) + 1)

# generates max/min + offsets for a cross-correlation result
# note: for the final statistics output, these offsets should be normalized:
#   offset_norm = float(offset) / array_size
# TODO: perhaps do this up to k-th order as well?
def xc_offsets(x):
    return (numpy.argmax(x), numpy.argmin(x))


