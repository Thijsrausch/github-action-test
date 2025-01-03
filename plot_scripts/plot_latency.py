#!/usr/bin/env python
# coding: utf-8

# ## Generating histogram, CDF and HDR plots from histrogram data in .csv format
# * also generates sequence plot from sequence data in .csv format
# 
# ### Input format
# * histogram data in csv format with two columns
# * latency (in nanosecond)
# * occurence
# * e.g. as output by MoonGen
# * example:
# ```
# 1663,1
# 1668,22
# 1669,76
# 1674,13
# 1675,930
# 1680,73
# 1681,449
# ```
# 
# ### Features
# * histogram, normalized histogram, CDF and HDR generation
# * optinal sequence plot generation
# * figures created in figures/*.tex
# * externalized data into data/*.tsv
# * TUMcolors supported
# * makefile to generate pdfs
# * same structure as expected by I8 thesis template
# * latency is converted to microsecond
# * histogram data is binned to microsecond resolution
# 
# ## You should not have to edit any of the following cells besides the last one
# * However you might want to tweak some plots manually
# 
# ## errors
# * if you get tex capacity exceeded when trying to compile the figures you have too many data points
#  * solution: less bins, by rounding more (e.g. 10 or 100 microsecond resolution)
#  * change: in to_microsecond change the dividend (from 1000 to 10000 or 100000)
#  * result: not microsecond resolution/bins but 10 or 100 microsecond
#  * dont forget to either update all axis labels or convert back to microsecond after binning

# In[ ]:


import os
import sys
import math
import json
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from glob import glob
rprint=print
from pprint import pprint as print


# In[ ]:


# import other utility notebooks
import import_ipynb
# NOTE: tumcolors only work with python 3.6 and newer
from util.tumcolor import tumcolor_cycler
from util.i8_tikzplotlib import get_tikz_code, save_plt
from util.loop_plot import _plot_loop


# In[ ]:


# for command line invocation
def run_from_cli():
    import argparse

    parser = argparse.ArgumentParser(description='Generating plots from histogram data')
    parser.add_argument('basepath', metavar='BASEPATH', type=str,
                        help='Base path for all experiments')
    parser.add_argument('--histogram-filename', metavar='HIST_FILENAME', type=str, default='histogram.csv',
                        help='name of the histogram data file, wildcard possible')
    parser.add_argument('--sequence-filename', metavar='SEQ_FILENAME', type=str, default='',
                        help='name of the sequence data file, wildcard possible')
    parser.add_argument('--name', type=str, default='',
                        help='suffix for output files, e.g. hdr-NAME.tex')
    parser.add_argument('path', metavar='PATH', type=str, nargs='+',
                        help='path to one or more csv file(s), will be RESULTS/<path>/HIST_FILENAME')
    parser.add_argument('--label', metavar='LABEL', type=str, action='append',
                        help='Nicer name for experiments')
    parser.add_argument('--round-ms-digits', metavar='ROUND', type=int, default=3,
                        help='Round to ROUND ms digits for binning')
    parser.add_argument('--histogram-bar-width', metavar='BAR_WIDTH', type=float, default=0.005,
                        help='Width for histogram bars')

    args = parser.parse_args()
    if args.label and not len(args.label) == len(args.path):
        raise argparse.ArgumentTypeError('Must provide a label for either no or all paths')
        
    experiments = []
    if args.label:
        experiments = list(zip(args.path, args.label))
    else:
        experiments = args.path
        
    plot(experiments,
         basepath=args.basepath,
         histogram_file=args.histogram_filename,
         sequence_file=args.sequence_filename,
         name=args.name,
         round_ms_digits=args.round_ms_digits,
         histogram_bar_width=args.histogram_bar_width,
    )
        
    sys.exit()


# In[ ]:


def read_2c_csv(exp):
    data = dict()
    with open(exp) as infile:
        for line in infile:
            lat, occ = line.strip().split(',')
            data[int(lat)] = int(occ)
    return data


# In[ ]:


