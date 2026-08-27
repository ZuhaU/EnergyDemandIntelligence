Power Generation Intelligence

Power Generation Intelligence is a data engineering and analytics project built around Pakistan’s electricity generation data.

The idea is to take electricity generation data, build a proper data pipeline around it, forecast future generation, generate useful insights from the results, and present everything through Power BI.

The project is also being moved toward a fully automated cloud setup using Azure, where the pipeline can run on a schedule without manually running each Python script.

⸻

What the Project Does

The pipeline currently handles:

1. Getting electricity generation data
2. Storing the raw data
3. Cleaning and validating the data
4. Transforming it into analysis-ready datasets
5. Creating monthly generation data
6. Forecasting future electricity generation
7. Evaluating the forecasting model
8. Generating analytical insights
9. Uploading the outputs to Azure
10. Visualizing the results in Power BI

The final version is intended to run automatically in the cloud on a scheduled basis.

⸻

Technologies

* Python — data processing and pipeline orchestration
* Pandas / NumPy — data cleaning and transformation
* Statsmodels — SARIMA/SARIMAX forecasting
* Scikit-learn — model evaluation
* Azure Data Lake Storage Gen2 — cloud data storage
* Azure Container Registry — Docker image storage
* Azure Container Apps Jobs — scheduled pipeline execution
* Docker — containerization
* Ollama + Phi-3 Mini — AI-generated executive summaries
* Power BI — dashboard and visualization

⸻

Data Pipeline

The project follows a Bronze → Silver → Gold structure.

Raw Electricity Data
        │
        ▼
     Bronze
        │
        ▼
     Silver
        │
        ├── Validation
        └── Cleaning
        │
        ▼
      Gold
        │
        ├── Forecasting
        │
        └── Intelligence
        │
        ▼
      Azure
        │
        ▼
    Power BI

Bronze

The Bronze layer contains the raw electricity-generation dataset.

Generation of Electricity by Sector.csv

The raw data is kept before the analytical transformations are applied.

Silver

The raw dataset is transformed into a normalized structure.

The main fields include:

date
source
generation_gwh
unit

The Silver data is then validated and cleaned before being used by the downstream stages.

Gold

The Gold layer contains the datasets used for analysis, forecasting, and Power BI.

Some of the current outputs include:

electricity_monthly_gold.csv
electricity_generation_forecast.csv
forecast_evaluation.csv

⸻

Forecasting

The forecasting component uses a SARIMA/SARIMAX model to forecast monthly electricity generation.

The current model uses:

Order: (1, 1, 1)
Seasonal Order: (1, 1, 1, 12)

The model is evaluated using a held-out historical test period before being trained on the available historical data to generate the future forecast.

The forecasting stage produces a 12-month forecast with confidence bounds.

The forecast output contains:

date
forecast_generation_gwh
lower_bound_gwh
upper_bound_gwh

The evaluation results are also saved for further analysis.

⸻

Intelligence

The Intelligence layer takes the results produced by the data and forecasting pipeline and turns them into useful findings.

The Python intelligence engine can identify things such as:

* Changes in electricity generation
* Year-over-year changes
* Generation trends
* Changes by generation source
* Unusually high or low values
* Forecast errors
* Forecast underestimation or overestimation

The structured findings are stored in:

Data/Intelligence/insights.csv

An executive summary can also be generated using Ollama and Phi-3 Mini based on the calculated findings.

The idea is to calculate the actual statistics first and then use the language model to explain those results, rather than asking the AI model to analyze the raw dataset and potentially invent numbers.

⸻

Azure

Azure is being used as the cloud backend for the project.

The Data Lake is organized into the following layers:

Azure Data Lake
│
├── Bronze
├── Silver
├── Gold
└── Intelligence

The Python pipeline contains upload components that publish the generated datasets to Azure.

The goal is for Azure Data Lake to become the main location for the processed data instead of relying on local CSV files.

