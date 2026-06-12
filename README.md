# simultaneousness analysis
This Project aims to determine simultaneousness factors for the use in power grid calculations. Therefore time series of climate data (i.e. solar radiation, wind velocity, air temperature,...) with the focus on the north of germany are evaluated. 

## Tooling 

| Tool        | Description                                                                 |
|-------------|-----------------------------------------------------------------------------|
| **Python**  | High-level, versatile programming language known for its readability and broad ecosystem. Widely used for web development, data analysis, automation, AI/ML, and scripting. |
| **UV**      | Ultra-fast Python package and project manager written in Rust. Combines dependency management, virtual environments, and publishing into a single efficient tool. |


## Data Sources

| Source | Description |
|--------|-------------|
| **DWD Climate Data Center (10‑Minute Observations)** | Open data provided by the Deutscher Wetterdienst (German Weather Service). Offers high‑resolution climate and weather observations across Germany with a temporal resolution of 10 minutes. Data categories include air temperature, precipitation, wind, solar radiation, and extreme events. [Docs](https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/10_minutes/) |

## Development Workflow with uv

To make changes to the package and ensure a smooth development experience, follow these steps:

1. **Clone the repository:**
   ```sh
   git clone <repo-url>
   cd simultaneousness-analysis
   ```
2. **Set up the environment:**
   ```sh
   uv venv
   uv sync
   ```
   - `uv venv` creates and activates a virtual environment.
   - `uv sync` installs all dependencies and the package in editable mode, so your changes are immediately reflected.
3. **Make your code changes** in `src/simultaneousness_analysis/` or its submodules.
4. **Test your changes:**
   - Run scripts (e.g., `python main.py`) or use `pytest` to run tests.
   - Imports will work out of the box.
5. **Add new dependencies:**
   - Add them to `pyproject.toml` under `[project.dependencies]` or `[dependency-groups]`.
   - Run `uv sync` again to update the environment.
6. **Commit and push your changes** as usual.

This workflow ensures that your environment is always up to date, imports work without hacks, and dependency management is simple and reproducible.

## Nearest Station Lookup

The package now supports finding the nearest DWD station from either:
- a German postal address, or
- explicit latitude/longitude coordinates.

Example usage:

```python
from pathlib import Path
from simultaneousness_analysis.meta import MetaTable

meta_table = MetaTable(data_path=Path("data/cdc/raw"))
nearest = meta_table.get_nearest_station_id_by_coordinates(
    latitude=54.769328,
    longitude=9.568905,
)
print(nearest.stations_id, nearest.distance_km)

nearest_address = meta_table.get_nearest_station_id_by_address(
    street="Rathausplatz",
    house_number="1",
    zip_code="24103",
    city="Kiel",
)
print(nearest_address.stations_id, nearest_address.distance_km)
```

This is useful for spatial queries and finding the best station for climate data analysis in northern Germany.

## Additional Development Instructions

### How to install and sync dependencies
- After cloning the repository, run:
  ```sh
  uv venv
  uv sync
  ```
- This will create a virtual environment and install all dependencies (including your package in editable mode).

### How to run scripts and tests
- To run the main script:
  ```sh
  python main.py
  ```
- To run tests (if available):
  ```sh
  pytest
  ```

### How to add new dependencies
- Add the new package to the `[project.dependencies]` or `[dependency-groups]` section in `pyproject.toml`.
- Alternatively use the command `uv add package`e.g. uv add pandas and uv will do it for you.
- Specify dependency group with --group e.g. `uv add --group test pytest`
- Then run:
  ```sh
  uv sync
  ```
- This will install the new dependency in your environment.

### How to handle branch switching with uncommitted changes
- If you need to switch branches but have uncommitted changes:
  ```sh
  git stash push -m "WIP: <description>"
  git checkout <other-branch>
  # When ready to restore your changes:
  git stash pop
  ```
- This will safely save and restore your work across branches.

### Example usage of the package in Python
```python
import simultaneousness_analysis as sa

# Access submodules or functions
sa.main()
result = sa.meta.MetaTable(...)
```

For more details, see the docstrings in the code or run:
```sh
python
>>> import simultaneousness_analysis as sa
>>> help(sa)
```

# Example: Using a class from the meta submodule
```sh
meta_table = sa.meta.MetaTable(data_path="path/to/data")
print(meta_table.table.head())
```