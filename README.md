# Generates Large Images

This is used for testing if large files are required

## Prerequisites

- [uv](https://github.com/astral-sh/uv)

## Install
```
uv sync
```

## Usage
If you want to generate images up to 2 GB
```
uv run python gen_images.py
```

If you want to generate images with a different size, use `--target-gb` parameter, for example:
```
uv run python gen_images.py --target-gb 4
```

They will generate images to the ignored `generated_images/` folder
