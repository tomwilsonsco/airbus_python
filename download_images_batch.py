from oneatlas import OneAtlasClient  # custom class in this repo
import json
import geopandas as gpd
from shapely.geometry import box
from pathlib import Path
import shutil
import zipfile
import time
import argparse
from datetime import datetime


# Define function to convert points -> buffer -> bounding box
def points_to_buffer_box(gdf, buffer_distance=500):
    """Buffer points by distance and convert to bounding boxes"""
    # Check if all geometries are Points
    if not all(gdf.geometry.geom_type == "Point"):
        print("All geometries in the GeoDataFrame must be Points. Exiting.")
        return None
    # Reproject to EPSG 27700
    gdf = gdf.to_crs(epsg=27700)
    # Buffer the geometries
    gdf["geometry"] = gdf.geometry.buffer(buffer_distance)
    # Convert buffers to bounding boxes
    gdf["geometry"] = gdf.geometry.apply(lambda geom: box(*geom.bounds))
    return gdf


def aoi_gdf_to_search_geojson(gdf, uid_column=None):
    """Convert geodataframe to geojson ensuring unique ids per feature"""
    if uid_column is None:
        uid_column = "id"
        gdf[uid_column] = gdf.index
    else:
        if not gdf[uid_column].is_unique:
            raise ValueError(
                f"Values in '{uid_column}' are not unique. Consider using default uid_column=None to add uids."
            )
    json_str = gdf[[uid_column, "geometry"]].to_crs(epsg=4326).to_json(drop_id=True)
    return json.loads(json_str), gdf[uid_column].tolist()


def get_feature_by_id(geojson, id_vals, search_id, uid_column="id"):
    """Filter geojson features to just one specified id"""
    if search_id not in id_vals:
        raise ValueError(f"id {search_id} not in list of id values")
    for feature in geojson["features"]:
        if feature["properties"][uid_column] == search_id:
            return feature
    return None


def process_zip_file(zip_file_path, target_directory, delete_zip=True):
    """Extract largest tif image from zip and store in local directory"""
    zip_file_path = Path(zip_file_path)
    target_directory = Path(target_directory)
    # Extract the ZIP file
    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        temp_extract_dir = zip_file_path.parent / "temp_extracted"
        zip_ref.extractall(temp_extract_dir)
    # Find the largest .tif file
    largest_tif_file = None
    largest_size = 0
    for file in temp_extract_dir.rglob("*.TIF"):
        if file.stat().st_size > largest_size:
            largest_tif_file = file
            largest_size = file.stat().st_size
    if largest_tif_file is not None:
        # Copy it to the target directory with _<number> appended to the file name
        number_suffix = zip_file_path.stem.split("_")[-1]
        new_file_name = (
            largest_tif_file.stem + f"_{number_suffix}" + largest_tif_file.suffix
        )
        target_file_path = target_directory / new_file_name
        shutil.copy(largest_tif_file, target_file_path)
        # Delete the extracted ZIP file and temporary directory
        shutil.rmtree(temp_extract_dir)
        if delete_zip:
            zip_file_path.unlink()
        print(f"extracted {target_file_path}")
    else:
        print("No .tif files found in the ZIP archive.")


def sift_images(images):
    # Sort images by acquisition date in descending order to get the most recent first
    images_sorted_by_date = sorted(
        images,
        key=lambda x: datetime.strptime(x["acquisition_date"], "%Y-%m-%dT%H:%M:%S.%fZ"),
        reverse=True,
    )

    # Extract the most recent image's id
    most_recent_image_id = images_sorted_by_date[0]["image_id"]

    # If there is only one image in the list, return its id only
    if len(images) == 1:
        return [most_recent_image_id]  # Only one image id to return

    # Otherwise, find the image with the least cloud cover, excluding the most recent image
    # Sort images by cloud cover, excluding the most recent image
    images_sorted_by_cloud_cover = sorted(
        images_sorted_by_date[1:], key=lambda x: x["cloud_cover"]
    )

    # Extract the image id with the least cloud cover
    least_cloud_cover_image_id = (
        images_sorted_by_cloud_cover[0]["image_id"]
        if images_sorted_by_cloud_cover
        else None
    )

    return [most_recent_image_id, least_cloud_cover_image_id]