def to_microsecond(data, keys=True, values=False):
    if keys and values:
        return {k / 1000: v / 1000 for k, v in data.items()}
    if keys:
        return {k / 1000: v for k, v in data.items()}
    if values:
        return {k: v / 1000 for k, v in data.items()}
    
def to_ms_bins(data, round_ms_digits=3):
    binned = {}
    for k, v in data.items():
        rounded = round(k, round_ms_digits)
        if rounded not in binned:
            binned[rounded] = v
        else:
            binned[rounded] += v
    return binned

def to_expanded(data):
    expanded = []
    for val, occ in data.items():
        expanded += [val] * occ
    return expanded

def normalize(data):
    total = sum(data.values())
    percs = {k: (v/total) for k, v in data.items()}
    return percs

def accumulate(data):
    global curr
    curr = 0
    def acc(val): # just for the list comprehension
        global curr
        curr += val
        return curr
    return {k: acc(v) for k, v in sorted(data.items())}
    
def to_hdr(data):
    # treat negative (>1.0) and exact 1.0 values and very high values for v
    MAX_ACCURACY = 1000000000
    return {k: 1/(1-v) for k, v in data.items() if not (1-v) == 0.0 and not 1/(1-v) < 0 and not 1/(1-v) > MAX_ACCURACY}


# In[ ]:


def extract_hist_data(paths, basepath='/', histogram_file='histogram.csv', round_ms_digits=3,
                      progression_mapping_function=None):
    data = {}
    if not isinstance(paths, list):
        paths = [paths]

    for path in paths:
        name = None
        if not isinstance(path, tuple):
            name = path.replace('_', '-') # tex friendly path
        else:
            name = path[1]
            path = path[0]
            
        extended_path = os.path.join(basepath, path)
        experiment = os.path.join(extended_path, histogram_file)
        rprint('Processing ' + extended_path)
        
        subexperiments = glob(experiment)
        update_name = False
        base_name = name
        if len(subexperiments) > 1:
            update_name = True
        
        for exp in subexperiments:
            # replace everything that is not wildcard
            if not (basepath == '.' or basepath == '..'):
                histo = exp.replace(basepath, '')
            histo = histo.replace(path, '')
            histo = histo.replace(histogram_file, '')
            histo = histo.replace('//', '/')
            histo = histo[:-1]
            
            rprint('Subexperiment ' + histo)
            if update_name:
                name = base_name + histo
                
            # load data
            try:
                raw_data = read_2c_csv(exp)
            except FileNotFoundError as exce:
                rprint('Skipping - {}'.format(exce), file=sys.stderr)
                continue
                
            # different processing steps
            ms_data = to_microsecond(raw_data)
            hist_data = to_ms_bins(ms_data, round_ms_digits=round_ms_digits)
            box_data = to_expanded(ms_data)
            normalized_data = normalize(hist_data)
            accumulated_data = accumulate(normalized_data)
            hdr_data = to_hdr(accumulated_data)
            
            
            # store data
            data[name] = {}
            data[name]['hist'] = hist_data
            data[name]['hist_norm'] = normalized_data
            data[name]['cdf'] = accumulated_data
            data[name]['hdr'] = hdr_data
            data[name]['box'] = box_data
            if progression_mapping_function:
                data[name]['x_value'] = progression_mapping_function(exp)

    return data

def extract_sequence_data(paths, basepath='/', sequence_file='sequence.csv'):
    data = {}
    if not isinstance(paths, list):
        paths = [paths]

    for path in paths:
        name = None
        if not isinstance(path, tuple):
            name = path.replace('_', '-') # tex friendly path
        else:
            name = path[1]
            path = path[0]
            
        extended_path = os.path.join(basepath, path)
        experiment = os.path.join(extended_path, sequence_file)
        rprint('Processing ' + extended_path)
        
        subexperiments = glob(experiment)
        update_name = False
        base_name = name
        if len(subexperiments) > 1:
            update_name = True
        
        for exp in subexperiments:
            # remove basepath and filename from what we will use as label
            histo = exp.replace(basepath, '')
            histo = histo.replace(sequence_file, '')
            
            rprint('Subexperiment ' + histo)
            if update_name:
                name = base_name + histo
        
            # load data
            try:
                raw_data = read_2c_csv(exp)
            except FileNotFoundError as exce:
                rprint('Skipping - {}'.format(exce), file=sys.stderr)
                continue
            
            # different processing steps
            seq_data = to_microsecond(raw_data, keys=False, values=True)
            
            
            # store data
            data[name] = {}
            data[name]['seq'] = seq_data

    return data


