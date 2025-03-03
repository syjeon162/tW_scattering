import numpy as np
import os
import matplotlib.pyplot as plt
from Tools.helpers import finalizePlotDir
from coffea import hist

import re


colors = {
    'tW_scattering': '#FF595E',
    'topW_lep': '#FF595E',
    'topW_v2': '#FF595E',
    'topW_v3': '#FF595E',
    'signal': '#FF595E',
    #'tW_scattering': '#000000', # this would be black
    'TTW': '#8AC926',
    'TTXnoW': '#FFCA3A',
    'prompt': '#8AC926',
    'TTX': '#FFCA3A',
    'TTZ': '#FFCA3A',
    'lost lepton': '#FFCA3A',
    'TTH': '#34623F',
    'TTTT': '#0F7173',
    'ttbar': '#1982C4',
    'top': '#1982C4',
    'non prompt': '#1982C4',
    'wjets': '#6A4C93',
    'diboson': '#525B76',
    'WZ': '#525B76',
    'WW': '#34623F',
    'DY': '#6A4C93',
    'rare': '#EE82EE',
    'XG': '#5bc0de',
    'charge flip': '#6A4C93',
    'chargeflip': '#6A4C93',
    'MuonEG': '#000000',
    'conv_mc': '#5bc0de',
    'np_obs_mc': '#1982C4',
    'np_est_mc': '#1982C4',
    'np_est_data': '#1982C4',
    'cf_obs_mc': '#0F7173',
    'cf_est_mc': '#0F7173',
    'cf_est_data': '#0F7173',
}
'''
other colors (sets from coolers.com):
#525B76 (gray)
#34623F (hunter green)
#0F7173 (Skobeloff)
'''

my_labels = {
    'topW_lep': r'$tW \to tW$',
    #'tW_scattering': 'top-W scat.',
    #'topW_v2': 'top-W scat.',
    #'topW_v3': 'top-W scat.',
    #'topW_lep': 'top-W scat.',
    'signal': 'top-W scat.',
    'prompt': 'prompt/irred.',
    'non prompt': 'nonprompt',
    'charge flip': 'charge flip',
    'chargeflip': 'charge mis-ID',
    'lost lepton': 'lost lepton',
    'TTW': r'$t\bar{t}$W',
    'TTX': r'$t\bar{t}$Z/H',
    'TTXnoW': r'$t\bar{t}X\ (no\ W)$',
    'TTH': r'$t\bar{t}$H',
    'TTZ': r'$t\bar{t}$Z',
    'TTTT': r'$t\bar{t}t\bar{t}$',
    'ttbar': r'$t\bar{t}$+jets',
    'top': r'$t\bar{t}$',
    'wjets': 'W+jets',
    'DY': 'Drell-Yan',
    'diboson': 'VV/VVV',
    'rare': 'Rare',
    'WZ': 'WZ',
    'WW': 'WW',
    'MuonEG': 'Observed',
    'pseudodata': 'Pseudo-data',
    'uncertainty': 'Uncertainty',
    'XG': 'XG',  # this is bare XG
    'conv_mc': r'$X\gamma$',
    'np_obs_mc': 'nonprompt (MC true)',
    'np_est_mc': 'nonprompt (MC est)',
    'cf_obs_mc': 'charge flip (MC true)',
    'cf_est_mc': 'charge flip (MC est)',
    'np_est_data': 'nonprompt',
    'cf_est_data': 'charge flip',
}


data_err_opts = {
    'linestyle': 'none',
    'marker': '.',
    'markersize': 10.,
    'color': 'k',
    'elinewidth': 1,
}

signal_err_opts = {
    'linestyle':'-',
    'color':'crimson',
    'elinewidth': 1,
}

#signal_err_opts = {
#    'linestyle': '-',
#    'marker': '.',
#    'markersize': 0.,
#    'color': 'k',
#    'elinewidth': 1,
#    'linewidth': 2,
#}


error_opts = {
    'label': 'uncertainty',
    'hatch': '///',
    'facecolor': 'none',
    'edgecolor': (0,0,0,.5),
    'linewidth': 0
}

