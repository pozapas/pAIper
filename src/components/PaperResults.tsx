'use client';

import React, { useState, useMemo } from 'react';
import { 
  FileText, 
  Users, 
  Calendar, 
  Quote, 
  ExternalLink, 
  Download,
  Filter,
  SortAsc,
  Star,
  Tag,
  ChevronDown,
  ChevronUp,
  Info,
  Search,
  BookOpen
} from 'lucide-react';
import { AcademicPaper, SearchResult, ExportOptions } from '@/types';
import { formatDate, truncateText } from '@/lib/utils';
import { cn } from '@/lib/utils';

interface PaperResultsProps {
  searchResult: SearchResult;
  onExport: (options: ExportOptions) => void;
  onGenerateReport: () => void;
  onBack: () => void;
}

type SortOption = 'relevance' | 'citations' | 'date' | 'title';
type FilterOption = 'all' | 'google-scholar' | 'scopus';

export default function PaperResults({ 
  searchResult, 
  onExport, 
  onGenerateReport, 
  onBack 
}: PaperResultsProps) {
  const [sortBy, setSortBy] = useState<SortOption>('relevance');
  const [filterBy, setFilterBy] = useState<FilterOption>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedPapers, setExpandedPapers] = useState<Set<string>>(new Set());
  const [showExportOptions, setShowExportOptions] = useState(false);

  const filteredAndSortedPapers = useMemo(() => {
    let papers = [...searchResult.papers];

    // Filter by source
    if (filterBy !== 'all') {
      papers = papers.filter(p => p.source === filterBy);
    }

    // Filter by search term
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      papers = papers.filter(p => 
        p.title.toLowerCase().includes(term) ||
        p.abstract.toLowerCase().includes(term) ||
        p.authors.some(a => a.name.toLowerCase().includes(term)) ||
        p.journal?.toLowerCase().includes(term) ||
        p.keywords?.some(k => k.toLowerCase().includes(term))
      );
    }

    // Sort papers
    papers.sort((a, b) => {
      switch (sortBy) {
        case 'relevance':
          return (b.relevanceScore || 0) - (a.relevanceScore || 0);
        case 'citations':
          return b.citationCount - a.citationCount;
        case 'date':
          return new Date(b.publicationDate).getTime() - new Date(a.publicationDate).getTime();
        case 'title':
          return a.title.localeCompare(b.title);
        default:
          return 0;
      }
    });

    return papers;
  }, [searchResult.papers, sortBy, filterBy, searchTerm]);

  const togglePaperExpansion = (paperId: string) => {
    const newExpanded = new Set(expandedPapers);
    if (newExpanded.has(paperId)) {
      newExpanded.delete(paperId);
    } else {
      newExpanded.add(paperId);
    }
    setExpandedPapers(newExpanded);
  };

  const handleExport = (format: 'csv' | 'json' | 'bibtex') => {
    const options: ExportOptions = {
      format,
      includeAbstracts: true,
      includeKeywords: true,
      sortBy: sortBy as keyof AcademicPaper
    };
    onExport(options);
    setShowExportOptions(false);
  };

  const getSourceBadgeColor = (source: string) => {
    return source === 'google-scholar' 
      ? 'bg-blue-100 text-blue-800 border-blue-200' 
      : 'bg-green-100 text-green-800 border-green-200';
  };

  const getRelevanceColor = (score?: number) => {
    if (!score) return 'text-gray-400';
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-orange-600';
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <FileText className="w-6 h-6 text-blue-600" />
          <h2 className="text-2xl font-bold text-gray-900">Research Papers</h2>
          <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm font-medium">
            {searchResult.totalFound} found
          </span>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={onBack}
            className="px-4 py-2 text-gray-600 hover:text-gray-700 font-medium"
          >
            ← Back to Queries
          </button>
          
          <button
            onClick={onGenerateReport}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 font-medium flex items-center gap-2"
          >
            <BookOpen className="w-4 h-4" />
            Generate Report
          </button>

          <div className="relative">
            <button
              onClick={() => setShowExportOptions(!showExportOptions)}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
              Export
              <ChevronDown className="w-4 h-4" />
            </button>

            {showExportOptions && (
              <div className="absolute right-0 top-full mt-2 bg-white border rounded-md shadow-lg z-10 min-w-36">
                <button
                  onClick={() => handleExport('csv')}
                  className="w-full px-4 py-2 text-left hover:bg-gray-50 first:rounded-t-md"
                >
                  Export as CSV
                </button>
                <button
                  onClick={() => handleExport('json')}
                  className="w-full px-4 py-2 text-left hover:bg-gray-50"
                >
                  Export as JSON
                </button>
                <button
                  onClick={() => handleExport('bibtex')}
                  className="w-full px-4 py-2 text-left hover:bg-gray-50 last:rounded-b-md"
                >
                  Export as BibTeX
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="bg-gray-50 rounded-lg p-4 mb-6">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search papers by title, author, journal..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Sort */}
          <div className="flex items-center gap-2">
            <SortAsc className="w-4 h-4 text-gray-500" />
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as SortOption)}
              className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="relevance">Relevance</option>
              <option value="citations">Citations</option>
              <option value="date">Date</option>
              <option value="title">Title</option>
            </select>
          </div>

          {/* Filter */}
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-gray-500" />
            <select
              value={filterBy}
              onChange={(e) => setFilterBy(e.target.value as FilterOption)}
              className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Sources</option>
              <option value="google-scholar">Google Scholar</option>
              <option value="scopus">Scopus</option>
            </select>
          </div>
        </div>

        <div className="mt-3 text-sm text-gray-600">
          Showing {filteredAndSortedPapers.length} of {searchResult.totalFound} papers
        </div>
      </div>

      {/* Papers List */}
      <div className="space-y-4">
        {filteredAndSortedPapers.map((paper) => (
          <div key={paper.id} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
            {/* Paper Header */}
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <h3 className="text-xl font-semibold text-gray-900 mb-2 leading-tight">
                  {paper.title}
                </h3>

                <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
                  <div className="flex items-center gap-1">
                    <Users className="w-4 h-4" />
                    <span>{paper.authors.map(a => a.name).join(', ')}</span>
                  </div>
                  
                  <div className="flex items-center gap-1">
                    <Calendar className="w-4 h-4" />
                    <span>{formatDate(paper.publicationDate)}</span>
                  </div>

                  {paper.citationCount > 0 && (
                    <div className="flex items-center gap-1">
                      <Quote className="w-4 h-4" />
                      <span>{paper.citationCount} citations</span>
                    </div>
                  )}
                </div>

                {paper.journal && (
                  <div className="text-sm text-gray-600 mb-3 italic">
                    Published in: {paper.journal}
                  </div>
                )}
              </div>

              <div className="flex flex-col items-end gap-2 ml-4">
                {/* Source Badge */}
                <span className={cn(
                  "px-2 py-1 text-xs font-medium rounded-full border",
                  getSourceBadgeColor(paper.source)
                )}>
                  {paper.source === 'google-scholar' ? 'Google Scholar' : 'Scopus'}
                </span>

                {/* Relevance Score */}
                {paper.relevanceScore && (
                  <div className="flex items-center gap-1">
                    <Star className={cn("w-3 h-3", getRelevanceColor(paper.relevanceScore))} />
                    <span className={cn("text-xs font-medium", getRelevanceColor(paper.relevanceScore))}>
                      {Math.round(paper.relevanceScore)}% match
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Abstract Preview */}
            <div className="mb-4">
              <p className="text-gray-700 leading-relaxed">
                {expandedPapers.has(paper.id) 
                  ? paper.abstract 
                  : truncateText(paper.abstract, 300)
                }
              </p>
              
              {paper.abstract.length > 300 && (
                <button
                  onClick={() => togglePaperExpansion(paper.id)}
                  className="text-blue-600 hover:text-blue-700 text-sm font-medium mt-2 flex items-center gap-1"
                >
                  {expandedPapers.has(paper.id) ? (
                    <>Show less <ChevronUp className="w-4 h-4" /></>
                  ) : (
                    <>Show more <ChevronDown className="w-4 h-4" /></>
                  )}
                </button>
              )}
            </div>

            {/* Keywords */}
            {paper.keywords && paper.keywords.length > 0 && (
              <div className="mb-4">
                <div className="flex items-center gap-1 mb-2">
                  <Tag className="w-3 h-3 text-gray-400" />
                  <span className="text-xs text-gray-500 font-medium">Keywords:</span>
                </div>
                <div className="flex flex-wrap gap-1">
                  {paper.keywords.map((keyword, index) => (
                    <span
                      key={index}
                      className="inline-block px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="flex items-center justify-between pt-3 border-t border-gray-200">
              <div className="flex items-center gap-4 text-sm">
                {paper.doi && (
                  <span className="text-gray-600">
                    DOI: {paper.doi}
                  </span>
                )}
              </div>

              <div className="flex items-center gap-2">
                {paper.pdfUrl && (
                  <a
                    href={paper.pdfUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-3 py-1 text-sm text-red-600 hover:text-red-700 font-medium flex items-center gap-1"
                  >
                    <Download className="w-3 h-3" />
                    PDF
                  </a>
                )}
                
                {paper.url && (
                  <a
                    href={paper.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-3 py-1 text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center gap-1"
                  >
                    <ExternalLink className="w-3 h-3" />
                    View Paper
                  </a>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredAndSortedPapers.length === 0 && (
        <div className="text-center py-12">
          <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No papers found</h3>
          <p className="text-gray-600">
            {searchTerm ? 'Try adjusting your search terms or filters.' : 'No papers match your current query.'}
          </p>
        </div>
      )}
    </div>
  );
}