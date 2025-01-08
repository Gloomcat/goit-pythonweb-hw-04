import argparse
import asyncio
import logging
import os
# aiopathlib is deprecated, ref
# https://github.com/waketzheng/aiopathlib?tab=readme-ov-file#aiopathlib-pathlib-support-for-asyncio
from anyio import Path
from aioshutil import copyfile
from typing import Any


class FileCopyError(Exception):
    pass


def parse_args() -> tuple[str, str]:
    parser = argparse.ArgumentParser(
        description="Script for async recursive copy process of files from source to output directory based on their extensions."
    )

    parser.add_argument(
        "--source", "-s", type=str, required=True, help="Path to source directory."
    )
    parser.add_argument(
        "--out", "-o", type=str, required=True, help="Path to output directory."
    )

    args = parser.parse_args()
    return args.source, args.out


async def copy_file(file: Path, out: Path) -> None:
    try:
        if not await file.exists():
            return

        out_subdir = out if file.suffix == "" else Path(
            out / file.suffix.lstrip("."))
        await out_subdir.mkdir(parents=True, exist_ok=True)

        await copyfile(file, out_subdir / file.name)
    except PermissionError:
        raise FileCopyError(f"Permission denied: {file}")
    except FileNotFoundError:
        raise FileCopyError(f"File not found: {file}")
    except Exception as e:
        raise FileCopyError(f"Failed to copy {file} to {out_subdir}: {e}")


async def read_folder(source_path: Path, out_path: Path) -> list[Any]:
    # Even it's not truly parallel, use cpu count minus one as standard number of concurrent jobs
    semaphore = asyncio.Semaphore(os.cpu_count() - 1)

    async def process_file(path):
        async with semaphore:
            if await path.is_file():
                await copy_file(path, out_path)

    tasks = [
        asyncio.create_task(process_file(path))
        async for path in source_path.rglob("*")
        if await path.is_file()
    ]

    return await asyncio.gather(*tasks, return_exceptions=True)


async def main():
    source, out = parse_args()

    source_path = Path(source)
    out_path = Path(out)
    if not await source_path.exists() or not await source_path.is_dir():
        logging.critical(f"Invalid source directory: {source}")
        return
    if not await out_path.parent.exists() or not await out_path.parent.is_dir():
        logging.critical(f"Invalid output directory: {out}")
        return

    try:
        for result in await read_folder(source_path, out_path):
            if result:
                logging.warning(result)
    except asyncio.CancelledError:
        print("Operation cancelled.")

    logging.info("Completed.")


if __name__ == "__main__":
    asyncio.run(main())