def main(buffer_distance=750, id_start=1, id_end=None):
    # Read local config.json to get api key and directory for outputs
    with open("config.json", "r") as file:
        config = json.load(file)

    api_key = config["api_key"]

    client = OneAtlasClient(api_key=api_key)

    output_folder = Path(config["output_dir"])
    input_file_gdb = Path(config["input_gdb"])

    # function to convert polygon gdf to bounding box list
    sites_gdf = gpd.read_file(input_file_gdb, layer="Registered_Sites_Merged_v2")

    # Drop rows with 'POINT EMPTY' geometry
    sites_gdf = sites_gdf[~sites_gdf.geometry.is_empty]

    # convert points geometry to bounding box around 500m buffer
    sites_box_gdf = points_to_buffer_box(sites_gdf, buffer_distance=1000)

    search_geojson, id_vals = aoi_gdf_to_search_geojson(
        sites_box_gdf, uid_column="image_id"
    )

    # Allow limits to image_id range processed
    id_vals = [i for i in id_vals if i >= id_start]
    if id_end is not None:
        id_vals = [i for i in id_vals if i <= id_end]
    print(f"processing ids {id_vals[0]} to {id_vals[-1]}")
    for id in id_vals:
        print(f"id {id}....")
        # extract the geojson feature for that id
        search_feature = get_feature_by_id(
            search_geojson, id_vals, id, uid_column="image_id"
        )

        # create search json - geometry is the search feature geometry
        img_search_json = {
            "cloudCover": "[0,30]",
            "incidenceAngle": "[0,40]",
            "processingLevel": "SENSOR",
            "relation": "contains",
            "geometry": search_feature["geometry"],
            "constellation": "PHR",
        }

        # make the request
        results = client.search(img_search_json)

        # extract relevant values from the results and store in client instance

        client.extract_results(results)

        if client.result_data:
            image_refs = sift_images(client.result_data)
            print(f"image_ids {", ".join(image_refs)} to order")
            for i, img_ref in enumerate(image_refs):
                print(f"ordering {img_ref}...")
                order_body = {
                    "kind": "order.data.product",
                    "products": [
                        {
                            "productType": "pansharpened",  # pansharpened # multiSpectral
                            "radiometricProcessing": "DISPLAY",  # REFLECTANCE # DISPLAY #
                            "imageFormat": "image/geotiff",
                            "crsCode": "urn:ogc:def:crs:EPSG::32630",  # UTM zone for Scotland
                            "id": img_ref,
                            "aoi": search_feature["geometry"],
                        }
                    ],
                }

                # Add a ref to identify the order
                order_ref = f"sg_quarry_{id}_{i + 1}"

                order_body["customerRef"] = order_ref

                client.get_price(order_body)["price"]

                client.create_order(order_body)

                status = ""
                while status != "delivered":

                    orders = client.list_orders(customerRef=order_ref)

                    order = orders["items"][0]

                    status = order["status"]
                    time.sleep(10)

                # The config.json in the repo specifies the output_folder (I'm using _PS if pan-sharpened)
                output_file = output_folder / f"sg_quarry_PS_{id}.zip"

                # Download the order to specified zip file
                client.download_order_to_file(order, output_file)

                process_zip_file(output_file, output_folder / "extracted_images")


if __name__ == "__main__":
    # Create the parser
    parser = argparse.ArgumentParser(
        description="Process satellite images based on given parameters."
    )

    # Add arguments with short and long options
    parser.add_argument(
        "-b",
        "--buffer_distance",
        type=int,
        default=750,
        help="Buffer distance for the bounding box in meters.",
    )
    parser.add_argument(
        "-s", "--id_start", type=int, default=1, help="Start ID for processing images."
    )
    parser.add_argument(
        "-e",
        "--id_end",
        type=int,
        default=None,
        help="End ID for processing images (optional).",
    )

    # Parse the arguments
    args = parser.parse_args()

    # Call the main function with the parsed arguments
    main(
        buffer_distance=args.buffer_distance, id_start=args.id_start, id_end=args.id_end
    )