fill_opts = {
    'edgecolor': (0,0,0,0.3),
    'alpha': 1.0
}

line_opts = {
    'linestyle':'-',
    'linewidth': 3,
}

signal_fill_opts = {
    'linewidth': 2,
    'linecolor': 'k',
    'edgecolor': (1,1,1,0.0),
    'facecolor': 'none',
    'alpha': 0.1
}

import mplhep as hep
plt.style.use(hep.style.CMS)

def make_plot_from_dict(
        hist_d_in,
        axis,
        data=None,
        normalize=True,
        log=False,
        save=False,
        axis_label=None,
        ratio_range=None,
        shape=False,
        ymax=False,
        overflow='all',
        data_label='Observation',
        systematics=True,
        lumi = 1,
):
    if save:
        finalizePlotDir( '/'.join(save.split('/')[:-1]) )

    if data:
        fig, (ax, rax) = plt.subplots(2,1,figsize=(10,10), gridspec_kw={"height_ratios": (3, 1)}, sharex=True)
    else:
        fig, ax  = plt.subplots(1,1,figsize=(10,10) )

    # project out other axis
    processes = hist_d_in.keys()
    hist_d = {}
    for p in processes:
        hist_d[p] = hist_d_in[p].project(axis.name, 'systematic').rebin(axis.name, axis).copy()

    if data:
        data_h = data.project(axis.name).rebin(axis.name, axis).copy()
        data_val = data_h.values(overflow=overflow)[()]

    #total = np.zeros_like(hist_d[list(processes)[0]].integrate('systematic', 'central').values(overflow=overflow)[()])
    total = hist_d[list(processes)[0]].copy()
    total.clear()
    for p in processes:
        total.add(hist_d[p])#.integrate('systematic', 'central').values(overflow=overflow)[()]

    central = total.integrate('systematic', 'central').values(overflow=overflow)[()]
    if data and normalize:
        norm = sum(data_val)/sum(central)
        central = norm*central
    else:
        norm = 1

    y_max = np.max(central)*1.3 if not log else np.max(central)*30
    y_min = 0 if not log else max(np.min(central)*0.03, 0.03)
    edges = axis.edges(overflow=overflow)
    hep.histplot(
        [ norm*hist_d[p].integrate('systematic', 'central').values(overflow=overflow)[()] for p in processes],
        edges,
        histtype="fill",
        stack=True,
        label=[ my_labels[p] for p in processes ],
        color=[ colors[p] for p in processes ],
        ax=ax)

    if data:
        hep.histplot(
            data_h.values(overflow=overflow)[()],
            edges,
            w2=data_h.values(overflow=overflow, sumw2=True)[()][1],
            histtype="errorbar",
            stack=False,
            label=data_label,
            color='black',
            ax=ax
        )

        hep.histplot(
            data_h.values(overflow=overflow)[()]/central,
            edges,
            yerr=(np.sqrt(data_h.values(overflow=overflow, sumw2=True)[()][1])/central),
            histtype="errorbar",
            stack=False,
            label=data_label,
            color='black',
            ax=rax
        )


    ax.legend(
        loc='upper left',
        bbox_to_anchor=(0.3, 0.8, 0.45, .2),
        #mode="expand",
        ncol=2,
        #borderaxespad=0.0,
        #labels=updated_labels,
        #handles=handles,
    )

    opts = {'step': 'post', 'label': 'uncertainty', 'hatch': '///',
                    'facecolor': 'none', 'edgecolor': (0, 0, 0, .5), 'linewidth': 0, 'zorder':100.}

    # could in principle do sth like this [x.name for x in ax.identifiers()]
    all_syst = ['mu', 'ele', 'b', 'l', 'PU', 'jes']

    #systematics =

    sys_up = np.zeros_like(hist_d[list(processes)[0]].integrate('systematic', 'central').values(overflow=overflow)[()])
    sys_down = np.zeros_like(hist_d[list(processes)[0]].integrate('systematic', 'central').values(overflow=overflow)[()])
    if systematics:
        for proc in processes:
            for syst in all_syst:
                try:
                    sys_up += (hist_d[proc].integrate('systematic', syst+'_up').values(overflow=overflow)[()] - hist_d[proc].integrate('systematic', 'central').values(overflow=overflow)[()])**2
                    sys_down += (hist_d[proc].integrate('systematic', syst+'_down').values(overflow=overflow)[()] - hist_d[proc].integrate('systematic', 'central').values(overflow=overflow)[()])**2
                except KeyError:
                    pass
                    #print (f"Systematic {syst} not present for processes {proc}")

            if proc.count("np_est"):
                sys_up += (0.3*hist_d[proc].integrate('systematic', 'central').values(overflow=overflow)[()])**2
                sys_down += (0.3*hist_d[proc].integrate('systematic', 'central').values(overflow=overflow)[()])**2

        sys_up = np.sqrt(sys_up)
        sys_down = np.sqrt(sys_down)

    # NOTE unfortunately this does not work
    #sys_up   = np.sqrt(sum( [(total.integrate('systematic', syst+'_up').values(overflow=overflow)[()]-central)**2 for syst in all_syst ]) )
    #sys_down = np.sqrt(sum( [(total.integrate('systematic', syst+'_down').values(overflow=overflow)[()]-central)**2 for syst in all_syst ]) )
    stat = np.sqrt(total.integrate('systematic', 'central').values(overflow=overflow, sumw2=True)[()][1])
    #print (sys_up)


    up = central + np.sqrt(sys_up**2 + stat**2)
    rup = 1 + np.sqrt(sys_up**2 + stat**2)/central

    down = central - np.sqrt(sys_down**2 + stat**2)
    rdown = 1 - np.sqrt(sys_down**2 + stat**2)/central
    ax.fill_between(x=edges, y1=np.r_[down, down[-1]], y2=np.r_[up, up[-1]], **opts)

    if data:
        rax.fill_between(x=edges, y1=np.r_[rdown, rdown[-1]], y2=np.r_[rup, rup[-1]], **opts)

    if data:
        if ratio_range:
            rax.set_ylim(*ratio_range)
        else:
            rax.set_ylim(0.1,1.9)
        rax.set_ylabel('Obs./Pred.')
        rax.set_xlabel(axis.label)
    else:
        ax.set_xlabel(axis.label)

    ax.set_ylabel('Events')
    ax.set_xlim(edges[0], edges[-1])
    ax.set_ylim(y_min, y_max)
    if log:
        ax.set_yscale('log')
    plt.subplots_adjust(hspace=0)

    hep.cms.label(
        "Preliminary",
        data= (data is not None),
        lumi=lumi,
        loc=0,
        ax=ax,
    )

    if normalize:
        fig.text(0.55, 0.55, 'Data/MC = %s'%round(norm,2), fontsize=20,  horizontalalignment='left', verticalalignment='bottom', transform=ax.transAxes )


    if save:
        fig.savefig("{}.pdf".format(save))
        fig.savefig("{}.png".format(save))
        print ("Figure saved in:", save)

