"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referendum/regions/departments."""
    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv("data/regions.csv", sep=",")
    departments = pd.read_csv("data/departments.csv", sep=",")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions = load_data()[1]
    departments = load_data()[2]
    fusion = pd.merge(departments, regions,
                      left_on="region_code", right_on="code", how="left")
    fusion = fusion.drop(columns=['id_x', 'region_code',
                                  'slug_x', 'id_y', "slug_y"])
    fusion = fusion.rename(columns={"code_y": "code_reg",
                                    "code_x": "code_dep",
                                    "name_x": "name_dep",
                                    "name_y": "name_reg"})
    fusion = fusion[['code_reg', 'name_reg', 'code_dep', 'name_dep']]
    return fusion


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """
    ref = load_data()[0]
    regions = load_data()[1]
    departments = load_data()[2]
    reg_and_dep = merge_regions_and_departments(regions, departments)
    ref["Department code"] = pd.to_numeric(ref["Department code"],
                                           errors="coerce"
                                           ).fillna(ref["Department code"]
                                                    ).astype(str)
    reg_and_dep["code_dep"] = pd.to_numeric(reg_and_dep["code_dep"],
                                            errors="coerce"
                                            ).fillna(reg_and_dep["code_dep"]
                                                     ).astype(str)

    fusion = pd.merge(referendum,
                      reg_and_dep, left_on="Department code",
                      right_on="code_dep", how="left")
    fusion = fusion[-fusion["Department code"].str.startswith("Z")]

    return fusion


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum = load_data()[0]
    regions = load_data()[1]
    departments = load_data()[2]
    reg_and_dep = merge_regions_and_departments(regions, departments)

    ref_and_areas = merge_referendum_and_areas(referendum, reg_and_dep)
    reg = ref_and_areas.groupby('name_reg')
    [["Registered", 'Abstentions',
        'Null', 'Choice A', 'Choice B']].sum().reset_index()

    return reg


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    referendum = load_data()[0]
    regions = load_data()[1]
    departments = load_data()[2]
    reg_and_dep = merge_regions_and_departments(regions, departments)
    ref_and_areas = merge_referendum_and_areas(referendum, reg_and_dep)
    ref_res_by_regions = compute_referendum_result_by_regions(ref_and_areas)
    gdf = gpd.read_file("data/regions.geojson")

    fusion = pd.merge(gdf, ref_res_by_regions,
                      left_on="nom", right_on="name_reg", how="left")
    fusion['rate'] = fusion['Choice A']/(fusion['Choice B']+fusion['Choice A'])
    fusion = gpd.GeoDataFrame(fusion)

    ax = fusion.plot(
            column='rate',
            cmap='OrRd',
            legend=True,
            edgecolor='black',
            figsize=(10, 6),
            legend_kwds={
                'label': "Proportion de votes pour le 'Choice A' "
                "(par rapport aux votes exprimés)",
                'orientation': "vertical",
                'shrink': 0.8
            }
        )

    ax.set_title("Résultats du référendum par région", fontsize=14, pad=15)
    return fusion


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