# In[ ]:


def get_sorted_values(xs, ys, sort_by='xs'):
    # necessary for python <3.6
    if sort_by == 'xs':
        sort_by = 0
    else:
        sort_by = 1
    tup = zip(xs, ys)
    tup = sorted(tup, key=lambda x: x[sort_by])
    xs = [x for x,_ in tup]
    ys = [y for _,y in tup]
    return xs, ys

def plot_sequence(data, name=''):
    fig, ax = plt.subplots(figsize=(12,6))
    ax.set_prop_cycle(tumcolor_cycler)
    
    max_value = 0
    min_value = 1000000
    for exp, data in sorted(data.items()):
        hist = data['seq']
        xs = list(hist.keys())
        ys = list(hist.values())
        xs, ys = get_sorted_values(xs, ys)
        max_value=max(max_value, max(xs))
        min_value=min(min_value, min(xs))
        ax.plot(xs, ys, marker='o', markersize=1, linestyle='', label=exp)

    plt.ylim(bottom=0)
                
    ax.grid()
    ax.set(ylabel='Latency [$\mu$s]',
           xlabel='Number [-]')
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    
    plt.xlim(left=min_value)
    plt.xlim(right=max_value)
    
    save_plt('sequence', name=name)
    plt.show()


# In[ ]:


def plot_hist(data, name='', key='hist', ymax=None, ylabel='Occurence [-]',
              historgram_bar_width=0.005):
    fig, ax = plt.subplots(figsize=(9,6))
    ax.set_prop_cycle(tumcolor_cycler)
    
    max_value = 0
    data_points = 0
    for exp, data in sorted(data.items()):
        hist = data[key]
        xs = list(hist.keys())
        if key == 'hist':
            factor = 1
        else:
            # assume normalized
            factor = 100
        ys = [factor * val for val in hist.values()]
        if not ys:
            continue
        tup = zip(xs, ys)
        tup = sorted(tup, key=lambda x: x[0])
        xs, ys = get_sorted_values(xs, ys)
        data_points += len(ys)
        max_value=max(max_value, max(ys))
        ax.bar(xs, ys, width=historgram_bar_width, label=exp)

    print('Total amount of data points: {}'.format(data_points))
    
    if not ymax:
        ymax = max_value
    plt.ylim(bottom=0)
    plt.ylim(top=ymax)
                
    ax.grid()
    ax.set(ylabel=ylabel,
           xlabel='Latency [$\mu$s]')
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    
    plt.xlim(left=0)
    
    save_plt(key, name=name)
    plt.show()


# In[ ]:


def plot_cdf(data, name=''):
    fig, ax = plt.subplots(figsize=(9,6))
    ax.set_prop_cycle(tumcolor_cycler)
    
    for exp, data in sorted(data.items()):
        cdf = data['cdf']
        xs = list(cdf.keys())
        ys = [100 * val for val in cdf.values()]
        xs, ys = get_sorted_values(xs, ys)
        ax.plot(xs, ys, label=exp)


    plt.ylim(bottom=0)
    plt.ylim(top=100)
                
    ax.grid()
    ax.set(ylabel='CDF [\%]',
           xlabel='Latency [$\mu$s]')
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    
    plt.xlim(left=0)
    
    save_plt('cdf', name=name)
    plt.show()


# In[ ]:


