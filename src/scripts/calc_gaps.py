import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

# Get times that fall within one SD of mean in distribution
def get_1sd_times(df_std, sd = 1):
    mean = df_std.mean()
    lb = mean - (df_std.std() * sd)
    ub = mean + (df_std.std() * sd)
    try: 
        temp = df_std.to_frame()
    except:
        temp = df_std
        pass
    ideal_times = (temp[(temp[temp.columns[0]] >= lb) & (temp[temp.columns[0]] <= ub)].index.to_list())
    worst_times = [i for i in temp.index if i not in ideal_times]
    return [ideal_times, worst_times]


def is_date_consecutive(datetimes):
    print(type(datetimes[0])) #make sure type is right or else pd.to_datetime()
    current_date = 0
    current_hour = 0
    last_day = 0
    last_hour = 0
    start = True
    stop = False
    #gaps = {i:{"start":0,"stop":0} for i in len("something")}
    gaps = {}
    try:
        for timestamp in range(len(datetimes)):
            current_date = datetimes[timestamp].date()
            current_hour = datetimes[timestamp].hour
            print(datetimes[timestamp], datetimes[timestamp].date(),datetimes[timestamp].hour)

            if stop is True:
                start = True
                stop = False
            print(current_date, current_hour, start, stop)

            if start is True:
                #start_date = current_date
                print("FIRST")
                gaps[current_date] = []#{"hours":[], "last":""}
                start = False
                pass
            if start is False and gaps[current_date] is not None:
                #print("Not last")
                if timestamp < len(datetimes) - 1:
                        #print(timestamp, len(datetimes))
                    #print("YES")
                    if datetimes[timestamp+1].date() != current_date:
                        print("Current:", gaps[current_date])
                        gaps[current_date].append(current_hour)#["hours"].append(current_hour)
                        #gaps[current_date]["last"] = current_date
                        stop = True
                        print("END")
                                #start = False
                    else:
                        print("CONT.")
                        gaps[current_date].append(current_hour)#["hours"].append(current_hour)
                        stop = False
                    #if datetimes[timestamp].date() current_date


            print(current_date, current_hour, start, stop, "\n", gaps[current_date], "\n\n")
    except AttributeError:
        print(gaps)
    else:
        return gaps


def find_gaps(df, sd_axis = 1):
    #df = df.mean(axis = 1) #mean of all strings
    best_hours, worst_hours = get_1sd_times(df.std(axis = sd_axis)) # for >hourly e.g. dail
    dip_dict = is_date_consecutive(sorted(worst_hours))

    ###SINGLE STRING ONLY
    lists = sorted(dip_dict.items()) # sorted by key, return a list of tuples

    x, y = zip(*lists) # unpack a list of pairs into two tuples
    #x = [str(i) for i in x]
    y = [len(i) for i in y]
    #plt.figure(figsize = (20,5))
    #hist,bins=np.histogram(y)
    #hist = hist[hist>0]
    #bins = np.array(range(1,6))

    ### MEAN OF ALL STRINGS
    by_month = [i.strftime("%Y:%m") for i in x]
    count_dict = {i:{k:0 for k in set(y)} for i in set(by_month)}
    for i,j in zip(by_month, y):
        count_dict[i][j] += 1

    vals = [list(i.values()) for i in count_dict.values()]
    return [(best_hours, worst_hours), (x,y), count_dict, vals]


def plot_gaps(df = None, y = None, count_dict = None, vals = None):
    ####AVERAGE OF ALL
    if df is not None:
        hours, coord, count_dict, vals = find_gaps(df)
        y = coord[1]
    fig, ax = plt.subplots(figsize = (15,10))
    #ax.bar(bins, hist, align="center")
    fig.suptitle("Distribution of drops/spikes by date", fontsize = 25)
    plt.style.use('seaborn-notebook')

    counts = pd.Series(y).value_counts()
    cmap = sns.color_palette("tab20").as_hex()
    bottom_dict = {}
    #counts[j+1] - vals[i][j]
    #vals = ([list(i.values()) for i in count_dict.values()])
    for i in range(len(vals)):
        #for j in range(0,6):
        for j in range(len(vals[0])):
            if i == 0:
                bottom_dict[j] = []
            if j == 0:
                bottom = 0
            if i>0:
                bottom = sum(bottom_dict[j])
            #print(bottom)
        #print(i+1, "-", j+1, "-", list(count_dict.keys())[i],"===", vals[i][j])
            plt.bar(str(j), vals[i][j],align="center",
                    color = cmap[i],
                    alpha = 0.7,
                    bottom=bottom,
                    label = list(count_dict.keys())[i] if j == 0 else "")
            bottom_dict[j].append(vals[i][j])
    #print('\n')

    #ax.bar([i.strftime("%Y:%m") for i in x],y, align="center")
#plt.bar(bins[:-1], hist, width=(bins[-1]-bins[-2]), align="edge")
    leg = ax.legend(title="Dates",loc='best', bbox_to_anchor=(1.2, 1), fontsize=20)
    leg.get_title().set_fontsize('24')
    ax.set_xlabel("Length of drop/spike (in hours)").set_fontsize(20)
    ax.xaxis.set_tick_params(labelsize=22)
    ax.yaxis.set_tick_params(labelsize=15)
    ax.set_ylabel("# of drops/spikes").set_fontsize(22)
    plt.show()



