#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import argparse
import logging
import os
import pandas as pd
import wandb


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    artifact_local_path = run.use_artifact(args.input_artifact).file()

    ######################
    df = pd.read_csv(artifact_local_path)

    # Filter dataframe which price between min and max price
    min_price = args.min_price
    max_price = args.max_price
    df = df[df['price'].between(min_price, max_price)].copy()
    logger.info(f"Filter price outliers outside range: {min_price}-{max_price}")
    logger.debug(f"Minimum price after filter: {df['price'].min()}")
    logger.debug(f"Maximum price after filter: {df['price'].max()}")
    
    # Format last_review as datetime format
    df['last_review'] = pd.to_datetime(df['last_review'])
    logger.info("Format last_review to datetime")

    # Save result to csv file
    df.to_csv(args.output_artifact, index=False)
    logger.info(f"Output artifact saved to {args.output_artifact}")

    # Upload to W&B
    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description
    )
    artifact.add_file(args.output_artifact)
    run.log_artifact(artifact)

    artifact.wait()
    logger.info("Cleaned data uploaded to wandb")
    ######################


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")


    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="Input artifact name",
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help="Output artifact name",
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help="Output artifact type",
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help="Output artifact description",
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help="Minimum price accepted",
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=float,
        help="Maximum price accepted",
        required=True
    )

    args = parser.parse_args()

    go(args)