def plot_hdr(data, name=''):
    fig, ax = plt.subplots(figsize=(9,6))
    ax.set_prop_cycle(tumcolor_cycler)
    
    max_value = 0
    min_value = 10000000000
    for exp, data in sorted(data.items()):
        hdr = data['hdr']
        xs = list(hdr.values())
        ys = list(hdr.keys())
        if not ys:
            continue
        xs, ys = get_sorted_values(xs, ys)
        max_value=max(max_value, max(ys))
        min_value=min(min_value, min(ys))
        ax.plot(xs, ys, label=exp)
              
            
    # automatically determine min/max based on min/max values log10
    log_max = pow(10, math.ceil(math.log10(max_value)))
    log_min = pow(10, math.floor(math.log10(min_value)))
    plt.ylim(bottom=log_min)
    plt.ylim(top=log_max)
                
    ax.grid()
    ax.set(xlabel='Percentile [\%] (log)',
           ylabel='Latency [$\mu$s] (log)')
    ax.set_xscale('log', subsx=[])
    ax.set_yscale('log')
    ticks = [1, 2, 10, 100, 1000, 10000, 100000, 1000000]
    labels = ["0", "50", "90", "99", "99.9", "99.99", "99.999", "99.9999"]
    plt.xticks(ticks, labels)
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.xlim(left=1)
    # TODO determine xlim right

    save_plt('hdr', name=name)
    plt.show()


# In[ ]:


def plot_box(data, name=''):
    fig, ax = plt.subplots(figsize=(9,6))
    ax.set_prop_cycle(tumcolor_cycler)
    
    boxes = []
    labels = []
    for exp, data in sorted(data.items()):
        values = data['box']
        boxes.append(values)
        labels.append(exp)
    ax.boxplot(boxes, showfliers=True, whis=1.5, labels=labels, patch_artist=True,
               medianprops=dict(color='TUMOrange'),
               boxprops=dict(facecolor='TUMWhite', color='TUMBlack'),
               
            )
            
    plt.ylim(bottom=0)
    plt.xticks(ticks=range(1, len(labels) + 1), labels=labels)
    plt.xlim(left=0.5, right=len(labels) + 0.5)
                
    ax.grid()
    ax.set(xlabel='',
           ylabel='Latency [$\mu$s]')

    save_plt('box', name=name)
    plt.show()


# In[ ]:


def plot_progression(data, name='', percentiles=None, xlabel='Unknown [-]'):
    if not percentiles:
        percentiles = [50]
    
    fig, ax = plt.subplots(figsize=(9,6))
    ax.set_prop_cycle(tumcolor_cycler)
    
    values = dict()
    max_x_value = 0
    min_x_value = 1000000
    
    # first gather data
    for exp, data in sorted(data.items()):
        test = '/'.join(exp.split('/')[:-1])
        if test not in values:
            values[test] = {}
            
        # get percentile from cdf data
        for percentile in percentiles:
            perc = -1
            try:
                perc = np.percentile(data['box'], percentile)
            except IndexError:
                pass
            if not percentile in values[test]:
                values[test][percentile] = []
            values[test][percentile].append((data['x_value'], perc))
        
    # plot data per test and percentile
    for exp, data in values.items():
        for percentile, data in data.items():
            data = sorted(data)
            xs = [x for x, _ in data]
            ys = [y for _, y in data]
            max_x_value = max(max_x_value, max(xs))
            min_x_value = min(max_x_value, min(xs))
            ax.plot(xs, ys, label='{} ({}th percentile)'.format(exp, percentile), marker='x')

    plt.ylim(bottom=0)
    plt.xlim(left=min_x_value)
    plt.xlim(right=max_x_value)
                
    ax.grid()
    ax.set(ylabel='Latency [$\mu$s]',
           xlabel=xlabel)
    ax.legend(loc='center left', bbox_to_anchor=(1, 1))
    
    save_plt('progression_{}'.format('_'.join([str(p) for p in percentiles])), name=name)
    plt.show()


# In[ ]:


def plot_loop(name, content, mapping, hist_data, key=None):
    if not key:
        key = [50]
    
    fig, ax = plt.subplots(figsize=(9,6))
    ax.set_prop_cycle(tumcolor_cycler)
    
    axis_label = None
    xss = {}
    yss = {}
    mapped = {}
    
    # gather data based on mapping
    for exp, run, type in content:
        axis_label = list(type.keys())[0]
        if exp not in xss:
            xss[exp] = []
            yss[exp] = {}
        xss[exp].append(list(type.values())[0])
        try:
            mapped[exp] = hist_data[mapping[exp][run]]
        except KeyError as exce:
            continue
        else:
            data = mapped[exp]
            for percentile in key:
                perc = -1
                try:
                    perc = np.percentile(data['box'], percentile)
                except IndexError:
                    pass
                if not percentile in yss[exp]:
                    yss[exp][percentile] = []
                yss[exp][percentile].append(perc)
        
    for exp, data in sorted(mapped.items()):
        for percentile in sorted(key):
            ys = yss[exp][percentile]
            xs = xss[exp]
            zipped = list(zip(xs, ys))
            zipped.sort(key=lambda tup: tup[0])
            xs, ys = zip(*zipped)
            
            ax.plot(xs, ys, marker='x', label = exp)
    
    plt.ylim(bottom=0)
    #plt.xlim(left=min_x_value)
    #plt.xlim(right=max_x_value)
                
    ax.grid()
    ax.set(ylabel='Latency [$\mu$s]',
           xlabel=axis_label)
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    
    save_plt('loop_{}'.format('_'.join([str(p) for p in key])), name=name)
    plt.show()


# In[ ]:


def _plot_sequence(paths, name, sequence_file, **kwargs):
    print('------------- plotting sequence data ------------')
    seq_data = extract_sequence_data(paths, sequence_file=sequence_file, **kwargs)
    if not seq_data:
        rprint('No sequence data found', file=sys.stderr)
    else:
        plot_sequence(seq_data, name)
        
def _plot_default_histogram(name, hist_data, historgram_bar_width):
    print('------------ plotting default histogram data ----------')
    # different plot types for histogram data
    plot_hist(hist_data, name, historgram_bar_width=historgram_bar_width)
    plot_hist(hist_data, name, key='hist_norm', ylabel='Occurence [\%]',
              historgram_bar_width=historgram_bar_width)
    plot_box(hist_data, name)
    plot_cdf(hist_data, name)
    plot_hdr(hist_data, name)
    
def _plot_progression(hist_data, name, progression_x_label, progression_percentiles):
    print('------------ progression plots ----------------')
    for percentiles in progression_percentiles:
        plot_progression(hist_data, name, percentiles=percentiles, xlabel=progression_x_label)


# In[ ]:


def plot(paths, name=None, default_plots=True, percentiles=None,
         histogram_file=None, round_ms_digits=3, historgram_bar_width=0.005,
         sequence_file=None,
         progression_mapping_function=None, progression_x_label=None,
         loop_file=None, loop_order=None,
         **kwargs):
    
    if sequence_file:
        _plot_sequence(paths, name, sequence_file, **kwargs)
    
    if histogram_file:
        # histogram data
        hist_data = extract_hist_data(paths, histogram_file=histogram_file, round_ms_digits=round_ms_digits,
                                      progression_mapping_function=progression_mapping_function,
                                      **kwargs)
        if not hist_data:
            rprint('No histogram data found', file=sys.stderr)
            return
        
        if default_plots:
            _plot_default_histogram(name, hist_data, historgram_bar_width)
            
    if not percentiles:
        print('you need to define the percentiles of interest as list of lists')
        return

    if (progression_mapping_function and not progression_x_label) or (progression_x_label and not progression_mapping_function):
        raise RuntimeError('must define progression_mapping_function AND progression_x_label if using loop variables')
    if progression_mapping_function and progression_x_label:
        _plot_progression(hist_data, name, progression_x_label, percentiles)
        
    if (loop_file and not loop_order) or (loop_order and not loop_file):
        raise RuntimeError('must define loop_file AND loop_order if using loop variables')
    if loop_file and loop_order:
        _plot_loop(paths, name, hist_data, loop_file, loop_order, percentiles, plot_loop, **kwargs)


# In[ ]:


