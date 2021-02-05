import argparse
from anbl_scraper.utils.csv_utils import (
    read_product_link_csv,
    write_product_link_csv,
    sillify,
)
from anbl_scraper.models import Product
from tqdm.contrib.concurrent import process_map, thread_map


def scrape(
    input_path, output_path="~/Downloads", max_workers=20, sample_size=None, silly=None
):
    # Read products from input csv
    prod_dicts = read_product_link_csv(input_path)
    products = list(map(Product.from_dict, prod_dicts))

    # Trim list of products if sample_size was provided
    if sample_size is not None and sample_size < len(products):
        products = products[:sample_size]

    # Uses concurrent.futures.TheadPoolExecutor.map() to fetch results
    print(f"Scraping metadata for {len(products)} products.")
    thread_map(lambda p: p.update_metadata(), products, max_workers=max_workers)

    if silly:
        products = sillify(products)

    # Write to file
    write_product_link_csv(
        output_path, [p.to_dict() for p in products], listing_type="scrape"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Using ANBL URLs obtained from a CSV generated by anbl-crawl, fetch each webpage and extract relevant metadata. Prints metadata to a new CSV.",
        epilog="Enjoy responsibly.",
    )
    parser.add_help
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Path to file containing product names and URLs.",
    )
    parser.add_argument(
        "-o",
        "--output-path",
        default="~/Downloads",
        help="Path to output file or directory. Default: %(default)s",
    )
    parser.add_argument(
        "-n",
        "--sample-size",
        type=int,
        help="If provided, scape only the first N items from the CSV.",
    )
    parser.add_argument(
        "-s",
        "--silly",
        type=bool,
        help="Set True if you wanna get a bit silly with things",
    )
    args = parser.parse_args()

    print(f"Running with args: {vars(args)}")
    scrape(
        input_path=args.input,
        output_path=args.output_path,
        sample_size=args.sample_size,
        silly=args.silly,
    )


if __name__ == "__main__":
    main()