def makePlot(output,
             histo,
             axis,
             bins=None,
             data=[],
             normalize=True,
             log=False,
             save=False,
             axis_label=None,
             ratio_range=None,
             upHists=[],
             downHists=[],
             shape=False,
             ymax=False,
             overflowclip=False,
             new_colors=colors,
             new_labels=my_labels,
             order=None,
             signals=[],
             omit=[],
             lumi=60.0,
             binwnorm=None,
             overlay=None,
             is_data=True,
             y_axis_label='Events',
             rescale={},
             obs_label='Observation',
             channel='all',
             ):
    
    if save:
        finalizePlotDir( '/'.join(save.split('/')[:-1]) )

    if channel == 'ee':
        ch_sel = slice(1.5, 2.5)
    elif channel == 'em':
        ch_sel = slice(0.5, 1.5)
    elif channel == 'mm':
        ch_sel = slice(-0.5, 0.5)
    elif channel == 'all':
        ch_sel = slice(-0.5, 2.5)
    else:
        raise NotImplementedError


    mc_sel   = re.compile('(?!(%s))'%('|'.join(data+omit))) if len(data+omit)>0 else re.compile('')
    data_sel = re.compile('('+'|'.join(data)+')(?!.*incl)')
    bkg_sel  = re.compile('(?!(%s))'%('|'.join(data+signals+omit))) if len(data+signals+omit)>0 else re.compile('')

    if histo is None:
        processes = [ p[0] for p in output.values().keys() if not p[0] in data ]
        histogram = output.copy()
        syst_histogram = output.copy()

    else:
        processes = [ p[0] for p in output[histo].values().keys() if not p[0] in data ]
        syst_histogram = output[histo].copy()
        histogram = output[histo].copy()

    #histogram.integrate('systematic', 'central').integrate('n_ele')
    # NOTE this is what we do in the data card creation
    # tmp_central = output[hist_name][(process, eft_point, 'central', 'central')].sum('EFT', 'systematic', 'prediction').copy()
    #histogram = histogram[(wildcard, )]
    try:
        syst_histogram =  (syst_histogram
                           .integrate('n_ele', ch_sel)
                           .project(axis, 'dataset', 'systematic'))
        histogram = (histogram
                     .integrate('systematic', 'central')
                     .integrate('n_ele', ch_sel)
                     .project(axis, 'dataset'))
        print ("n_ele axis found for this histogram")
    except KeyError:
        # fallback if there's no n_ele axis
        print ("No n_ele axis found for this histogram")
        syst_histogram =  (syst_histogram
                           .project(axis, 'dataset', 'systematic'))
        histogram = (histogram
                     .integrate('systematic', 'central')
                     .project(axis, 'dataset'))

    if overlay: overlay = overlay.project(axis, 'dataset')
    if bins:
        histogram = histogram.rebin(axis, bins)
        syst_histogram = syst_histogram.rebin(axis, bins)
        if overlay: overlay = overlay.rebin(axis, bins)

    y_max = histogram[bkg_sel].sum("dataset").values(overflow='over')[()].max()

    MC_total = histogram[bkg_sel].sum("dataset").values(overflow='over')[()].sum()
    Data_total = 0
    if data:
        Data_total = histogram[data_sel].sum("dataset").values(overflow='over')[()].sum()
        #observation = histogram[data[0]].sum('dataset').copy()
        #first = True
        #for d in data:
        #    print (d)
        #    if not first:
        #        observation.add(histogram[d].sum('dataset'))
        #        print ("adding")
        #    first = False
    
    print ("Data:", round(Data_total,0), "MC:", round(MC_total,2))
    
    rescale_tmp = { process: 1 if not process in rescale else rescale[process] for process in processes }
    if normalize and data_sel:
        scales = { process: Data_total*rescale_tmp[process]/MC_total for process in processes }
        histogram.scale(scales, axis='dataset')
    else:
        scales = rescale_tmp

    if shape:
        scales = { process: 1/histogram[process].sum("dataset").values(overflow='over')[()].sum() for process in processes }
    histogram.scale(scales, axis='dataset')
    
    if data:
        fig, (ax, rax) = plt.subplots(2,1,figsize=(10,10), gridspec_kw={"height_ratios": (3, 1)}, sharex=True)
    else:
        fig, ax  = plt.subplots(1,1,figsize=(10,10) )

    if overlay:
        ax = hist.plot1d(overlay, overlay="dataset", ax=ax, stack=False, overflow='over', clear=False, line_opts=line_opts, fill_opts=None, binwnorm=binwnorm)

    if shape:
        ax = hist.plot1d(histogram[bkg_sel], overlay="dataset", ax=ax, stack=False, overflow='over', clear=False, line_opts=line_opts, fill_opts=None, binwnorm=binwnorm)
    else:
        ax = hist.plot1d(histogram[bkg_sel], overlay="dataset", ax=ax, stack=True, overflow='over', clear=False, line_opts=None, fill_opts=fill_opts, order=(order if order else processes), binwnorm=binwnorm)

    if signals:
        for sig in signals:
            ax = hist.plot1d(histogram[sig], overlay="dataset", ax=ax, stack=False, overflow='over', clear=False, line_opts=line_opts, fill_opts=None, binwnorm=binwnorm)
    if data:
        ax = hist.plot1d(histogram[data_sel].sum("dataset"), ax=ax, overflow='over', error_opts=data_err_opts, clear=False, binwnorm=binwnorm)
        #ax = hist.plot1d(observation, ax=ax, overflow='over', error_opts=data_err_opts, clear=False)

        hist.plotratio(
                num=histogram[data_sel].sum("dataset"),
                denom=histogram[bkg_sel].sum("dataset"),
                ax=rax,
                error_opts=data_err_opts,
                denom_fill_opts=None, # triggers this: https://github.com/CoffeaTeam/coffea/blob/master/coffea/hist/plot.py#L376
                guide_opts={},
                unc='num',
                #unc=None,
                overflow='over'
        )
    
    
    handles, labels = ax.get_legend_handles_labels()
    updated_labels = []
    for handle, label in zip(handles, labels):
        try:
            if label is None or label=='None':
                updated_labels.append(obs_label)
                handle.set_color('#000000')
            else:
                updated_labels.append(new_labels[label])
                handle.set_color(new_colors[label])
        except:
            pass

    if data:
        if ratio_range:
            rax.set_ylim(*ratio_range)
        else:
            rax.set_ylim(0.1,1.9)
        rax.set_ylabel('Obs./Pred.')
        if axis_label:
            rax.set_xlabel(axis_label)

    ax.set_xlabel(axis_label)
    ax.set_ylabel(y_axis_label)
    
    if not binwnorm:
        if not shape:
            addUncertainties(ax, axis, histogram, bkg_sel,
                             [syst_histogram.integrate('systematic', x) for x in upHists],
                             [syst_histogram.integrate('systematic', x)  for x in downHists],
                             overflow='over', ratio=False,
                             )

        if data:
            addUncertainties(rax, axis, histogram, bkg_sel,
                             [syst_histogram.integrate('systematic', x) for x in upHists],
                             [syst_histogram.integrate('systematic', x) for x in downHists],
                             overflow='over', ratio=True,
                             )
    
    if log:
        ax.set_yscale('log')
        
    y_mult = 1.7 if not log else 100
    if overflowclip:
        ax.set_xlim(None, bins._hi)
        y_max = histogram[bkg_sel].sum("dataset").values(overflow='none')[()].max()
    if ymax:
        ax.set_ylim(0.01, ymax)
    else:
        y_max = y_max*y_mult*(Data_total/MC_total) if data else y_max*y_mult
        ax.set_ylim(0.01, y_max if not shape else 2)
        #if binwnorm: ax.set_ylim(0.5)

    ax.legend(
        loc='upper right',
        bbox_to_anchor=(0.03, 0.88, 0.90, .11),
        mode="expand",
        ncol=3,
        borderaxespad=0.0,
        labels=updated_labels,
        handles=handles,
    )
    plt.subplots_adjust(hspace=0)

    hep.cms.label(
        "Preliminary",
        data=len(data)>0 and is_data,
        lumi=lumi,
        loc=0,
        ax=ax,
    )

    if normalize:
        fig.text(0.55, 0.55, 'Data/MC = %s'%round(Data_total/MC_total,2), fontsize=20,  horizontalalignment='left', verticalalignment='bottom', transform=ax.transAxes )


    if save:
        fig.savefig("{}.pdf".format(save))
        fig.savefig("{}.png".format(save))
        print ("Figure saved in:", save)

