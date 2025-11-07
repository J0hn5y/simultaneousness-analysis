# simultaneousness analysis
This Project aims to determine simultaneousness factors for the use in power grid calculations. Therefore time series of climate data (i.e. solar radiation, wind velocity, air temperature,...) with the focus on the north of germany are evaluated. 




## Tooling

| Tool        | Description                                                                 |
|-------------|-----------------------------------------------------------------------------|
| **SQLite**  | Lightweight, self-contained SQL database engine. Requires no separate server process, making it ideal for embedded applications, prototyping, and small to medium-sized projects. |
| **Python**  | High-level, versatile programming language known for its readability and broad ecosystem. Widely used for web development, data analysis, automation, AI/ML, and scripting. |
| **Postman** | Collaboration platform for API development. Lets you design, test, and document APIs with an intuitive interface for sending requests, inspecting responses, and automating workflows. |
| **Draw.io** | Versatile diagramming tool (also known as diagrams.net) for creating flowcharts, UML diagrams, network schematics, and more. Integrates with GitHub and other platforms for version-controlled documentation. |

### Python Modules
| Tool        | Description                                                                 |
|-------------|-----------------------------------------------------------------------------|
| **UV**      | Ultra-fast Python package and project manager written in Rust. Combines dependency management, virtual environments, and publishing into a single efficient tool. |

### VS Code Extensions

| Extension       | Description                                                                 |
|-----------------|-----------------------------------------------------------------------------|
| **autoDocstring** | Automatically generates Python docstrings in formats like Google, NumPy, or reStructuredText. Helps maintain consistent and comprehensive documentation with minimal effort. |
| **Python**        | Core extension by Microsoft that adds Python language support, including IntelliSense, debugging, linting, environment management, and code navigation. |
| **Jupyter**       | Enables running and editing Jupyter Notebooks directly in VS Code. Provides interactive data exploration, visualization, and notebook-style workflows. |
| **Black**         | Opinionated Python code formatter that enforces a consistent style automatically. Ensures PEP 8 compliance and reduces time spent on formatting debates. |

## Data Sources

| Source | Description |
|--------|-------------|
| **DWD Climate Data Center (10‑Minute Observations)** | Open data provided by the Deutscher Wetterdienst (German Weather Service). Offers high‑resolution climate and weather observations across Germany with a temporal resolution of 10 minutes. Data categories include air temperature, precipitation, wind, solar radiation, and extreme events. [Docs](https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/10_minutes/) |
| **Open‑Meteo API** | Free, global weather API designed for developers. Provides forecasts and historical data with variables such as wind speed, wind direction, temperature, and solar radiation (global horizontal irradiance in W/m²). No API key required. [Docs](https://open-meteo.com/) |
| **Bright Sky API** | Free JSON API for Germany, built on official DWD open data. Returns weather observations and forecasts including wind speed, wind direction, temperature, sunshine duration, and solar radiation. Ideal for Germany‑centric projects. [Docs](https://brightsky.dev/) |