# this will only be triggered if invoked from command-line
if not sys.argv[0].endswith('ipykernel_launcher.py'):
    run_from_cli()


# # Make your edits in the cell below

# In[ ]:


# base path for all your experiments
# e.g. if all your experiments are in /srv/testbed/results/USER/default/
# with subexperiments that have the HISTOGRAM_FILENAME in
# 2020-02-23_13-44-39_703517/litecoincash/9000-0064
# 2020-02-23_13-44-39_703517/litecoincash/9000-0065
# 2019-02-23_13-44-39_703517/litecoincash/9000-0064
RESULTS='sample_data'
# HISTOGRAM_FILENAME may contain wildcard
HISTOGRAM_FILENAME = 'histogram_run*.csv'

# fine tuning parameters for histograms
ROUND_MS_DIGITS = 1
HISTOGRAM_BAR_WIDTH = 0.5

# plot expects a list of subexperiments that will be combined like the following
#    RESULTS/<subexperiment>/HISTOGRAM_FILENAME
# each subexperiment is either defined as
# - string, used as path to experiment and as legend entry
# - tuple of (path, name) where name will be used as legend entry for this subexperiment
# works the same for optional SEQUENCE_FILENAME
# optional keyword 'name': added to output files

# you now have three options for plotting
# #1: plot the latency output of each experiment run
# usually this is NOT what you want but can be helpful to check that your experiment actually ran
# this will generate a lot of plots and will take some time (and might be unreadable)
plot([
      ('2020-09-04_17-08-15_063541/bitcoin', 'Test1'),
     ],
     basepath=RESULTS,
     name='sample',
    
     histogram_file=HISTOGRAM_FILENAME,
     round_ms_digits=ROUND_MS_DIGITS,
     historgram_bar_width=HISTOGRAM_BAR_WIDTH,
)


# In[ ]:


RESULTS='sample_data'
HISTOGRAM_FILENAME = 'histogram_run*.csv'

# #2: plot a progression of your experiment
# usually you have one parameter in your experiment runs changing
# if you have encoded this into the filename, you can plot it

# you need to define this function
def progression_mapping_function(exp):
    # in case you want to plot the progression of
    # experiments within one experiment folder
    # this function maps a certain run (one output file within this
    # experiment) to the x value used for the progression
    
    # in this example case the progression is based on the run number
    # which is encoded in the path (the wildcard in the histogram file)
    val = float(exp.split('_run')[-1].split('.')[0])
    return val

# as before, but with progression_* parameters
# percentiles defines which percentiles you want per plot
plot([
      ('2020-09-04_17-08-15_063541/bitcoin', 'Test1'),
     ],
     basepath=RESULTS,
     name='sample',
     histogram_file=HISTOGRAM_FILENAME,
    
     percentiles=[[50], [0, 100]],
     default_plots=False, # do not plot #1 plots
    
     progression_mapping_function=progression_mapping_function,
     progression_x_label='Packet Size [B]',
)


# In[ ]:


RESULTS='sample_data'
HISTOGRAM_FILENAME = 'histogram_run*.csv'

# can include wildcards
LOOP_FILENAME = '*_unknown_run*.loop'

# #3: using a pos loop experiment
# define the format of the loopfile
# and define the order of the loop parameters
plot([
      ('2020-09-04_17-08-15_063541/bitcoin', 'Test1'),
     ],
     basepath=RESULTS,
     name='sample',
     histogram_file=HISTOGRAM_FILENAME,
    
     percentiles=[[50], [0, 100]],
     default_plots=False,
    
     loop_file=LOOP_FILENAME,
     loop_order=['pkt_sz', 'cpu_frequency', 'pkt_rate'],
)


# In[ ]:


RESULTS='/srv/testbed/results/stubbe/modanet/'
SEQUENCE_FILENAME = 'sequence.csv'

# you can plot only the sequence data
plot([
      ('2020-02-23_13-44-39_703517/litecoincash/*', 'Baseline'),
     ],
     basepath=RESULTS,
     sequence_file=SEQUENCE_FILENAME,
     name='sample',
)


# In[ ]:




