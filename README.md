# Weather Agent

An AI-powered weather agent that answers questions about the current temperature and 7-day forecast for any city in the world.

Built with the **Microsoft Agent Framework** and deployed to **Azure AI Foundry**, it uses the [Open-Meteo API](https://open-meteo.com/) for weather data and exposes a hosted responses endpoint.

## Architecture

```
agent-wheather/
├── agents/weather/
│   ├── azure.yaml              # Azure AI Agent deployment config
│   └── src/temperature/
│       ├── main.py             # Agent entrypoint & tools
│       ├── pyproject.toml      # Agent dependencies
│       └── Dockerfile          # Container definition
├── pyproject.toml              # Workspace root
└── .env                        # Environment variables (not committed)
```

## How it works

The agent exposes two tools:

- **`get_current_temperature`** - Returns the current temperature (Celsius) for a given city.
- **`get_weekly_temperature_forecast`** - Returns the 7-day min/max temperature forecast.

Both tools use the Open-Meteo geocoding and forecast APIs. The agent is powered by an Azure AI Foundry model deployment and served via the `ResponsesHostServer`.

## Prerequisites

- Python >= 3.12
- [uv](https://docs.astral.sh/uv/) package manager
- [Azure Developer CLI (`azd`)](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/) with the AI Agent extension
- An Azure AI Foundry project with a deployed model
- A `.env` file with the following variables:
  ```
  FOUNDRY_PROJECT_ENDPOINT=<your-foundry-endpoint>
  AZURE_AI_MODEL_DEPLOYMENT_NAME=<your-model-deployment>
  ```

## Running locally

```bash
azd ai agent run
```

This starts the agent server on `http://localhost:8088`.

## Author

Joaquin Carballo
