import argparse
import asyncio
import logging
import os

# aiopathlib is deprecated, ref
# https://github.com/waketzheng/aiopathlib?tab=readme-ov-file#aiopathlib-pathlib-support-for-asyncio
from anyio import Path
from aioshutil import copyfile

LOGGER = logging.getLogger("CopyDir")
LOGGER.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

LOGGER.addHandler(ch)


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

        out_subdir = out if file.suffix == "" else Path(out / file.suffix.lstrip("."))
        await out_subdir.mkdir(parents=True, exist_ok=True)

        await copyfile(file, out_subdir / file.name)
    except PermissionError:
        LOGGER.warning(f"Permission denied: {file}")
    except FileNotFoundError:
        LOGGER.warning(f"File not found: {file}")
    except Exception as e:
        LOGGER.warning(f"Failed to copy {file} to {out_subdir}: {e}")


async def read_folder(source_path: Path, out_path: Path) -> None:
    # Even it's not truly parallel, use cpu count minus one as standard number of concurrent jobs
    semaphore = asyncio.Semaphore(os.cpu_count() - 1)

    completed_files = 0

    async def process_file(path):
        nonlocal completed_files
        async with semaphore:
            if await path.is_file():
                await copy_file(path, out_path)
                completed_files += 1
                LOGGER.info(f"Processed files: {completed_files}\r")

    tasks = [
        asyncio.create_task(process_file(path))
        async for path in source_path.rglob("*")
        if await path.is_file()
    ]

    await asyncio.gather(*tasks)


async def main():
    source, out = parse_args()

    source_path = Path(source)
    out_path = Path(out)
    if not await source_path.exists() or not await source_path.is_dir():
        LOGGER.critical(f"Invalid source directory: {source}")
        return
    if not await out_path.parent.exists() or not await out_path.parent.is_dir():
        LOGGER.critical(f"Invalid output directory: {out}")
        return

    try:
        await read_folder(source_path, out_path)
    except asyncio.CancelledError:
        LOGGER.info("Operation cancelled.")

    LOGGER.info("Completed.")


if __name__ == "__main__":
    asyncio.run(main())
