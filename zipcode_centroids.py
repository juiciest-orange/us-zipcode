import geopandas as gpd
import pandas as pd
from functools import reduce
import matplotlib.pyplot as plt
from matplotlib import colormaps

# Read Census data
df = gpd.read_file('cb_2020_us_zcta520_500k.zip')

# Remove leading zeroes from MA postal codes
df['ZCTA5CE20'] = df['ZCTA5CE20'].str.lstrip('0')

# Rename ZCTA5CE20 to postal_code
df.rename(columns={'ZCTA5CE20':'postal_code'},inplace=True)
df['postal_code'] = df['postal_code'].astype('str')

# Read in Geonames data
# Leading zeroes already removed
headerNames = ['country_code','postal_code','place_name','admin_name1','admin_code1','admin_name2',
               'admin_code2','admin_name3','admin_code3','latitude','longitude','accuracy']
geonames = pd.read_csv('geonames_postalcode/US/US.txt',sep='\t',names=headerNames, usecols=['postal_code','place_name',
                                                                                            'admin_name2','admin_name1'])
geonames['postal_code'] = geonames['postal_code'].astype('str')

# Population data
popn = pd.read_csv('DECENNIALDHC2020.P1_2025-04-18T172015/DECENNIALDHC2020.P1-Data.csv', header=1)
popn[['Identifier', 'postal_code']] = popn['Geographic Area Name'].str.split(' ', n=1, expand=True)
popn.drop(columns=['Identifier','Unnamed: 3','Geography','Geographic Area Name'],inplace=True)
popn['postal_code'] = popn['postal_code'].astype('str')
popn['postal_code'] = popn['postal_code'].str.lstrip('0')

# Merge
dfs = [df, geonames, popn]
spatial_df = reduce(lambda left, right: pd.merge(left, right, on='postal_code', how='outer'), dfs)

gdf = gpd.GeoDataFrame(spatial_df)
centroids = gdf.to_crs('+proj=cea').centroid.to_crs(gdf.crs) # Project the shapes to a flat surface to get centroid, then convert back to original projection system
gdf['centroid'] = centroids
gdf.dropna(inplace=True)

del(dfs)
del(spatial_df)

def draw_county_figure(county, state):
    fig, ax = plt.subplots()
    
    plt.title(f'{county} County Zipcode Centroids', 
              fontdict={'fontsize': 16, 'fontweight': 'normal'},
              loc='center', 
              pad=10)
    
    
    gdf[(gdf['admin_name2']==f'{county}')&(gdf['admin_name1']==f'{state}')].plot(ax=ax, column=' !!Total', edgecolor='black', 
                                                                                 cmap='viridis', legend=True,
                                                                                 legend_kwds={"label": "Population", 
                                                                                              "orientation": "horizontal"})
    gdf[(gdf['admin_name2']==f'{county}')&(gdf['admin_name1']==f'{state}')]['centroid'].plot(ax=ax, marker='o', color='red', markersize=1)
    
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    file_name = f'{county}_{state}'.replace(' ','_').lower()
    plt.savefig(file_name+'.png', bbox_inches='tight')

def draw_city_figure(city, state):
    fig, ax = plt.subplots()
    
    plt.title(f'{city}, {state} Zipcode Centroids', 
              fontdict={'fontsize': 16, 'fontweight': 'normal'},
              loc='center', 
              pad=10)
    

    gdf[(gdf['place_name']==f'{city}')&(gdf['admin_name1']==f'{state}')].plot(ax=ax, column=' !!Total', edgecolor='black', 
                                                                                 cmap='viridis', legend=True,
                                                                                 legend_kwds={"label": "Population", 
                                                                                              "orientation": "horizontal"})
    gdf[(gdf['place_name']==f'{city}')&(gdf['admin_name1']==f'{state}')]['centroid'].plot(ax=ax, marker='o', color='red', markersize=1)

    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    file_name = f'{city}_{state}'.replace(' ','_').lower()
    plt.savefig(file_name+'.png', bbox_inches='tight')

# draw_county_figure(county='Santa Clara', state='California')
draw_city_figure(city='Boston',state='Massachusetts')