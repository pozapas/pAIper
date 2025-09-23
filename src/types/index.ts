// API Configuration Types
export interface APIConfig {
  openRouterKey?: string;
  openRouterModel?: string;
  ollamaEndpoint?: string;
  ollamaModel?: string;
  googleScholarKey?: string;
  scopusKey?: string;
}

// Research Query Types
export interface ResearchQuery {
  id: string;
  originalQuery: string;
  refinedQuery: string;
  keywords: string[];
  searchTerms: string[];
  selected: boolean;
  confidence?: number;
  source: 'openrouter' | 'ollama' | 'user';
}

// Academic Paper Types
export interface Author {
  name: string;
  affiliation?: string;
  email?: string;
}

export interface Citation {
  count: number;
  url?: string;
}

export interface AcademicPaper {
  id: string;
  title: string;
  authors: Author[];
  abstract: string;
  publicationDate: string;
  journal?: string;
  conference?: string;
  publisher?: string;
  doi?: string;
  url?: string;
  pdfUrl?: string;
  citationCount: number;
  keywords?: string[];
  source: 'google-scholar' | 'scopus';
  queryId: string; // Which query found this paper
  relevanceScore?: number;
}

// Report Types
export interface ResearchReport {
  id: string;
  title: string;
  executiveSummary: string;
  literatureOverview: string;
  thematicAnalysis: string;
  methodologicalSynthesis: string;
  researchGaps: string;
  implications: string;
  references: ApaReference[];
  generatedAt: Date;
  wordCount: number;
  paperCount: number;
}

export interface ApaReference {
  id: string;
  authors: string;
  year: string;
  title: string;
  journal?: string;
  volume?: string;
  issue?: string;
  pages?: string;
  doi?: string;
  url?: string;
  citation: string; // Full APA formatted citation
}

// Search Types
export interface SearchParams {
  queries: ResearchQuery[];
  sources: ('google-scholar' | 'scopus')[];
  dateRange?: {
    from: Date;
    to: Date;
  };
  maxResults: number;
  sortBy: 'relevance' | 'date' | 'citations';
}

export interface SearchResult {
  papers: AcademicPaper[];
  totalFound: number;
  queryResults: {
    queryId: string;
    count: number;
    papers: AcademicPaper[];
  }[];
}

// UI State Types
export interface AppState {
  currentStep: 'welcome' | 'config' | 'query-generation' | 'query-selection' | 'search' | 'results' | 'report';
  apiConfig: APIConfig;
  originalQuery: string;
  generatedQueries: ResearchQuery[];
  selectedQueries: ResearchQuery[];
  searchResults: SearchResult | null;
  report: ResearchReport | null;
  loading: boolean;
  error: string | null;
}

// Export Types
export interface ExportOptions {
  format: 'csv' | 'json' | 'bibtex';
  includeAbstracts: boolean;
  includeKeywords: boolean;
  sortBy: keyof AcademicPaper;
}

// AI Model Types
export interface AIModel {
  provider: 'openrouter' | 'ollama';
  name: string;
  endpoint?: string;
  maxTokens: number;
  temperature: number;
}

// Error Types
export interface APIError {
  code: string;
  message: string;
  details?: any;
}