# Airbus OneAtlas API - Python ordering
Python code using [AirBus OneAtlas API](https://www.geoapi-airbusds.com/index.html) to preview and download images clipped to feature extents.  

See [download_images.ipynb](download_images.ipynb) for example process.

The `oneatlas` Python module in this repo started out as the [OneAtlas example](https://www.geoapi-airbusds.com/guides/python-client/) but extra functions were added to easily extract and print relevant image information and plot the quicklook image. This makes it easier to decide which image to order for download. 

Using this process it is possible to view the quicklook and get a price quotation before place an order and spend anything.

Set your api key and output folder location in `config.json`. This config file is included in `.gitignore` to prevent risk of pushing your api key.