def addUncertainties(
        ax,
        axis,
        h,
        selection,
        up_vars,
        down_vars,
        overflow='over',
        ratio=False,
    ):

    # h is the central histogram, up and down the variations

    bins = h[selection].axis(axis).edges(overflow=overflow)
    
    values = h[selection].sum('dataset').values(overflow=overflow, sumw2=True)[()]
    central = values[0]
    stats = values[1]
    
    up = np.zeros_like(central)
    down = np.zeros_like(central)
    
    for up_var in up_vars:
        up += (up_var[selection].sum('dataset').values(overflow=overflow, sumw2=False)[()] - central)**2
    
    for down_var in down_vars:
        down += (down_var[selection].sum('dataset').values(overflow=overflow, sumw2=False)[()] - central)**2
    
    up   += stats 
    down += stats
 
    if ratio:
        up = np.ones_like(central) + np.sqrt(up)/central
        down = np.ones_like(central) - np.sqrt(down)/central
    else:
        up = central + np.sqrt(up)
        down = central - np.sqrt(down)
    
    opts = {'step': 'post', 'label': 'uncertainty', 'hatch': '///',
                    'facecolor': 'none', 'edgecolor': (0, 0, 0, .5), 'linewidth': 0, 'zorder':100.}
    
    ax.fill_between(x=bins, y1=np.r_[down, down[-1]], y2=np.r_[up, up[-1]], **opts)

