# pAIper - AI-Powered Research Paper Discovery

An intelligent research tool that uses AI to generate optimized search queries, discover academic papers from Google Scholar and Scopus, and create comprehensive research reports with APA citations.

## 🚀 Features

### 🤖 AI-Powered Query Generation

- Uses OpenRouter with Google Gemini 2.5 Flash as default model
- Support for custom OpenRouter model names
- Local Ollama model support with automatic model detection
- Generates multiple optimized academic search queries
- Provides confidence scores and keyword extraction
- Interactive query selection interface

### 📚 Comprehensive Paper Search
- **Google Scholar** integration via SerpApi
- **Scopus** database search via Elsevier API
- Automatic deduplication and relevance scoring
- Rich metadata extraction (authors, citations, DOI, etc.)

### 📊 Advanced Export Options
- **CSV Export** with customizable fields
- **JSON Export** for data processing
- **BibTeX Export** for reference managers
- Complete session export for reproducibility

### 📝 AI-Generated Reports
- PhD-level comprehensive research reports
- Proper APA citations throughout text
- Structured sections (Abstract, Introduction, Methodology, Findings, Conclusion)
- Export to PDF and plain text formats

## 🛠 Technology Stack

- **Frontend**: Next.js 15, React 19, TypeScript, Tailwind CSS
- **Backend**: Next.js API Routes
- **AI Models**: OpenRouter API (Claude), Ollama (local)
- **Academic APIs**: SerpApi (Google Scholar), Elsevier Scopus API
- **Export**: jsPDF, PapaParse, File-Saver
- **Deployment**: Vercel

## 📋 Prerequisites

You need at least one AI provider and one academic database API:

### AI Providers (Choose at least one)
- **OpenRouter API Key** (Recommended) - [Get API Key](https://openrouter.ai)
- **Ollama** (Local) - [Install Ollama](https://ollama.ai)

### Academic Databases (Choose at least one)
- **Google Scholar** - [SerpApi Key](https://serpapi.com)
- **Scopus** - [Elsevier Developer Portal](https://dev.elsevier.com)

## 🚀 Quick Start

### Option 1: Deploy to Vercel (Recommended)

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/paiper)

### Option 2: Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd paiper
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your API keys (optional - can be entered in UI)
   ```

4. **Run the development server**
   ```bash
   npm run dev
   ```

5. **Open your browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

## 🔧 Configuration

### API Configuration
The app provides a user-friendly interface to configure APIs. You can either:

1. **Enter API keys in the web interface** (recommended for security)
2. **Set environment variables** in `.env.local`:
   ```env
   NEXT_PUBLIC_SITE_URL=http://localhost:3000
   ```

### Supported AI Models

#### OpenRouter

- Google Gemini 2.5 Flash (default)
- Custom model support (enter any OpenRouter model ID)
- All OpenRouter models supported via custom input

#### Ollama (Local)
- Llama 3.1 (8B, 70B)
- Mistral models
- Custom fine-tuned models

## 📖 Usage Guide

### 1. Configure APIs
- Enter your API keys for AI providers and academic databases
- The system validates keys before proceeding

### 2. Enter Research Query
- Describe your research topic in natural language
- Example: "machine learning applications in healthcare diagnosis"

### 3. Review Generated Queries
- AI generates 5 optimized academic search queries
- Review and select queries that best match your needs
- Each query shows confidence score and keywords

### 4. Search Academic Papers
- System searches your selected databases
- Papers are ranked by relevance and citation count
- Duplicates are automatically removed

### 5. Explore Results
- Browse papers with abstracts, authors, and metadata
- Filter and sort results
- Export papers in various formats

### 6. Generate Report
- AI analyzes paper abstracts and generates a comprehensive report
- Includes proper APA citations throughout
- Export as PDF or text

## 🎯 Best Practices

### Query Writing
- Be specific about your research domain
- Include key concepts and methodologies
- Avoid overly broad or narrow topics

### API Usage
- Start with smaller result sets (20-50 papers)
- Use multiple queries for comprehensive coverage
- Be mindful of API rate limits

### Report Generation
- Review paper selection before generating reports
- Edit and customize report titles
- Verify citations and references

## 🔒 Privacy & Security

- **API Keys**: Never stored on servers, only in browser session
- **Data**: No research data is permanently stored
- **Privacy**: All searches and reports are ephemeral
- **HTTPS**: All API communications are encrypted

## 🧪 Development

### Project Structure
```
src/
├── app/
│   ├── api/            # API routes
│   └── page.tsx        # Main page
├── components/         # React components
├── lib/               # Utility functions
└── types/             # TypeScript definitions
```

### Key Components
- `PaiperApp.tsx` - Main application orchestrator
- `APIConfiguration.tsx` - API key management
- `QuerySelection.tsx` - Query review interface
- `PaperResults.tsx` - Search results display
- `ReportDisplay.tsx` - Generated report viewer

### API Routes
- `/api/generate-queries` - AI query generation
- `/api/search-papers` - Academic paper search
- `/api/generate-report` - Research report creation

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md).

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenRouter for AI model access
- Elsevier for Scopus API
- SerpApi for Google Scholar access
- Next.js team for the excellent framework
- Vercel for hosting platform

## 📞 Support

- 📧 Email: support@paiper.ai
- 💬 Discord: [Join our community](https://discord.gg/paiper)
- 📖 Documentation: [docs.paiper.ai](https://docs.paiper.ai)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/paiper/issues)

## 🎉 What's Next?

- [ ] Real-time collaboration features
- [ ] Advanced citation analysis
- [ ] Integration with more academic databases
- [ ] Mobile app development
- [ ] Custom AI model fine-tuning
- [ ] Institutional subscriptions

---

**Built for researchers, by researchers. Happy researching! 🔬**
