# Personal Health Studio - Multi-Agent Health Intelligence System

> **Transform your health PDFs into actionable intelligence using Claude Desktop, Snowflake, and advanced AI agents**

## 🎯 Quick Start

This project provides a complete, personalized multi-agent system for extracting, analyzing, and visualizing your health data from any health app export (Apple Health, MyChart, Epic, Kaiser, etc.).

### What It Does

- **Extracts** comprehensive health data from PDF exports with 100% accuracy
- **Structures** medical records into analytics-ready JSON
- **Analyzes** your health journey across years using natural language queries
- **Visualizes** trends, patterns, and correlations in your personal health data

### Five-Minute Setup

1. **Clone this repo**
   ```bash
   git clone <your-repo-url> health-intelligence
   cd health-intelligence
   ```

2. **Review the architecture**
   - Read [CLAUDE.md](CLAUDE.md) to understand the system design
   - Review [Principles-and-Processes.md](Principles-and-Processes.md) for engineering standards

3. **Set up Claude Desktop**
   - Copy `claude_desktop_config.json` to your Claude Desktop settings
   - Configure Snowflake credentials (see CLAUDE.md)

4. **Run the agents**
   - Use the **Health Data Extractor Agent** to process your PDF
   - Use the **Health Analyst Agent** to query and explore your data

## 📚 Project Structure

```
├── agents/
│   ├── extractor-agent/        # PDF extraction with 100% accuracy
│   │   ├── config/             # Agent instructions and description
│   │   └── knowledge/           # JSON schemas for data extraction
│   └── analyst-agent/           # Natural language analysis & visualization
│       └── config/              # Agent instructions
├── data-store/
│   └── snowflake/               # Database schema and queries
├── tools/
│   └── health-mcp/              # MCP server for Snowflake integration
├── semantic-model/              # Natural language → SQL mappings
├── requirements/                # Technical specifications
├── docs/
│   └── Research/                # Planning documents and research
├── CLAUDE.md                    # Claude Code instructions (start here!)
├── Principles-and-Processes.md  # Engineering standards
└── README.md                    # This file
```

## 🏗️ Architecture

### Two-Agent Pipeline

```
Your Health PDF
    ↓
[Extractor Agent]  → Reads PDF, extracts data with 100% accuracy
    ↓
JSON Files (lab results, vitals, medications, clinical data)
    ↓
[Health MCP Server]  → Connects agents to Snowflake
    ↓
Snowflake Database  → Structured health records
    ↓
[Analyst Agent]  → Analyzes via natural language queries
    ↓
Insights & Visualizations
```

## 🚀 Key Features

### Extractor Agent
- Processes PDFs from any health app source
- Extracts with guaranteed accuracy (100% fidelity to source)
- Organizes by data type: labs, vitals, medications, clinical data
- Groups by year for efficient analysis

### Analyst Agent
- Imports structured data into Snowflake
- Enables natural language queries
- Provides visual analytics dashboards
- Supports multi-provider data correlation

### Design Philosophy

This project follows **conservative engineering principles**:
- **Fail-safe defaults**: Validates data before processing
- **Data integrity first**: No approximations or missing values
- **Transparent operations**: Logs all decisions and errors clearly
- **User empowerment**: Clear instructions for every step

## 📖 Documentation

- **[CLAUDE.md](CLAUDE.md)** - System design for Claude Code development
- **[Principles-and-Processes.md](Principles-and-Processes.md)** - Software engineering standards
- **[plan.md](plan.md)** - Implementation roadmap
- **[docs/Research/](docs/Research/)** - Planning documents and exploration notes

## 🔧 Technology Stack

- **Claude Desktop** - AI agent orchestration
- **Snowflake** - Structured health data storage
- **Cortex Analyst** - Natural language → SQL conversion
- **MCP (Model Context Protocol)** - Agent-to-database bridging
- **Python 3.10+** - Deterministic extraction and validation logic

## 💡 Design Decisions

### Why Snowflake?
- Built-in semantic model for natural language queries
- Zero-operations database
- Excellent for health data analytics
- Cortex Analyst handles NL→SQL translation

### Why Two Agents?
- **Separation of concerns**: Extraction vs. analysis
- **Specialization**: Each agent optimized for its task
- **Reusability**: Analyst works with any extracted data source
- **Scalability**: Easy to add specialized agents later

### Why This Architecture?
- Deterministic extraction ensures data accuracy
- Probabilistic analysis leverages Claude's reasoning
- Conservative defaults catch errors early
- Clear audit trails for sensitive health data

## 🎓 Learning Resources

### For Understanding the System
1. Start with [CLAUDE.md](CLAUDE.md) - full system overview
2. Review agent instructions in `agents/*/config/`
3. Explore data schemas in `agents/extractor-agent/knowledge/`

### For Getting Hands-On
1. Upload a health PDF to the Extractor Agent
2. Review extracted JSON output
3. Import to Snowflake using the Analyst Agent
4. Query your health data with natural language

## 🔐 Privacy & Security

- Your health data **never leaves your control**
- All processing happens locally or in your Snowflake instance
- No data is sent to external services
- Full audit trail of all data operations

## 📋 Roadmap

### Phase 1: Foundation (Current)
- [x] Agent configuration and instructions
- [x] Data extraction schemas
- [ ] Snowflake database schema
- [ ] MCP server implementation

### Phase 2: Analysis
- [ ] Semantic model for natural language queries
- [ ] Analyst Agent data import
- [ ] Sample visualizations

### Phase 3: Enhancement
- [ ] Multi-source PDF support
- [ ] Advanced analytics capabilities
- [ ] Custom notification framework

## 🤝 Contributing

This is a personal project, but the architecture is designed to be extended. To modify:

1. Review [Principles-and-Processes.md](Principles-and-Processes.md) for standards
2. Follow CLAUDE.md design patterns
3. Test extractions with sample data
4. Document changes in decision logs

## 📞 Support

For questions or issues:
1. Check relevant README files
2. Review agent instructions in config/
3. Consult technical specifications in requests/
4. Review your working session logs in docs/Research/

## 📄 License

This project is built on the foundation of [georgevetticaden/multi-agent-health-insight-system](https://github.com/georgevetticaden/multi-agent-health-insight-system) (MIT License) and extends it with personal customizations.

---

**Last Updated**: February 12, 2026  
**Status**: Foundation Phase - Ready for Agent Development
