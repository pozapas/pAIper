'use client';

import React, { useState } from 'react';
import { APIConfig, ResearchQuery, SearchResult, ResearchReport, AppState, ExportOptions } from '@/types';
import APIConfiguration from '@/components/APIConfiguration';
import QuerySelection from '@/components/QuerySelection';
import PaperResults from '@/components/PaperResults';
import ReportDisplay from '@/components/ReportDisplay';
import { ShaderAnimation } from '@/components/ui/shader-animation';
import { Brain, Search, FileText, BookOpen, AlertCircle, ArrowRight, Sparkles, Zap, Target } from 'lucide-react';
import { cn } from '@/lib/utils';
import { 
  exportPapersToCSV, 
  exportPapersToJSON, 
  exportPapersToBibTeX
} from '@/lib/export';

export default function PaiperApp() {
  const [appState, setAppState] = useState<AppState>({
    currentStep: 'welcome', // Start with welcome screen
    apiConfig: {},
    originalQuery: '',
    generatedQueries: [],
    selectedQueries: [],
    searchResults: null,
    report: null,
    loading: false,
    error: null
  });

  const [originalQuery, setOriginalQuery] = useState('');

  const setLoading = (loading: boolean, error: string | null = null) => {
    setAppState(prev => ({ ...prev, loading, error }));
  };

  const setError = (error: string) => {
    setAppState(prev => ({ ...prev, error, loading: false }));
  };

  // Step 1: API Configuration
  const handleConfigUpdate = (config: APIConfig) => {
    setAppState(prev => ({ ...prev, apiConfig: config }));
  };

  const handleConfigComplete = () => {
    setAppState(prev => ({ ...prev, currentStep: 'query-generation' }));
  };

  // Step 2: Query Generation
  const generateQueries = async () => {
    if (!originalQuery.trim()) {
      setError('Please enter a research query');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch('/api/generate-queries', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          originalQuery: originalQuery.trim(),
          apiConfig: appState.apiConfig,
          numQueries: 5
        })
      });

      if (!response.ok) {
        throw new Error('Failed to generate queries');
      }

      const { queries } = await response.json();
      
      setAppState(prev => ({
        ...prev,
        originalQuery: originalQuery.trim(),
        generatedQueries: queries,
        currentStep: 'query-selection',
        loading: false,
        error: null
      }));
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to generate queries');
    }
  };

  // Step 3: Query Selection
  const handleQueriesUpdate = (queries: ResearchQuery[]) => {
    setAppState(prev => ({ ...prev, generatedQueries: queries }));
  };

  const handleQuerySelectionComplete = () => {
    const selected = appState.generatedQueries.filter(q => q.selected);
    setAppState(prev => ({
      ...prev,
      selectedQueries: selected,
      currentStep: 'search'
    }));
    searchPapers();
  };

  // Step 4: Paper Search
  const searchPapers = async () => {
    const selectedQueries = appState.generatedQueries.filter(q => q.selected);
    
    if (selectedQueries.length === 0) {
      setError('Please select at least one query');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch('/api/search-papers', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          queries: selectedQueries,
          apiConfig: appState.apiConfig,
          maxResults: 50,
          sources: ['google-scholar', 'scopus']
        })
      });

      if (!response.ok) {
        throw new Error('Failed to search papers');
      }

      const searchResult: SearchResult = await response.json();
      
      setAppState(prev => ({
        ...prev,
        searchResults: searchResult,
        currentStep: 'results',
        loading: false,
        error: null
      }));
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to search papers');
    }
  };

  // Step 5: Export Papers
  const handleExport = (options: ExportOptions) => {
    if (!appState.searchResults) return;

    try {
      switch (options.format) {
        case 'csv':
          exportPapersToCSV(appState.searchResults.papers, options);
          break;
        case 'json':
          exportPapersToJSON(appState.searchResults.papers);
          break;
        case 'bibtex':
          exportPapersToBibTeX(appState.searchResults.papers);
          break;
      }
    } catch (error) {
      setError('Failed to export papers');
    }
  };

  // Step 6: Report Generation
  const generateReport = async () => {
    if (!appState.searchResults) return;

    setLoading(true);

    try {
      const response = await fetch('/api/generate-report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          papers: appState.searchResults.papers,
          originalQuery: appState.originalQuery,
          apiConfig: appState.apiConfig,
          reportTitle: `Research Report: ${appState.originalQuery}`
        })
      });

      if (!response.ok) {
        throw new Error('Failed to generate report');
      }

      const { report }: { report: ResearchReport } = await response.json();
      
      setAppState(prev => ({
        ...prev,
        report,
        currentStep: 'report',
        loading: false,
        error: null
      }));
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to generate report');
    }
  };

  // Navigation
  const goBack = () => {
    switch (appState.currentStep) {
      case 'config':
        setAppState(prev => ({ ...prev, currentStep: 'welcome' }));
        break;
      case 'query-generation':
        setAppState(prev => ({ ...prev, currentStep: 'config' }));
        break;
      case 'query-selection':
        setAppState(prev => ({ ...prev, currentStep: 'query-generation' }));
        break;
      case 'search':
      case 'results':
        setAppState(prev => ({ ...prev, currentStep: 'query-selection' }));
        break;
      case 'report':
        setAppState(prev => ({ ...prev, currentStep: 'results' }));
        break;
    }
  };

  // Start the application from welcome screen
  const startResearch = () => {
    setAppState(prev => ({ ...prev, currentStep: 'config' }));
  };

  // Progress Steps
  const steps = [
    { id: 'config', title: 'Configuration', icon: Brain, completed: appState.currentStep !== 'config' && appState.currentStep !== 'welcome' },
    { id: 'query-generation', title: 'Query Generation', icon: Search, completed: appState.generatedQueries.length > 0 },
    { id: 'query-selection', title: 'Query Selection', icon: Search, completed: appState.selectedQueries.length > 0 },
    { id: 'results', title: 'Paper Results', icon: FileText, completed: !!appState.searchResults },
    { id: 'report', title: 'Research Report', icon: BookOpen, completed: !!appState.report }
  ];

  const currentStepIndex = steps.findIndex(step => 
    step.id === appState.currentStep || 
    (appState.currentStep === 'search' && step.id === 'results')
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Welcome Screen with Shader Animation */}
      {appState.currentStep === 'welcome' && (
        <div className="relative w-full h-screen overflow-hidden">
          <ShaderAnimation />
          <div className="absolute inset-0 z-10 flex flex-col items-center justify-center text-center">
            {/* Welcome Content */}
            <div className="max-w-4xl mx-auto px-6">
              <div className="mb-8">
                <div className="flex items-center justify-center mb-6">
                  <div className="w-20 h-20 bg-white/10 backdrop-blur-md rounded-2xl flex items-center justify-center border border-white/20">
                    <Brain className="w-10 h-10 text-white" />
                  </div>
                </div>
                <h1 className="text-6xl font-bold text-white mb-4 leading-tight">
                  pAIper
                </h1>
                <p className="text-xl text-white/90 mb-8 leading-relaxed">
                  AI-Powered Research Discovery Platform
                </p>
                <p className="text-lg text-white/80 mb-12 max-w-2xl mx-auto">
                  Harness the power of artificial intelligence to discover, analyze, and synthesize academic papers. 
                  Generate optimized search queries, access multiple databases, and create comprehensive research reports.
                </p>
              </div>

              {/* Features Grid */}
              <div className="grid md:grid-cols-3 gap-6 mb-12">
                <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
                  <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center mb-4">
                    <Sparkles className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">AI Query Generation</h3>
                  <p className="text-white/80 text-sm">
                    Transform your research ideas into optimized academic search queries using advanced AI
                  </p>
                </div>

                <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
                  <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center mb-4">
                    <Target className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">Multi-Database Search</h3>
                  <p className="text-white/80 text-sm">
                    Search across Google Scholar, Scopus, and more to find the most relevant papers
                  </p>
                </div>

                <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
                  <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center mb-4">
                    <Zap className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">Smart Reports</h3>
                  <p className="text-white/80 text-sm">
                    Generate PhD-level literature reviews with APA citations and thematic analysis
                  </p>
                </div>
              </div>

              {/* Call to Action */}
              <div className="space-y-4">
                <button
                  onClick={startResearch}
                  className="inline-flex items-center gap-3 px-8 py-4 bg-white text-gray-900 rounded-xl font-semibold hover:bg-white/90 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
                >
                  Start Research Journey
                  <ArrowRight className="w-5 h-5" />
                </button>
                <p className="text-white/60 text-sm">
                  Join thousands of researchers accelerating their academic work
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Application */}
      {appState.currentStep !== 'welcome' && (
        <>
          {/* Header */}
          <header className="bg-white border-b border-gray-200">
            <div className="max-w-7xl mx-auto px-6 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => setAppState(prev => ({ ...prev, currentStep: 'welcome' }))}
                    className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center hover:bg-blue-700 transition-colors"
                  >
                    <Brain className="w-5 h-5 text-white" />
                  </button>
                  <div>
                    <h1 className="text-xl font-bold text-gray-900">pAIper</h1>
                    <p className="text-sm text-gray-600">AI-Powered Research Discovery</p>
                  </div>
                </div>
                
                {appState.originalQuery && (
                  <div className="flex items-center gap-2 max-w-md">
                    <span className="text-sm text-gray-500">Research Query:</span>
                    <span className="text-sm font-medium text-gray-900 truncate">
                      "{appState.originalQuery}"
                    </span>
                  </div>
                )}
              </div>
            </div>
          </header>

          {/* Progress Bar */}
          <div className="bg-white border-b border-gray-200">
            <div className="max-w-7xl mx-auto px-6 py-4">
              <div className="flex items-center justify-between">
                {steps.map((step, index) => {
                  const Icon = step.icon;
                  const isCurrent = index === currentStepIndex;
                  const isCompleted = step.completed;
                  const isAccessible = index <= currentStepIndex;

                  return (
                    <div
                      key={step.id}
                      className={cn(
                        "flex items-center gap-2 px-3 py-2 rounded-lg transition-colors",
                        isCurrent ? "bg-blue-100 text-blue-700" :
                        isCompleted ? "text-green-600" :
                        isAccessible ? "text-gray-600" : "text-gray-400"
                      )}
                    >
                      <Icon className="w-4 h-4" />
                      <span className="text-sm font-medium hidden sm:block">{step.title}</span>
                      {isCompleted && <span className="w-2 h-2 bg-green-500 rounded-full" />}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Error Display */}
          {appState.error && (
            <div className="max-w-7xl mx-auto px-6 py-4">
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-3">
                <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
                <div>
                  <h3 className="font-medium text-red-900">Error</h3>
                  <p className="text-red-700 text-sm">{appState.error}</p>
                </div>
                <button
                  onClick={() => setError('')}
                  className="ml-auto text-red-600 hover:text-red-700"
                >
                  ×
                </button>
              </div>
            </div>
          )}

          {/* Loading State */}
          {appState.loading && (
            <div className="max-w-7xl mx-auto px-6 py-12 text-center">
              <div className="inline-flex items-center gap-3 bg-blue-50 px-6 py-4 rounded-lg">
                <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                <span className="text-blue-700 font-medium">
                  {appState.currentStep === 'query-generation' && 'Generating optimized queries...'}
                  {appState.currentStep === 'search' && 'Searching academic databases...'}
                  {appState.currentStep === 'report' && 'Analyzing papers and generating report...'}
                </span>
              </div>
            </div>
          )}

          {/* Main Content */}
          {!appState.loading && (
            <main className="max-w-7xl mx-auto px-6 py-8">
              {appState.currentStep === 'config' && (
                <APIConfiguration
                  config={appState.apiConfig}
                  onConfigUpdate={handleConfigUpdate}
                  onContinue={handleConfigComplete}
                />
              )}

              {appState.currentStep === 'query-generation' && (
                <div className="max-w-2xl mx-auto text-center">
                  <div className="mb-8">
                    <Search className="w-12 h-12 text-blue-600 mx-auto mb-4" />
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">Enter Your Research Query</h2>
                    <p className="text-gray-600">
                      Describe your research topic, and our AI will generate optimized search queries
                      to find the most relevant academic papers.
                    </p>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <textarea
                        value={originalQuery}
                        onChange={(e) => setOriginalQuery(e.target.value)}
                        placeholder="Enter your research query here... (e.g., 'machine learning applications in healthcare diagnosis')"
                        className="w-full h-32 p-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none text-gray-900 placeholder-gray-500"
                        maxLength={500}
                      />
                      <div className="text-right text-sm text-gray-500 mt-1">
                        {originalQuery.length}/500 characters
                      </div>
                    </div>

                    <button
                      onClick={generateQueries}
                      disabled={!originalQuery.trim()}
                      className={cn(
                        "w-full py-3 px-6 rounded-lg font-medium transition-colors",
                        originalQuery.trim()
                          ? "bg-blue-600 text-white hover:bg-blue-700"
                          : "bg-gray-300 text-gray-500 cursor-not-allowed"
                      )}
                    >
                      Generate Research Queries
                    </button>
                  </div>
                </div>
              )}

              {appState.currentStep === 'query-selection' && (
                <QuerySelection
                  queries={appState.generatedQueries}
                  onQueriesUpdate={handleQueriesUpdate}
                  onContinue={handleQuerySelectionComplete}
                  onBack={goBack}
                  originalQuery={appState.originalQuery}
                />
              )}

              {appState.currentStep === 'results' && appState.searchResults && (
                <PaperResults
                  searchResult={appState.searchResults}
                  onExport={handleExport}
                  onGenerateReport={generateReport}
                  onBack={goBack}
                />
              )}

              {appState.currentStep === 'report' && appState.report && (
                <ReportDisplay
                  report={appState.report}
                  onBack={goBack}
                />
              )}
            </main>
          )}
        </>
      )}
    </div>
  );
}