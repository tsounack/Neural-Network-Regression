import pandas as pd

def create_dataframes():
    # Extract Satellite Data
    sat_data = pd.read_csv("A_ERA.csv", sep=",", index_col=0, parse_dates=True)
    sat_data.index = pd.to_datetime(sat_data.index)
    sat_data.drop(["longitude", "latitude"], axis=1, inplace=True)
    sat_data.dropna(inplace=True)

    # Extract Buoy Data
    buoy_data = pd.read_csv("A_MeteoStation_Data.csv", sep=";", index_col=0, parse_dates=True)
    buoy_data = buoy_data.loc[:,["wind_speed [m/s]", "air_temperature [ｰC]", "wind_direction [ｰ]"]]
    buoy_data.index = pd.to_datetime(buoy_data.index)
    buoy_data = buoy_data.groupby(pd.Grouper(freq="1h")).mean()
    buoy_data.dropna(inplace=True)
        
    # Extract Anemometer Data
    df_temp = buoy_data.merge(sat_data, right_index=True, left_index=True)
    df_temp.dropna(inplace=True)
    df_subtract = df_temp["air_temperature [ｰC]"].subtract(df_temp["sst"]) + 273.15
    anemo_data = pd.DataFrame([df_temp["wind_speed [m/s]"], df_temp["wind_direction [ｰ]"], df_subtract]).transpose()
    anemo_data.columns = ["WS", "Wdir", "Delta T"] 

    df_temp_lidar = pd.read_csv("A_Wind_Data.txt", sep="\t", parse_dates=True, index_col=0)
    df_temp_lidar = df_temp_lidar.loc[:,df_temp_lidar.columns.str.contains("wind_speed ")]
    df_temp_lidar = df_temp_lidar.groupby(pd.Grouper(freq="1h")).mean()
    df_temp_lidar.dropna(inplace=True)


    heights_A = [40,57,77,97,117,137,157,177,197]
    regex = ""
    for i in range(len(heights_A)):
        z = heights_A[i]
        regex += str(z)
        if i!=len(heights_A)-1:
            regex += "|"

    lidar_data = df_temp_lidar.filter(regex=regex)
    lidar_data.columns = [f"WS {z}m" for z in heights_A]

    df_temp_X = anemo_data.merge(sat_data, right_index=True, left_index=True)
    df_temp_X["month"] = df_temp_X.index.month
    df_temp_X = df_temp_X[df_temp_X["WS"] != 0]
    df_temp_X.dropna(inplace=True)

    df_temp_y = lidar_data.groupby(pd.Grouper(freq="1h")).mean()        
    df_temp_y.dropna(inplace=True)

    df_temp_Xy = df_temp_X.merge(df_temp_y, right_index=True, left_index=True)
    df_temp_Xy.dropna(inplace=True)
    df_temp_Xy = df_temp_Xy.sample(frac=1)

    Xy_data = df_temp_Xy
    X_data = df_temp_Xy.loc[:, ~df_temp_Xy.columns.str.contains("WS ")]
    y_data = df_temp_Xy.loc[:, df_temp_Xy.columns.str.contains("WS ")]

    return X_data, y_data