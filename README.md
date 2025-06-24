# 🚀 LLM-Powered BPM Lifecycle Demo

A comprehensive Streamlit application that demonstrates the power of Large Language Models (LLMs) in Business Process Management (BPM) across all five key stages of the BPM lifecycle.

## 🌟 Features

### Complete BPM Lifecycle Coverage
- **🎯 Process Identification**: Analyze business context and value proposition
- **🔍 Process Discovery**: Map current state process flows
- **📊 Process Analysis**: Identify bottlenecks, risks, and improvement opportunities
- **🔄 Process Redesign**: Create optimized future state processes
- **📈 Process Monitoring**: Establish KPIs and continuous improvement frameworks

### Interactive Visualizations
- **Process Flow Diagrams**: Auto-generated Graphviz visualizations
- **BPMN Export**: Download standard BPMN XML files
- **Side-by-side Comparison**: As-Is vs To-Be process views

### Pre-built Scenarios
- 📦 Supply Chain Procurement (Simple)
- 🏪 R&D New Product Development (Medium)
- 🏦 University Enrollment System (Complex)
- ✏️ Custom Process Input

## 🔧 Installation

### Prerequisites
- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd llm-bpm-lifecycle
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Graphviz (for process visualizations)**
   
   **On Ubuntu/Debian:**
   ```bash
   sudo apt-get install graphviz
   ```
   
   **On macOS:**
   ```bash
   brew install graphviz
   ```
   
   **On Windows:**
   - Download from [Graphviz website](https://graphviz.org/download/)
   - Add to system PATH

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

## 📋 Requirements

Create a `requirements.txt` file with the following dependencies:

```txt
streamlit>=1.28.0
graphviz>=0.20.1
xmltodict>=0.13.0
langchain>=0.0.350
openai>=1.0.0
```

## 🚀 Usage

### Getting Started

1. **Launch the app**: Run `streamlit run app.py`
2. **Enter your OpenAI API Key**: 
   - Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
   - Paste it in the secure input field
   - Select your preferred model (GPT-4 recommended for best results)

3. **Choose a scenario**:
   - Select from pre-built scenarios or create custom input
   - Modify the process description as needed

4. **Run the analysis**: Click "🔍 Run Complete BPM Analysis"

### Understanding the Output

The application processes your business process through five sequential stages:

#### 1️⃣ **Process Identification**
- Business purpose and objectives
- Key stakeholders identification
- Current pain points analysis
- Business value assessment
- Improvement potential areas

#### 2️⃣ **Process Discovery**
- Sequential process steps extraction
- Current state process flow visualization
- Downloadable As-Is BPMN diagram

#### 3️⃣ **Process Analysis**
- Bottleneck identification
- Redundancy analysis
- Risk assessment
- Automation opportunities
- Resource utilization review

#### 4️⃣ **Process Redesign**
- Optimized process design
- To-Be process flow visualization
- Downloadable improved BPMN diagram
- Key improvements summary

#### 5️⃣ **Process Monitoring**
- KPI framework design
- Target values and thresholds
- Monitoring frequency recommendations
- Technology enablers suggestions

## 🔐 Security & Privacy

- **API Key Security**: Your OpenAI API key is only used during the session and is never stored
- **Local Processing**: All data processing happens in your browser session
- **No Data Persistence**: No business process data is saved or transmitted beyond OpenAI API calls

## 💰 Cost Considerations

- **User-Funded**: Users provide their own OpenAI API keys
- **Model Costs**: 
  - GPT-4: ~$0.03 per 1K tokens (input) / $0.06 per 1K tokens (output)
  - GPT-3.5-turbo: ~$0.001 per 1K tokens (input) / $0.002 per 1K tokens (output)
- **Typical Usage**: A complete BPM analysis usually costs $0.10-$0.50 depending on complexity and model choice

## 🛠️ Customization

### Adding New Scenarios
Edit the `DEMO_SCENARIOS` dictionary in `app.py`:

```python
DEMO_SCENARIOS = {
    "Your New Scenario": {
        "description": "Your process description here...",
        "complexity": "Simple|Medium|Complex",
        "industry": "Your Industry"
    }
}
```

### Modifying Prompts
Update the `BPMStageTemplates` class methods to customize the analysis prompts for each stage.

### Styling
Modify the Streamlit configuration and CSS in the `st.set_page_config()` and custom CSS sections.

## 🔍 Troubleshooting

### Common Issues

**1. Graphviz not found**
```bash
# Install Graphviz system package
sudo apt-get install graphviz  # Ubuntu/Debian
brew install graphviz          # macOS
```

**2. OpenAI API Errors**
- Verify your API key is correct
- Check your OpenAI account has available credits
- Ensure API key has appropriate permissions

**3. Import Errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**4. Streamlit Issues**
```bash
# Clear Streamlit cache
streamlit cache clear
```

## 📊 Example Output

The application generates comprehensive analysis including:

- **Visual Process Maps**: Before and after process flows
- **BPMN Files**: Standard XML format for process modeling tools
- **Detailed Reports**: Multi-stage analysis with actionable insights
- **KPI Frameworks**: Measurable metrics for process monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for providing the powerful GPT models
- **Streamlit** for the excellent web app framework
- **LangChain** for LLM integration utilities
- **Graphviz** for process visualization capabilities

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/your-username/your-repo/issues) section
2. Create a new issue with detailed description
3. Include error messages and system information

## 🔮 Future Enhancements

- [ ] Integration with more process modeling tools
- [ ] Support for additional LLM providers (Anthropic Claude, Google Gemini)
- [ ] Process simulation capabilities
- [ ] Multi-language support
- [ ] Advanced analytics and reporting
- [ ] Collaborative features for team analysis

