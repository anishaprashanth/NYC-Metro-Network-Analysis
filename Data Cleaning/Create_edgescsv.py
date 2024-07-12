
import pandas as pd
data = pd.read_csv("/Users/yujiaxi/Desktop/Network/FinalProject/MTA_Subway_Stations_20231102.csv")
data.columns = data.columns.str.replace(" ","_")
data['Stop_Name_Next'] = data['Stop_Name'].shift(1)
data['Georeference_Next'] = data['Georeference'].shift(1)
data['Complex_ID_Next'] = data['Complex_ID'].shift(1)
data['GTFS_Latitude_Next'] = data['GTFS_Latitude'].shift(1)
data['GTFS_Longitude_Next'] = data['GTFS_Longitude'].shift(1)
data['C'] = data.groupby(['Daytime_Routes']).cumcount()+1
data = data[['Daytime_Routes','Complex_ID','Complex_ID_Next','GTFS_Latitude_Next','GTFS_Longitude_Next','GTFS_Latitude','GTFS_Longitude','Stop_Name','Stop_Name_Next']]
data.to_csv("/Users/yujiaxi/Desktop/Network/FinalProject/edges_new.csv")
