# DeepTech Deal Navigator

A sophisticated deal sourcing tool designed for General Partners (GPs) to streamline the process of identifying and evaluating investment opportunities in the deep technology sector.

## Overview

The DeepTech Deal Navigator guides users through four critical stages of investment opportunity identification and evaluation:

1. **Sector Selection**: Strategic identification of promising deep technology sectors
2. **Deal Sourcing**: Systematic approach to finding potential investment opportunities
3. **Startup Finding**: Detailed company discovery and initial screening
4. **Technology Risk Assessment**: Comprehensive evaluation of technical viability and risks

## Tech Stack

- **Frontend**: Python/Streamlit for an interactive user interface
- **AI Integration**: Claude API for intelligent analysis
- **Version Control**: Git
- **Database**: PostgreSQL

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd DeepTechDealNavigator
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Set up environment variables:
- Create a `.env` file in the project root
- Add required API keys and configurations:
  ```
  CLAUDE_API_KEY=your_api_key_here
  DATABASE_URL=your_database_url
  ```

## Project Structure

```
├── stages/
│   ├── sector_selector.py
│   ├── deal_sourcer.py
│   ├── startup_finder.py
│   └── tech_risk_assessor.py
├── .streamlit/
│   └── config.toml
├── main.py
├── claude_api.py
├── database.py
├── utils.py
└── [other configuration files]
```

## Usage

1. Start the application:
```bash
streamlit run main.py
```

2. Navigate through the four stages:
   - Select target sectors
   - Source potential deals
   - Find and screen startups
   - Assess technological risks

## Features

- **Sector Analysis**: AI-powered analysis of deep technology sectors
- **Deal Pipeline**: Structured approach to deal sourcing and management
- **Risk Assessment**: Comprehensive technology risk evaluation
- **Data-Driven Insights**: Leveraging AI for deeper market understanding

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add License Information]

## Support

For support, please [add contact information or process]
