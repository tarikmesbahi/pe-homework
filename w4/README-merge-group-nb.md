---
jupytext:
  encoding: '# -*- coding: utf-8 -*-'
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.19.5
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# merge, group, pivot and plot

```{admonition} to download
:class: warning

to work on this assignment locally, {download}`start by downloading the zip<./ARTEFACTS-merge-group.zip>`
```

In this assignment we study how **health and wealth** relate across the world, using indicators published by the World Bank. The data comes in several separate files, so we will

* **merge** them into a single, clean dataframe
* **group** and **pivot** the result
* see how a pivot table relates to `groupby` + `unstack`
* **plot** with `df.plot()` and with seaborn's `pairplot`

```{code-cell} ipython3
import numpy as np
import pandas as pd
import seaborn as sns
```

```{code-cell} ipython3
# optional
import itables
itables.init_notebook_mode()
```

## the data

+++

there are four files in the `data/` folder

| file | one row per | main column |
|-|-|-|
| `life-expectancy.csv` | country and year | `life_exp` (years) |
| `gdp-per-capita.csv` | country and year | `gdp_per_capita` (current US$) |
| `population.csv` | country and year | `population` |
| `countries.csv` | country | `region`, `income_level` |

+++

### loading

+++

load each of the four files into a dataframe, named respectively `life`, `gdp`, `pop` and `countries`  
and have a look at each of them: shape, first rows, types

```{code-cell} ipython3
:tags: [level_basic]

life = pd.read_csv("data/life-expectancy.csv")
gdp = pd.read_csv("data/gdp-per-capita.csv")
pop = pd.read_csv("data/population.csv")
countries = pd.read_csv("data/countries.csv")

print("------Life------")
print(life.shape)
print(life.dtypes)
print(life.head(2))

print("------GDP-----")
print(gdp.shape)
print(gdp.dtypes)
print(gdp.head(2))

print("------POP------")
print(pop.shape)
print(pop.dtypes)
print(pop.head(2))

print("------COUNTRIES------")
print(countries.shape)
print(countries.dtypes)
print(countries.head(2))
```

### content

to better understand what we have at hand, answer these questions

1. how many rows do we have in each table
2. the three indicator files have the same columns `country_code`, `country`, `year`  
   what are the rows that identify a measure uniquely ? so, what are the **two columns** we need to merge on ?

:::{admonition} hint
:class: tip dropdown

now could be the right time to check for `df.duplicated()`
:::

```{code-cell} ipython3
print(f"Rows:\nPop: {pop.shape[0]}\nLife: {life.shape[0]}\nGdp: {gdp.shape[0]}")
print("Rows to merge on: \"country_code\", \"year\"")
```

## merging

+++

### how many rows for the merge ?

+++

we're trying to foresee how many rows a merge would yield

the three files do not have the same number of rows: what does that tell you ?  
it is not enough to conclude by itself, we need to know how the keys of the 3 dataframes compare:

1. how do the keys of `life` and `pop` compare ?
2. same question for `life` and `gdp` ?
3. and so, how many rows do you expect from an inner merge
4. and from an outer merge ? how many undefined data will the outer merge contain ?

:::{admonition} hint
:class: tip dropdown

a common trick is to:
- compute the index made of the key columns:
```python
keys = df.set_index([..., ...]).index
```

- and then use set-like operations (`difference`, `intersection`, `union`) on these keys;
- note however that `==` to compare 2 indexes **is not the right tool here**
consider using `symmetric_difference()` instead
:::

```{code-cell} ipython3
:tags: [level_basic]

keys = ["country_code", "year"]
k_life = life.set_index(keys).index
k_gdp = gdp.set_index(keys).index
k_pop = pop.set_index(keys).index

print(f"Dans life et pas dans pop: {k_life.difference(k_pop)}")
print(f"Dans pop et pas dans life: {k_pop.difference(k_life)}")

print(f"Dans life et pas dans gdp: {k_life.difference(k_gdp)}")
print(f"Dans gdp et pas dans life: {k_gdp.difference(k_life)}")

print(f"Attendu après inner merge: {k_life.shape[0] - len(k_life.difference(k_gdp))}")

k_inner = k_life.intersection(k_gdp).intersection(k_pop)
print(k_inner.shape[0])

print(f"Attendu après inner merge {k_life.shape[0] - len(k_gdp.difference(k_life))}")

k_outer = k_life.union(k_pop).union(k_gdp)
print(k_outer.shape[0])
```

### merging the indicators

+++

merge `life`, `gdp` and `pop` into a single dataframe `indicators`, with **these 6 columns**

`country_code, country, year, life_exp, gdp_per_capita, population`

do this twice:

1. once with the default merge,
2. and once with `how="outer"`
3. compare the number of rows with the expectations
4. finally check for missing data in both; does that add up with the previous question ?

:::{admonition} hint
:class: tip dropdown

the `country` column is already in `life`, so you do not want to get it again from the other dataframes
:::

```{code-cell} ipython3
:tags: [level_basic]

new_cols = ["country_code", "country", "year", "life_exp", "gdp_per_capita", "population"]

indicators_inner = life.merge(gdp, on=keys).merge(pop, on=keys)[new_cols]
print(indicators_inner.shape[0])
print(indicators_inner.head(2))

indicators_outer = life.merge(gdp, on=keys, how="outer").merge(pop, on=keys, how="outer")[new_cols]
print(indicators_outer.shape[0])
print(indicators_outer.head(2))

print(f"Missing inner:\n {indicators_inner.isna().sum()}")
print(f"Missing outer:\n {indicators_outer.isna().sum()}")
```

which kind of merge one do you prefer here, and why ?  
(for the rest of the assignment, we keep the outer version, to see the missing values)

+++

### adding the regions

+++

now we want to add the `region` and `income_level` columns to `indicators`, taken from `countries`  
this time we merge on one column only: `country_code`

1. how many rows do you expect in the result ?  
   (for a given country, is there one row or several in the `countries` table ?)
2. merge, and call the result `df`; check that you get the number of rows you expected
3. you now have both a `country` and a `name` column, that seem to contain the same thing;
  (optional step) double-check they genuinely are identical
4. drop the `name` column

:::{admonition} hint
:class: tip dropdown
maybe `Series.is_unique` can come in handy
:::

```{code-cell} ipython3
:tags: [level_basic]

indicators = indicators_outer

print(f'"country_code" unqiue ? {countries["country_code"].is_unique}')

df = indicators.merge(countries, on="country_code")

print(f"Rows: {df.shape[0]}")
print(df.head(2))

print("-------------")

print(f'Country == Name ? {(df["country"] == df["name"]).all()}')
print(f'Country == Name ? {df["country"].equals(df["name"])}')

df = df.drop(columns="name")

print(df.head(2))
```

### cleaning

+++

1. look at the values in the `region` column: `value_counts()` should show you something that is not a region
2. look at some entries in this category, to check it's safe to remove
3. remove those entries

:::{admonition} hints
:class: tip dropdown

- in the World Bank data, groups like *World* or *Euro area* are mixed with actual countries; they have a `region` of `"Aggregates"`
- maybe time to check for `df.sample()`
:::

```{code-cell} ipython3
:tags: [level_basic]

print(df["region"].value_counts())

mask_aggregates = df["region"] == "Aggregates"

print(df.loc[mask_aggregates, ["country"]].head(2))

df = df.loc[~mask_aggregates].copy()

print(df["region"].value_counts())
```

### computing decade

+++

as we have not yet seen how to deal with time-related data, we will
add a column `decade` (like 1990, 2000, 2010, 2020) computed from `year` as an integer

:::{admonition} hint
:class: tip dropdown

the integer division `//` can help to compute the decade
:::

```{code-cell} ipython3
:tags: [level_basic]

df["decade"] = (df["year"] // 10) * 10

print(df.head(2))
```

## groupby

+++

```{admonition} simple averages ?
:class: warning

for the sake of simplicity, we will compute means as a simple average over **countries**, so a small island weighs as much as India  
it is fine for an exercise, but of course it is not the life expectancy of the people living in a region  

see the appendix on weighting by population for a better way
```

1. compute the average life expectancy for each region
2. then do the same for each pair `(region, decade)`
3. what is the type of the index of this last result ?
4. look at the `levels` attribute of this index; what do you find in there ?

```{code-cell} ipython3
:tags: [level_basic]

print(df.groupby("region")["life_exp"].mean())

print("\n---------------\n")

gb_lifeexp = df.groupby(["region", "decade"])["life_exp"].mean()

print(gb_lifeexp)

print("\n---------------\n")

print(type(gb_lifeexp.index))

print(gb_lifeexp.index.levels)
```

## pivot_table

+++

build a table with one row per region, one column per decade, and the average life expectancy in each cell

```{code-cell} ipython3
:tags: [level_basic]

pivoted = df.pivot_table(index="region", columns="decade", values="life_exp")

print(pivoted)
```

## stack and unstack

+++

you have just seen two ways to compute almost the same thing: the 2-level `groupby` result, and the pivot table  
use `unstack()` on the former to obtain the latter, and check that they are equal  
(see also `DataFrame.equals`, or `pd.testing.assert_frame_equal`)

```{code-cell} ipython3
:tags: [level_basic]

unstacked = gb_lifeexp.unstack()

print(unstacked.equals(pivoted))

pd.testing.assert_frame_equal(unstacked, pivoted)
```