⸻

Docker

The project is containerized using Docker.

The Docker container packages the Python environment and project code so that the pipeline can run in a consistent environment.

The main entry point is:

src/pipeline.py

The project is organized into:

src/
├── ingestion/
├── transformation/
├── validation/
├── forecasting/
├── intelligence/
├── azure/
└── pipeline.py

The Docker image is stored in Azure Container Registry.

⸻

Azure Container Apps Job

The next stage of the project is to run the complete Dockerized pipeline through an Azure Container Apps Job.

The intended workflow is:

Scheduled Job
      │
      ▼
Docker Container
      │
      ▼
pipeline.py
      │
      ├── Get latest data
      ├── Transform
      ├── Validate
      ├── Clean
      ├── Create Gold datasets
      ├── Forecast
      ├── Generate insights
      └── Upload results to Azure
             │
             ▼
        Azure Data Lake
             │
             ▼
          Power BI

Once this is complete, the project should be able to run the pipeline automatically on a schedule instead of requiring each stage to be executed manually.

⸻

Power BI

Power BI is used as the visualization and reporting layer.

The dashboard includes views for:

* Total electricity generation
* Generation by source
* Historical trends
* Renewable generation
* Future forecasts
* Forecast performance
* Generated intelligence

The final dashboard will use the data stored in Azure rather than depending on local copies of the CSV files.

⸻

Project Structure

PowerGenerationIntelligence/
│
├── Data/
│   ├── Raw/
│   ├── Silver/
│   ├── Gold/
│   └── Intelligence/
│
├── src/
│   │
│   ├── azure/
│   │   ├── upload_to_bronze.py
│   │   ├── upload_silver.py
│   │   ├── upload_gold.py
│   │   └── upload_source_gold.py
│   │
│   ├── forecasting/
│   │   └── forecast.py
│   │
│   ├── ingestion/
│   │   ├── download_data.py
│   │   └── inspect_data.py
│   │
│   ├── intelligence/
│   │   └── generate_insights.py
│   │
│   ├── transformation/
│   │   ├── transform_electricity.py
│   │   ├── create_gold.py
│   │   └── create_source_gold.py
│   │
│   ├── validation/
│   │   └── validate_data.py
│   │
│   ├── pipeline.py
│   └── requirements.txt
│
├── Dockerfile
├── .dockerignore
└── README.md

⸻

Current Status

Completed

* Electricity generation data processing
* Bronze layer
* Silver transformation
* Data validation
* Data cleaning
* Monthly Gold dataset
* Source Gold dataset
* SARIMA/SARIMAX forecasting
* 12-month future forecast
* Forecast model evaluation
* Intelligence generation
* AI-generated executive summary
* Azure Data Lake setup
* Bronze data upload
* Silver data upload
* Gold data upload
* Docker containerization
* Azure Container Registry
* Azure Container Apps Job setup
* Power BI dashboard

Still Working On

* Upload Intelligence output to Azure
* Connect Intelligence output to Power BI
* Push the final Docker image to Azure Container Registry
* Get the complete pipeline running successfully inside the Azure Container Apps Job
* Make the SBP data ingestion fully automated
* Run a complete end-to-end cloud test
* Final project cleanup and documentation

⸻

Final Goal

The end goal is for the complete project to work like this:

                         Azure
                           │
                    Scheduled Job
                           │
                           ▼
                    Docker Container
                           │
                           ▼
                      pipeline.py
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
        Ingestion      Processing     Forecasting
            │              │              │
            └──────────────┼──────────────┘
                           ▼
                      Intelligence
                           │
                           ▼
                    Azure Data Lake
                           │
                           ▼
                        Power BI

The goal is to have one scheduled cloud pipeline that can:

Pull the latest data → process it → forecast electricity generation → generate insights → store the results in Azure → make the updated information available in Power BI.

The final system should require minimal manual intervention once the cloud automation is in place.
