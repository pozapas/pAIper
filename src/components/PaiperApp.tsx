'use client';

import React, { useState } from 'react';
import { APIConfig, ResearchQuery, SearchResult, ResearchReport, AppState, ExportOptions } from '@/types';
import APIConfiguration from '@/components/APIConfiguration';
import QuerySelection from '@/components/QuerySelection';
import PaperResults from '@/components/PaperResults';
import ReportDisplay from '@/components/ReportDisplay';
import { HeroSection } from '@/components/ui/hero-section';
import { StepNavigation, PageTransition, AppStep } from '@/components/ui/step-navigation';
import { AnimatedGroup } from '@/components/ui/animated-group';
import { Brain, Search, FileText, BookOpen, AlertCircle, Sparkles, X } from 'lucide-react';
import { cn } from '@/lib/utils';
import { 
  exportPapersToCSV, 
  exportPapersToJSON, 
  exportPapersToBibTeX
} from '@/lib/export';

export default function PaiperApp() {
  const [appState, setAppState] = useState<AppState>({
    currentStep: 'welcome',
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

  // Track completed steps
  const [completedSteps, setCompletedSteps] = useState<AppStep[]>([]);

  const markStepCompleted = (step: AppStep) => {
    if (!completedSteps.includes(step)) {
      setCompletedSteps(prev => [...prev, step]);
    }
  };

  const setLoading = (loading: boolean, error: string | null = null) => {
    setAppState(prev => ({ ...prev, loading, error }));
  };

  const setError = (error: string) => {
    setAppState(prev => ({ ...prev, error, loading: false }));
  };

  // Navigation functions
  const goToStep = (step: AppStep) => {
    setAppState(prev => ({ ...prev, currentStep: step }));
  };

  const goBack = () => {
    const stepOrder: AppStep[] = ['welcome', 'config', 'query-generation', 'query-selection', 'search', 'results', 'report'];
    const currentIndex = stepOrder.indexOf(appState.currentStep);
    if (currentIndex > 0) {
      goToStep(stepOrder[currentIndex - 1]);
    }
  };

  // Start research from welcome screen
  const startResearch = () => {
    setAppState(prev => ({ ...prev, currentStep: 'config' }));
  };

  // Step 1: API Configuration
  const handleConfigUpdate = (config: APIConfig) => {
    setAppState(prev => ({ ...prev, apiConfig: config }));
  };

  const handleConfigComplete = () => {
    markStepCompleted('config');
    setAppState(prev => ({ ...prev, currentStep: 'query-generation' }));
  };

  // Step 2: Query Generation
  const generateQueries = async () => {
    if (!originalQuery.trim()) {
      setError('Please enter a research query');
      return;
    }

    setLoading(true);
    setAppState(prev => ({ ...prev, originalQuery }));

    try {
      const response = await fetch('/api/generate-queries', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          originalQuery: originalQuery,
          apiConfig: appState.apiConfig, // Can be undefined - will use basic query generation
          numQueries: 5
        })
      });

      if (!response.ok) {
        throw new Error('Failed to generate queries');
      }

      const data = await response.json();
      setAppState(prev => ({ 
        ...prev, 
        generatedQueries: data.queries,
        currentStep: 'query-selection',
        loading: false
      }));
      markStepCompleted('query-generation');
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to generate queries');
    }
  };

  // Step 3: Query Selection
  const handleQueriesUpdate = (queries: ResearchQuery[]) => {
    setAppState(prev => ({ ...prev, generatedQueries: queries }));
  };

  const handleQuerySelectionComplete = async () => {
    const selectedQueries = appState.generatedQueries.filter(q => q.selected);
    if (selectedQueries.length === 0) {
      setError('Please select at least one query');
      return;
    }

    markStepCompleted('query-selection');
    setAppState(prev => ({ 
      ...prev, 
      selectedQueries,
      currentStep: 'search'
    }));

    // Immediately start searching
    await searchPapers(selectedQueries);
  };

  // Step 4: Paper Search
  const searchPapers = async (queries: ResearchQuery[]) => {
    setLoading(true);

    try {
      const response = await fetch('/api/search-papers', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          queries,
          apiConfig: appState.apiConfig,
          maxResults: 50
        })
      });

      if (!response.ok) {
        throw new Error('Failed to search papers');
      }

      const searchResults = await response.json();
      setAppState(prev => ({ 
        ...prev, 
        searchResults,
        currentStep: 'results',
        loading: false
      }));
      markStepCompleted('search');
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to search papers');
    }
  };

  // Step 5: Export & Report Generation
  const handleExport = async (options: ExportOptions) => {
    if (!appState.searchResults) return;

    try {
      const papers = appState.searchResults.papers;

      switch (options.format) {
        case 'csv':
          exportPapersToCSV(papers, options);
          break;
        case 'json':
          exportPapersToJSON(papers);
          break;
        case 'bibtex':
          exportPapersToBibTeX(papers);
          break;
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to export papers');
    }
  };

  const generateReport = async () => {
    if (!appState.searchResults) return;

    setLoading(true);
    setAppState(prev => ({ ...prev, currentStep: 'report' }));

    try {
      const response = await fetch('/api/generate-report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          papers: appState.searchResults.papers,
          originalQuery: appState.originalQuery,
          apiConfig: appState.apiConfig
        })
      });

      if (!response.ok) {
        throw new Error('Failed to generate report');
      }

      const { report } = await response.json();
      setAppState(prev => ({ 
        ...prev, 
        report,
        loading: false
      }));
      markStepCompleted('results');
      markStepCompleted('report');
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to generate report');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-muted/10 to-background">
      {/* Welcome Screen */}
      {appState.currentStep === 'welcome' && (
        <div className="h-screen">
          <HeroSection onStartResearch={startResearch} />
        </div>
      )}

      {/* Main Application */}
      {appState.currentStep !== 'welcome' && (
        <>
          <StepNavigation
            currentStep={appState.currentStep}
            completedSteps={completedSteps}
            onStepChange={goToStep}
            onBack={goBack}
          />

          {/* Error Display */}
          {appState.error && (
            <div className="max-w-7xl mx-auto px-6 py-4">
              <AnimatedGroup preset="slide">
                <div className="glass rounded-2xl p-6 flex items-start gap-4 border-destructive/20 bg-destructive/5 shadow-modern">
                  <div className="w-10 h-10 rounded-xl bg-destructive/10 flex items-center justify-center shrink-0">
                    <AlertCircle className="w-5 h-5 text-destructive" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-foreground mb-1">Oops! Something went wrong</h3>
                    <p className="text-muted-foreground text-sm leading-relaxed">{appState.error}</p>
                  </div>
                  <button
                    onClick={() => setError('')}
                    className="text-muted-foreground hover:text-foreground transition-colors p-1"
                    aria-label="Dismiss error"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </AnimatedGroup>
            </div>
          )}

          {/* Loading State */}
          {appState.loading && (
            <div className="fixed inset-0 bg-background/50 backdrop-blur-md z-50 flex items-center justify-center">
              <div className="glass rounded-3xl p-10 shadow-modern-xl max-w-md mx-4">
                <AnimatedGroup preset="scale">
                  <div className="text-center">
                    <div className="relative w-20 h-20 mx-auto mb-6">
                      <div className="absolute inset-0 border-4 border-muted rounded-full"></div>
                      <div className="absolute inset-0 border-4 border-primary rounded-full border-t-transparent animate-spin"></div>
                      <div className="absolute inset-4 gradient-primary rounded-full flex items-center justify-center">
                        <Sparkles className="w-6 h-6 text-white animate-pulse" />
                      </div>
                    </div>
                    <h3 className="text-xl font-bold text-foreground mb-3">
                      {appState.currentStep === 'query-generation' && 'Creating Smart Queries'}
                      {appState.currentStep === 'search' && 'Searching Academic Papers'}
                      {appState.currentStep === 'report' && 'Generating Your Report'}
                    </h3>
                    <p className="text-muted-foreground leading-relaxed">
                      {appState.currentStep === 'query-generation' && 'Our AI is crafting optimized search queries tailored to your research topic...'}
                      {appState.currentStep === 'search' && 'Scanning thousands of academic papers across multiple databases...'}
                      {appState.currentStep === 'report' && 'Analyzing findings and creating a comprehensive literature review...'}
                    </p>
                  </div>
                </AnimatedGroup>
              </div>
            </div>
          )}

          {/* Main Content */}
          {!appState.loading && (
            <main className="max-w-7xl mx-auto px-6 py-8">
              <PageTransition currentStep={appState.currentStep}>
                {appState.currentStep === 'config' && (
                  <div className="max-w-4xl mx-auto">
                    <AnimatedGroup preset="slide">
                      <div className="text-center mb-12">
                        <div className="w-16 h-16 gradient-primary rounded-2xl flex items-center justify-center mx-auto mb-6">
                          <Brain className="w-8 h-8 text-white" />
                        </div>
                        <h2 className="text-4xl font-bold text-foreground mb-4">
                          Quick Setup
                        </h2>
                        <p className="text-muted-foreground max-w-2xl mx-auto text-lg leading-relaxed">
                          Connect your AI provider and academic database access to unlock the full power of intelligent research discovery.
                        </p>
                      </div>
                    </AnimatedGroup>
                    <APIConfiguration
                      config={appState.apiConfig}
                      onConfigUpdate={handleConfigUpdate}
                      onContinue={handleConfigComplete}
                    />
                  </div>
                )}

                {appState.currentStep === 'query-generation' && (
                  <div className="max-w-4xl mx-auto">
                    <AnimatedGroup preset="blur-slide">
                      <div className="text-center mb-12">
                        <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
                          <Search className="w-8 h-8 text-white" />
                        </div>
                        <h2 className="text-4xl font-bold text-foreground mb-4">
                          Describe Your Research Topic
                        </h2>
                        <p className="text-muted-foreground max-w-2xl mx-auto text-lg leading-relaxed">
                          Tell us about your research interest in your own words. Our AI will create multiple smart search queries to find the most relevant papers.
                        </p>
                      </div>

                      <div className="glass rounded-3xl p-10 shadow-modern-xl">
                        <div className="space-y-8">
                          <div>
                            <label className="block text-lg font-semibold text-foreground mb-4">
                              What would you like to research?
                            </label>
                            <textarea
                              value={originalQuery}
                              onChange={(e) => setOriginalQuery(e.target.value)}
                              placeholder="Example: How does machine learning help predict climate change patterns and improve early warning systems?"
                              className="w-full h-40 p-6 border-2 border-border rounded-2xl focus:outline-none focus:ring-4 focus:ring-primary/20 focus:border-primary resize-none text-foreground placeholder-muted-foreground bg-background transition-all text-lg leading-relaxed"
                              maxLength={500}
                            />
                            <div className="flex justify-between items-center mt-4">
                              <div className="text-sm text-muted-foreground">
                                💡 <strong>Tip:</strong> Be specific about your research focus for better results
                              </div>
                              <div className="text-sm text-muted-foreground">
                                {originalQuery.length}/500 characters
                              </div>
                            </div>
                          </div>

                          <button
                            onClick={generateQueries}
                            disabled={!originalQuery.trim()}
                            className={cn(
                              "w-full py-6 px-8 rounded-2xl font-semibold text-lg transition-all duration-300 transform",
                              originalQuery.trim()
                                ? "gradient-primary text-white hover:opacity-90 shadow-modern-lg hover:shadow-modern-xl hover:scale-[1.02]"
                                : "bg-muted text-muted-foreground cursor-not-allowed"
                            )}
                          >
                            <Sparkles className="w-5 h-5 mr-2 inline" />
                            Generate Smart Search Queries
                          </button>
                        </div>
                      </div>
                    </AnimatedGroup>
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
              </PageTransition>
            </main>
          )}
        </>
      )}
    </div>
  );
}