def scale_and_merge(histogram, scales, nano_mapping, quiet=False):
    """
    Scale NanoAOD samples to a physical cross section.
    Merge NanoAOD samples into categories, e.g. several ttZ samples into one ttZ category.

    histogram -- coffea histogram
    scales -- scales to apply to each dataset
    nano_mapping -- dictionary to map NanoAOD samples into categories
    """
    temp = histogram.copy()
    # NOTE copy is not what is slow, but some histogram operations.
    # This is probably a price we have to pay for flexibility

    temp.scale(scales, axis='dataset')
    temp = temp.group("dataset", hist.Cat("dataset", "new grouped dataset"), nano_mapping) # this is not in place

    return temp

def compute_darkness(r, g, b, a=1.0):
    """Compute the 'darkness' value from RGBA (darkness = 1 - luminance)
       stolen from Nick Amin: https://github.com/aminnj/yahist
       Version from Jonathan Guiang: https://gist.github.com/jkguiang/279cb4d2e68e64148afc62274df09f18
    """
    return a * (1.0 - (0.299 * r + 0.587 * g + 0.114 * b))

def bin_text(counts, x_edges, y_edges, axes, cbar, errors=None, size=10, fmt=":0.2e"):
    """Write bin population on top of 2D histogram bins,
       stolen from Nick Amin: https://github.com/aminnj/yahist
       Version from Jonathan Guiang: https://gist.github.com/jkguiang/279cb4d2e68e64148afc62274df09f18
    """
    show_errors = (type(errors) != type(None))
    x_centers = x_edges[1:]-(x_edges[1:]-x_edges[:-1])/2
    y_centers = y_edges[1:]-(y_edges[1:]-y_edges[:-1])/2
    
    if show_errors:
        label_template = r"{0"+fmt+"}\n$\pm{1:0.2f}\%$"
    else:
        errors = np.zeros(counts.shape)
        label_template = r"{0"+fmt+"}"
        
    xyz = np.c_[        
        np.tile(x_centers, len(y_centers)),
        np.repeat(y_centers, len(x_centers)),
        counts.flatten(),
        errors.flatten()
    ][counts.flatten() != 0]

    r, g, b, a = cbar.mappable.to_rgba(xyz[:, 2]).T
    colors = np.zeros((len(xyz), 3))
    colors[compute_darkness(r, g, b, a) > 0.45] = 1

    for (x, y, count, err), color in zip(xyz, colors):
        axes.text(
            x,
            y,
            label_template.format(count, err),
            color=color,
            ha="center",
            va="center",
            fontsize=size,
            wrap=True,
        )

    return

def get_yahist(hist, rebin=1, overflow=True):
    from yahist import Hist1D
    counts = hist.values()
    edges = hist.axis().edges()
    w2 = hist.errors()**2
    if overflow:
        counts[1] += counts[0]
        counts[-2] += counts[-1]
        w2[1] += w2[1]
        w2[-2] += w2[-1]
        counts = np.array(counts[1:-1])
        edges = np.array(edges[1:-1])
        w2 = np.array(w2[1:-1])

    tmp_hist = Hist1D.from_bincounts(counts, edges, np.sqrt(w2), )
    tmp_hist = tmp_hist.rebin(rebin)
    return tmp_hist