and conversely, what does `stack()` do when applied on the pivot table ?

```{code-cell} ipython3
:tags: [level_basic]

stacked = pivoted.stack()

print(stacked.head(2))
print(stacked.equals(gb_lifeexp))

#pd.testing.assert_frame_equal(stacked, gb_lifeexp)
```

so, in a nutshell: `pivot_table(index=A, columns=B, values=C)` is the same as `groupby([A, B])[C].mean().unstack()`  
(and the pivot table can do more, e.g. several aggregation functions or `margins=True`)

+++

## plotting with pandas

+++

```{admonition} the reflex
:class: tip

pandas dataframes and series know how to draw themselves: `df.plot()`  
so the idea is to **prepare the dataframe** so that its shape fits what you want to see, rather than loop on `plt` calls
```

+++

1. use `pivoted` to draw one curve per region, showing how the life expectancy evolves over decades  
the result should look like this

:::{image} media/lines.svg
:width: 600px
:align: center
:::

:::{admonition} hint
:class: tip dropdown

`df.plot()` draws one curve per column, with the index on the x axis; so you may need to transpose first
:::

```{code-cell} ipython3
:tags: [level_basic]

pivoted.T.plot()
```

2. now a bar chart (`kind="barh"` or `df.plot.barh()`) of the average life expectancy per region for the most recent decade only (the column `2020`)

```{code-cell} ipython3
:tags: [level_basic]

pivoted.loc[:,2020].plot.barh()
```

3. finally, a scatter plot of `life_exp` against `gdp_per_capita` for year 2019, using `df.plot.scatter()`  
use a log scale on the x axis (`logx=True`) to make it readable

```{code-cell} ipython3
:tags: [level_basic]

df.loc[df["year"] == 2019].plot.scatter(x="gdp_per_capita", y="life_exp", logx=True)
```

## pairplot

+++

seaborn's `pairplot()` draws, for a set of numerical columns:
- the histogram of each column (on the diagonal), and
- the scatter plot of every pair

see [this page for a short intro to seaborn](https://numerique.info-mines.paris/seaborn-intro-nb/)

1. on the 2019 data, draw a `pairplot` of the columns `life_exp`, `gdp_per_capita` and `population`, with a color per `region`  
2. the result is not very readable; why ?
   try to fix this by using the logarithm of the two last columns (`numpy.log10`)

you should produce something like this:

:::{image} media/pairplot.svg
:width: 600px
:align: center
:::

```{code-cell} ipython3
:tags: [level_basic]

#??
```

## optional: going further

+++

how many countries are there in each (region, income level) pair ?  
build the table with one row per region, one column per income level, and add the totals with `margins=True`

:::{admonition} hint
:class: tip dropdown

here you want to **count** *different* countries: look at `nunique()` as an aggregation function  
and what about regions that have no country in some income level ?
:::

```{code-cell} ipython3
:tags: [level_basic]

# your code
```

## appendix: weighting by population

+++

in the `groupby` section, we have computed the mean over countries  
to get the life expectancy of the people of a region, each country should be weighted by its population

there is no weighted mean in `groupby`, but a weighted mean is `sum(life_exp * population) / sum(population)`  
so compute these two sums by (region, decade), and divide them

:::{admonition} hint
:class: tip dropdown

- first build the product `life_exp * population`, e.g. with `assign()`
- rows where `life_exp` or `population` is missing must be removed first; otherwise, the two sums do not cover the same countries
- the result can be reshaped with `unstack()` to look like `pivoted`
:::

```{code-cell} ipython3
:tags: [level_basic]

# your code
```

## appendix: where does the data come from

+++

all the data was downloaded once from the [World Bank open data API](https://datahelpdesk.worldbank.org/knowledgebase/topics/125589), restricted to the years 1990 to 2020

* life expectancy at birth: indicator `SP.DYN.LE00.IN`
* GDP per capita, current US$: indicator `NY.GDP.PCAP.CD`
* total population: indicator `SP.POP.TOTL`
* country metadata (region, income level): the `country` endpoint

for example, with [httpie](https://httpie.io/), the life expectancy for all countries, in 2019 only, as json (`format==json` and the other `==` are query parameters)

```bash
http "https://api.worldbank.org/v2/country/all/indicator/SP.DYN.LE00.IN" format==json date==2019 per_page==300
```

for the years used here, replace the date with `date==1990:2020`, and use `per_page==20000` to get everything in one page  
the country metadata is at `https://api.worldbank.org/v2/country`  
the script `fetch-data.py`, next to this notebook, does the whole job with Python's `requests` library instead

rows with no value were dropped from the three indicator files, which is why they do not all cover the same country / year pairs
