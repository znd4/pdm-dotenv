# pdm-dotenv

[![Tests](https://github.com/zdog234/pdm-dotenv/workflows/Tests/badge.svg)](https://github.com/zdog234/pdm-dotenv/actions?query=workflow%3Aci)
[![pypi version](https://img.shields.io/pypi/v/pdm-dotenv.svg)](https://pypi.org/project/pdm-dotenv/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm.fming.dev)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![codecov](https://codecov.io/github/znd4/pdm-dotenv/branch/main/graph/badge.svg?token=0PHW2BUEOY)](https://codecov.io/github/znd4/pdm-dotenv)

A pdm plugin that automatically loads .env files

## Requirements

pdm-dotenv requires Python >=3.8

## Installation

```shell
pdm self add pdm-dotenv
```

## Configuration

If you want to use something other than `.env`, such as `.dev.env`, you can set `dotenv.path`, e.g.:

```shell
pdm config --local dotenv.path .dev.env
```
