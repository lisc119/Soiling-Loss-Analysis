import pandas as pd
import matplotlib.pyplot as plt
import datetime

#from .apply_filters import add_temporal


def get_sdv_mean_range(df, starttimes, endtime):
    dfnew = pd.DataFrame()
    for start in starttimes:
        df_selected = df.between_time(start, endtime)
        df_resample=df_selected.resample('d')
        df_day_mean=df_resample.mean()
        df_day_std=df_resample.std()
        sdv_mean= df_day_std.mean().mean()
        df_temp=pd.DataFrame({'start':start, 'end':endtime, 'sdv_mean':[sdv_mean]})
        dfnew= pd.concat([dfnew, df_temp], ignore_index=True)
    dfnew.set_index('start', drop=True, inplace=True)
    return dfnew


def get_sdv_mean_range_end(df, starttime, endtimes):
    dfnew = pd.DataFrame()
    for end in endtimes:
        df_selected = df.between_time(starttime, end)
        df_resample=df_selected.resample('d')
        df_day_mean=df_resample.mean()
        df_day_std=df_resample.std()
        sdv_mean= df_day_std.mean().mean()
        df_temp=pd.DataFrame({'start':starttime, 'end':end, 'sdv_mean':[sdv_mean]})
        dfnew= pd.concat([dfnew, df_temp], ignore_index=True)
    dfnew.index=dfnew.end
    return dfnew


def plot_SR(df, year, month,day, starttime, endtime, col):
    df_selected = df[(df.index.year == year)&(df.index.month == month) & (df.index.day == day)].between_time(starttime, endtime)
    plt.plot(df_selected.index, df_selected[col], label = str(year)+'-'+ str(month)+'-'+str(day))
    plt.xticks(rotation='vertical')
    plt.legend()
    plt.show()


def plot_EPI_dpm(df):
    #Visualize EPI over the day by month
    #df = add_temporal(df)
    #df['TimeOfDay']=df.index
    #df['MonthOfYear']=df['TimeOfDay'].apply(lambda x: datetime.strftime(datetime.strptime(str(x),'%Y-%m-%d %H:%M:%S'), '%Y-%m'))
    #df['TimeOfDay']=df['TimeOfDay'].apply(lambda x: datetime.strftime(datetime.strptime(str(x),'%Y-%m-%d %H:%M:%S'), '%H:%M:%S'))
    #df['av_strings']= df.mean(axis=1)

    toplot= df.groupby(['TimeOfDay','MonthOfYear']).mean().unstack()
    toplot.av_strings.plot(figsize=(15,5))
    plt.show()

    plt.hist(toplot.av_strings)
    plt.show()

    toplot[toplot.av_strings<1.2]['av_strings'].plot(figsize=(15,5))
    plt.show()


def plot_EPI_sd_daily_windows(df):
    #Visualise the std of EPI across the day with varying start and end times
    df.index= pd.to_datetime(df.index, format='%Y-%m-%d %H:%M:%S')

    alltimes=df.index.strftime("%H:%M").unique()
    starttimes=alltimes
    endtime = '23:55'

    sdv_starttimes= get_sdv_mean_range(df, starttimes,endtime)
    sdv_starttimes.sdv_mean.plot()
    plt.xticks(rotation='vertical')
    plt.show()

    endtimes= alltimes
    starttime = endtimes[41]
    sdv_endtimes =get_sdv_mean_range_end(df, starttime, endtimes)
    sdv_endtimes.sdv_mean.plot()
    plt.xticks(rotation='vertical')
    plt.show()


def plot_EPI_daily_window(df):
    #Plot EPI over the whole day and chosen time period
    plot_SR(df, 2019,10,31,'08:00','23:55','av_strings')
    plt.show()

    for day in range(1,32):
        plot_SR(df, 2019,9,day,'16:00','18:00','av_strings')
    plt.show()

    for day in range(1,32):
            plot_SR(df, 2019,9,day,'16:00','18:00','av_strings')
    plt.show()

    df_H =df.groupby('H').agg('mean')
    df_H['av_strings'].plot()
    plt.show()


def good_day_filter_plot(df, start_time, end_time):
    
    # pick a specific time period of a day 
    time = [ind for ind in df.index if (ind.hour>=start_time)&(ind.hour<=end_time)]
    
    # aggregate by day and calculate a mean of each string
    df_agg=df.loc[time].resample('d')
    df_string_mean=df_agg.mean()
    
    # calculate mean & std of df_string_mean
    anal = pd.Series(df.values.ravel()).describe()
    mean=anal[1]
    std=anal[2]
    
    # plot histogram of df_string_mean
    ax = df_string_mean.plot.hist(legend=False)
    plt.axvline(mean, color='r', linestyle='dashed', linewidth=2)
    plt.axvline(mean-std, color='b', linestyle='dashed', linewidth=2)
    plt.axvline(mean+std, color='b', linestyle='dashed', linewidth=2)
    plt.figtext(0.99, 0.05, 'mean', horizontalalignment='right', color='r');
    plt.figtext(0.99, 0.01, 'mean±std', horizontalalignment='right', color='b');
    plt.show()


#########################

def yearplot(dataframe, start_time, end_time, x_name='date', y_name='output/calculated', mask=None):
    """creates a line plot with data aggregated by day. Uses a midday-window."""
    
    df_Pavlin=dataframe
    
    #make it work with series and dataframes
    if isinstance(dataframe,pd.Series):
        df_Pavlin=df_Pavlin.to_frame() #cheap trick to turn into frame
        df_Pavlin.rename(columns={0: 'value'}, inplace=True)
    
    data = df_Pavlin
    #set midday mask for aggregating
    time=timemask(df_Pavlin, start_time,end_time) # timewindow that will be plotted
    df_pavlin=df_Pavlin.loc[time].resample('d').median() #
    
    if mask is not None:
        df_pavlin=df_pavlin[mask.sum(axis=1)!=0]

    # stack data
    data=stack(df_pavlin,y_name)

    #cheap hack to define a one-color palette for the individual strings
    colors_hue=list(np.full((400), '#666666'))
    num_colors=data['string'].nunique()
    
    #generate diagram
    plt.figure(figsize=(10, 5))
    sns.set()
    sns.set_style("whitegrid",{'grid.color': '.95',})
    sns.set_palette('dark')
    sns.set_context("poster")
    sns.set_palette(sns.color_palette(colors_hue, num_colors))
    
    g = sns.lineplot(data=data, x=x_name, y=y_name, markers='x',color='red',linewidth=2, alpha=0.8,ci=None,estimator=np.median)

    # define Labels and Axis
    g.set(xlabel='', ylabel=y_name)
    labels=data.index.strftime('%b').unique()
    g.set_xticklabels(labels=labels)

    return data
