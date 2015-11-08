import numpy
from numpy.fft import fft, ifft
from scipy import stats

# Features implemented:
# event_durations - compute the durations of events given their start times and the overall duration
# overall_rep_features - compute the overall repetitiveness of a single-dimensional signal
# intra_sect_rep_features* - compute the repetitiveness within each section of a single-dimensional signal
# inter_sect_rep_features* - compute the repetitiveness across each pair of sections of a single-dimensional signal
# 
# * - requires a call to partition_segments in order to partition the segments into their respective sections

# predicted computational costs (benchmarked using an i5-3210M CPU @ 2.50GHz × 4):
# test data: 10,000 tracks with 1,000 randomly generated segments and 10 randomly spaced sections each
#   overall repetition: approximately 4 minutes to compute for all 12 timbre dimensions
#   intra-section repetition: approximately 8 minutes to compute for all 12 timbre dimensions
#   inter-section repetition: approximately 60 minutes to compute for all 12 timbre dimensions
# actual results on the real dataset may vary

# computes the length of each event (e.g. segments, sections, tatums, bars, beats, etc)
# input:
#   events_start - the start times of the events
#   duration - the total duration of the track
#   norm - if set to true, normalizes the durations by the total duration (optional, defaults to false)
# outputs: list of same size as events_start, containing the respective length of each event in seconds
def event_durations(events_start, duration, norm=False):
    if events_start:
        n = len(events_start)
        start = events_start[0]
        to_ret = [0.] * n
        for i in range(1,n):
            end = events_start[i]
            to_ret[i-1] = end - start
            start = end
        to_ret[n-1] = duration - start
        if norm:
            for k in range(0,n):
                to_ret[k] /= duration
        return to_ret
    else:
        return []

# computes overall repetition features of the input list
# input:
#   samples - input list of data
# final result is ordered as follows:
#   [max_off, max, min_off, min, mean, median, var, skew, kurtosis]
# for:
#   offset locations of max/min ('max_off'/'min_off'), and their values ('max'/'min')
#   statistics for the absolute value autocorrelation result ('mean','median','var','skew','kurtosis')
def overall_rep_features(samples):
    return extract_ac_features(samples, stats=True)

# computes repetition features within each section
# input:
#   samples - input list of data
#   partitions - structure generated from calling partition_segments (we only need to call this once per song)
# accumulates the overall max, and min, as well as statistics for the max and mins across all sections
# final result is ordered as follows:
#   [max_min, max_max, mean_max, var_max, skew_max, kurtosis_max, min_min, max_min, mean_min, var_min, skew_min, kurtosis_min]
def intra_sect_rep_features(samples, partitions):
    num_sect = len(partitions)
    max_vals = numpy.zeros(num_sect, dtype='f')
    min_vals = numpy.zeros(num_sect, dtype='f')
    for i, (start, end) in enumerate(partitions):
        result = extract_ac_features(samples[start:end])
        max_vals[i] = result[1]
        min_vals[i] = result[3]
    return [numpy.min(max_vals), numpy.max(max_vals), numpy.mean(max_vals), numpy.var(max_vals), stats.skew(max_vals), stats.kurtosis(max_vals), 
        numpy.min(min_vals), numpy.max(min_vals), numpy.mean(min_vals), numpy.var(min_vals), stats.skew(min_vals), stats.kurtosis(min_vals)]

# computes repetition features pairwise among sections
# input:
#   samples - input list of data
#   partitions - structure generated from calling partition_segments (we only need to call this once per song)
# accumulates the overall max, and min, as well as statistics for the max and mins across all sections
# final result is ordered as follows:
#   [max_min, max_max, mean_max, var_max, skew_max, kurtosis_max, min_min, max_min, mean_min, var_min, skew_min, kurtosis_min]
def inter_sect_rep_features(samples, partitions):
    num_sect = len(partitions)
    num_pairs = (num_sect * (num_sect - 1)) / 2 # num_sect choose 2
    max_vals = numpy.zeros(num_pairs, dtype='f')
    min_vals = numpy.zeros(num_pairs, dtype='f')
    pair_idx = 0
    for i, (s1, e1) in enumerate(partitions):
        for j in range(i+1, num_sect):
            (s2, e2) = partitions[j]
            result = extract_xc_features(samples[s1:e1], samples[s2:e2])
            max_vals[pair_idx] = result[1]
            min_vals[pair_idx] = result[3]
            pair_idx += 1
    return [numpy.min(max_vals), numpy.max(max_vals), numpy.mean(max_vals), numpy.var(max_vals), stats.skew(max_vals), stats.kurtosis(max_vals), 
        numpy.min(min_vals), numpy.max(min_vals), numpy.mean(min_vals), numpy.var(min_vals), stats.skew(min_vals), stats.kurtosis(min_vals)]

# performs autocorrelation on the input list
# outputs the following statistics in a list (as requested):
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
# outputs the following statistics in a list (as requested):
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

# returns a list of 2-tuples, containing the first (inclusive) and last (exclusive) indices of segments within each section
# if a segment overlaps between two sections, it is placed into the former section unless 4/5 or more of the segment lies within the latter section
# if the first section starts at some t > 0, all segments within the interval [0,t] are included in the first section
# if the last section ends at some t < duration, all segments within the interval [t,duration] are included in the last section
# final output list size will correspond to the number of sections
def partition_segments(sections_start, segments_start, duration):
    num_sect = len(sections_start)
    num_seg = len(segments_start)
    to_ret = [(0,0)] * num_sect
    i = 0
    for i_sect in range(1,num_sect):
        start = i
        end = sections_start[i_sect] * 5
        seg_start = 4 * segments_start[i]
        seg_end = segments_start[i+1]
        while (seg_start + seg_end) < end:
            i += 1
            seg_start = 4 * seg_end
            seg_end = segments_start[i+1]
        to_ret[i_sect-1] = (start, i)
    to_ret[num_sect-1] = (i, num_seg)
    return to_ret

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


