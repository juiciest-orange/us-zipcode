import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

census = gpd.read_file('cb_2020_us_zcta520_500k.zip')
census.rename(columns={'ZCTA5CE20':'postal_code'},inplace=True)

headerNames = ['country_code','postal_code','place_name','admin_name1','admin_code1','admin_name2',
               'admin_code2','admin_name3','admin_code3','latitude','longitude','accuracy']
geonames = pd.read_csv('geonames_postalcode/US/US.txt',sep='\t',names=headerNames, usecols=['postal_code','place_name','admin_name2','admin_name1'])

geonames['postal_code']=geonames['postal_code'].astype('str')
census['postal_code']=census['postal_code'].astype('str')

spatial_df  = geonames.merge(census, on='postal_code', how='left')
gdf = gpd.GeoDataFrame(spatial_df)

del(spatial_df,geonames,census)

centroids = gdf.to_crs('+proj=cea').centroid.to_crs(gdf.crs) # Project the shapes to a flat surface to get centroid, then convert back to original projection system
gdf['centroid'] = centroids

del(centroids)

fig, ax = plt.subplots()

plt.title("Santa Clara County Centroids by Zipcode", 
          fontdict={'fontsize': 16, 'fontweight': 'normal'},
          loc='center', 
          pad=10)


gdf[(gdf['admin_name2']=='Santa Clara')&(gdf['admin_name1']=='California')].plot(ax=ax, color='white', edgecolor='black')
gdf[(gdf['admin_name2']=='Santa Clara')&(gdf['admin_name1']=='California')]['centroid'].plot(ax=ax, marker='o', color='red', markersize=1)

plt.xlabel("Longitude")
plt.ylabel("Latitude")

plt.savefig('figure.png', bbox_inches='tight')