import copy
import pandas as pd
import numpy as np
import copy


def adjust_degradation(pmax, annual_rate = 0):
    #rate_per_hr = (annual_rate)/(365*24)
    if annual_rate == 0:
        return pmax
    rate_per_5min = (annual_rate)/(365*24*12)
    print(f"Adjusting expected power by degradation rate of: {annual_rate*100}%/year...")
    return np.subtract(pmax, rate_per_5min)


def calc_panel_eff(df_cap, area):
    df_cap['panel_eff'] = df_cap['capacity_kW'] / (
            area * df_cap['Panel_number']) #rename park1/2 so both have same
    #panel_eff = round(panel_eff.tail(1).values[0],4) #This is just one value...? Why?
    return df_cap


def calc_pmax(df_env, df_cap, area = None, panel_eff = None, gamma = None):
    area = (1.956 * 0.992) 
    #panel_eff = 0.1572
    temp_std = 25
    gamma = -0.004

    def calc_temp_factor(df_env, temp_std = 25, gamma = -0.004):
        return (1 + (df_env['Temp_P'] - temp_std) * gamma)

    def calc_area(w, l, units = 'm'): #flesh this out; not implemented
        if units == 'm':
            return w*l
        else:
            print("TODO")
            pass
    
    df_cap = calc_panel_eff(df_cap, area)
    df_env['irr_T_adj'] = ((df_env['Irradiance']/1000) * calc_temp_factor(df_env)) #*\
    panel_spec = (df_cap['panel_eff'] * area * df_cap['Panel_number'])

    return [df_env, df_cap, panel_spec]


def filter_saturation(df):
# Calculating periods where inverter output is less than the sum of its strings output (saturation)
    sum_strDF = copy.deepcopy(park1_sub.iloc[:,0])
    #sum the values of strings going to each inverter

    for num in range (1,7): #where is this number coming from? 7 is 5 for park 2
        df= park1_sub.iloc[:,[0,num]]
        colnames=park1_sub.columns
        str_list = colnames[colnames.str.contains('ST '+str(num))]
        df['sum_strings '+str(num)]=park1_sub[str_list].dropna().sum(axis=1)
        df['Input-Output '+str(num)]= df['sum_strings '+str(num)]-df.iloc[:,1] 
        sum_strDF= pd.merge(sum_strDF,df, on= ['datetime'])


    sum_strDF.set_index('datetime', drop=True,inplace=True)
    #Add column for 'saturated' True or False, if sum of strings is greater than output of inverter
    InOut =sum_strDF.columns[sum_strDF.columns.str.contains('Input-Output')]

    saturationDF = sum_strDF.loc[:,InOut]
    saturationDF['saturated']=saturationDF.sum(axis=1)>0
    saturated_dates= saturationDF[saturationDF.saturated==True].index


def calc_efficiency(df_clean, df_cap, degradation_rate):
    df_clean, df_cap, panel_spec = calc_pmax(df_clean, df_cap)
    collist = df_clean.columns
    Inverters = collist[collist.str.contains('Inverter')].to_list()
    strings = collist[collist.str.contains('ST')].to_list()

    columns = [i for i in collist if i.replace('_(kW)', '') in df_cap['displayname']]

    pmax = np.outer(
            np.ma.array(df_clean['irr_T_adj'],
                mask=np.isnan(df_clean['irr_T_adj'])),
            np.ma.array(panel_spec, mask=np.isnan(panel_spec))
            )
    # Adjust max expected power by degradation rate
    pmax_adj = adjust_degradation(pmax, degradation_rate)   
    #
    output = np.ma.array(
            df_clean[columns],
            mask=np.isnan(df_clean[columns])
            )
    df_eff = pd.DataFrame((output / pmax_adj).data)
    df_eff.index = df_clean['datetime']
    df_eff.columns = columns
    return df_eff
