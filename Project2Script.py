import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

#importing the files of counties and citys
counties_gdf = gpd.read_file('C:\\Users\\kevin\\OneDrive\\Documents\\CSC_486_DataMiningMethods\\DataMiningProject2Folder\\cb_2018_us_county_500k\\cb_2018_us_county_500k.shp')
cities_gdf = gpd.read_file('C:\\Users\\kevin\\OneDrive\\Documents\\CSC_486_DataMiningMethods\\DataMiningProject2Folder\\cities\\citiesx010g.shp')
#Changing the column to numeric in order to use the columns numbers
counties_gdf['STATEFP'] = pd.to_numeric(counties_gdf['STATEFP'])

IA_gdf = counties_gdf[counties_gdf['STATEFP'] == 19]
SD_gdf = counties_gdf[counties_gdf['STATEFP'] == 46]
IL_gdf = counties_gdf[counties_gdf['STATEFP'] == 17]
MN_gdf = counties_gdf[counties_gdf['STATEFP'] == 27]
IN_gdf = counties_gdf[counties_gdf['STATEFP'] == 18]
#Merging all the states geodataframes for counties
fivestatescounties_gdf = IA_gdf.append([SD_gdf, IL_gdf, MN_gdf, IN_gdf])

cities_gdf['STATE_FIPS'] = pd.to_numeric(cities_gdf['STATE_FIPS'])

IAc_gdf = cities_gdf[cities_gdf['STATE_FIPS'] == 19]
SDc_gdf = cities_gdf[cities_gdf['STATE_FIPS'] == 46]
ILc_gdf = cities_gdf[cities_gdf['STATE_FIPS'] == 17]
MNc_gdf = cities_gdf[cities_gdf['STATE_FIPS'] == 27]
INc_gdf = cities_gdf[cities_gdf['STATE_FIPS'] == 18]
#Merging all the states geodtaframes for cities
fivestatescity_gdf = IAc_gdf.append([SDc_gdf, ILc_gdf, MNc_gdf, INc_gdf])
#Dropping not needed columns
del cities_gdf['COUNTY']; del cities_gdf['COUNTYFIPS']

#Filting out the rows for when the feature column states "CIVIL"
fivestatescity_gdf = fivestatescity_gdf[fivestatescity_gdf['FEATURE'] == 'Civil']

#Changing to the same epsg for both geodatagrames
counties_projected_gdf = fivestatescounties_gdf.to_crs('epsg:4087')
cities_projected_gdf = fivestatescity_gdf.to_crs('epsg:4087')
#Plotting  the projected and unprojected counties geodtate frames
fivestatescounties_gdf.plot()
counties_projected_gdf.plot()

#Getting teh area of each county
counties_projected_gdf['Area'] = counties_projected_gdf['geometry'].area

#Spacial joining my county and city geodataframes
joined_fivestates_gdf = gpd.tools.sjoin( cities_projected_gdf, counties_projected_gdf, how='right', op='within')

#Printing the top Largest Cities
print('The Top 5 Largest cities')
fivelargecity = joined_fivestates_gdf.sort_values(by=['POP_2010'], ascending=False).iloc[:5]
print(fivelargecity['NAME_left'])

#Getting the people per square meter in each county
joined_fivestates_gdf['PPSM'] = joined_fivestates_gdf['POP_2010']/joined_fivestates_gdf['Area']
peoplepersquaredmeter = joined_fivestates_gdf[['NAME_right','PPSM']]
peoplesquaredmeter = peoplepersquaredmeter.groupby('NAME_right')

#Finding the total population in each county 
print('The population total in each county')
totalpopulation_gdf = joined_fivestates_gdf.groupby('NAME_right')
total = totalpopulation_gdf['POP_2010'].sum()
print (total)

#Counting all the cities/towns within each county
countofcitys = joined_fivestates_gdf.groupby('NAME_right')['NAME_left'].nunique()

#Getting the top five counties in each state
print('Getting the top five counties in each state')
popcountinS = joined_fivestates_gdf[joined_fivestates_gdf['STATE'].isin(joined_fivestates_gdf.groupby('STATE')['POP_2010'].sum().nlargest(5).index)].groupby(['STATE','NAME_right']).sum()['POP_2010'].groupby(level=0, group_keys=False).nlargest(5)
print(popcountinS)


#Getting the top five counties in all five states
print('Getting the top five counties in all fives states') 

topfivecount = joined_fivestates_gdf[joined_fivestates_gdf['NAME_right'].isin(joined_fivestates_gdf.groupby('NAME_right')['POP_2010'].sum().nlargest(5).index)].groupby('NAME_right').sum()['POP_2010'].groupby(level=0, group_keys=False).nlargest(5)
print(topfivecount.nlargest(5))

print('Getting the top five counties in terms of population density') 
topfivecountpop = joined_fivestates_gdf[joined_fivestates_gdf['NAME_right'].isin(joined_fivestates_gdf.groupby('NAME_right')['PPSM'].sum().nlargest(5).index)].groupby('NAME_right').sum()['PPSM'].groupby(level=0, group_keys=False).nlargest(5)
print(topfivecountpop.nlargest(5))


#Plotting based on population density with legend
joined_fivestates_gdf['logPPSM'] = np.log(joined_fivestates_gdf['PPSM'])
joined_fivestates_gdf.plot(column = 'logPPSM',edgecolor = 'black',cmap = 'Reds', legend = True)


