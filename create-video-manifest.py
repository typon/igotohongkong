import json
import math
import datetime
from pysubparser import parser
import click
import sys
import unicodedata
import re


def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


def get_microseconds(t):
    return (
        (t.hour * 3600 * 1000_000)
        + (t.minute * 60 * 1000_000)
        + (t.second * 1000_000)
        + t.microsecond
    )


@click.command()
@click.option("--sub-file", type=click.File("r"), required=True)
@click.option("--output-manifest-file", type=click.File("w"), required=True)
def cli(sub_file, output_manifest_file):
    subtitles = parser.parse(sub_file.name)

    output_json = []
    for subtitle in subtitles:
        start_time = get_microseconds(subtitle.start)
        end_time = get_microseconds(subtitle.end)
        length = end_time - start_time

        length_in_seconds = math.ceil(length / 1000_000)
        start_time_in_seconds = math.floor(start_time / 1000_000)

        clip_filename = f"{slugify(subtitle.text)}-{start_time_in_seconds}.mp4"
        output_json.append(
            {
                "start_time": start_time_in_seconds,
                "length": length_in_seconds,
                "rename_to": clip_filename,
                "title": subtitle.text,
            }
        )

    json.dump(output_json, output_manifest_file, indent=4, sort_keys=True)


if __name__ == "__main__":
    cli()
