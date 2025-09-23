'use client';

import React, { useState } from 'react';
import { Search, CheckCircle, Circle, Star, Tag, Brain, Zap, ChevronRight, Plus, X } from 'lucide-react';
import { ResearchQuery } from '@/types';
import { cn, generateId } from '@/lib/utils';

interface QuerySelectionProps {
  queries: ResearchQuery[];
  onQueriesUpdate: (queries: ResearchQuery[]) => void;
  onContinue: () => void;
  onBack: () => void;
  originalQuery: string;
}

export default function QuerySelection({ 
  queries, 
  onQueriesUpdate, 
  onContinue, 
  onBack, 
  originalQuery 
}: QuerySelectionProps) {
  const [previewQuery, setPreviewQuery] = useState<string | null>(null);
  const [showAddCustom, setShowAddCustom] = useState(false);
  const [customQuery, setCustomQuery] = useState('');
  const [customKeywords, setCustomKeywords] = useState('');

  const toggleQuerySelection = (queryId: string) => {
    const updatedQueries = queries.map(q => 
      q.id === queryId ? { ...q, selected: !q.selected } : q
    );
    onQueriesUpdate(updatedQueries);
  };

  const selectAll = () => {
    const updatedQueries = queries.map(q => ({ ...q, selected: true }));
    onQueriesUpdate(updatedQueries);
  };

  const deselectAll = () => {
    const updatedQueries = queries.map(q => ({ ...q, selected: false }));
    onQueriesUpdate(updatedQueries);
  };

  const addCustomQuery = () => {
    if (!customQuery.trim()) return;

    const keywords = customKeywords
      .split(',')
      .map(k => k.trim())
      .filter(k => k.length > 0);

    const newQuery: ResearchQuery = {
      id: generateId(),
      originalQuery: originalQuery,
      refinedQuery: customQuery.trim(),
      keywords: keywords,
      searchTerms: keywords,
      selected: true,
      source: 'user' as any, // Custom source for user-added queries
    };

    const updatedQueries = [...queries, newQuery];
    onQueriesUpdate(updatedQueries);

    // Reset form
    setCustomQuery('');
    setCustomKeywords('');
    setShowAddCustom(false);
  };

  const selectedQueries = queries.filter(q => q.selected);

  const getSourceIcon = (source: string) => {
    switch (source) {
      case 'openrouter':
        return <Brain className="w-4 h-4 text-blue-500" />;
      case 'ollama':
        return <Zap className="w-4 h-4 text-purple-500" />;
      case 'user':
        return <Search className="w-4 h-4 text-green-600" />;
      default:
        return <Search className="w-4 h-4 text-gray-500" />;
    }
  };

  const getConfidenceColor = (confidence?: number) => {
    if (!confidence) return 'text-gray-400';
    if (confidence >= 80) return 'text-green-600';
    if (confidence >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="flex items-center gap-3 mb-6">
        <Search className="w-6 h-6 text-blue-600" />
        <h2 className="text-2xl font-bold text-gray-900">Select Research Queries</h2>
      </div>

      <div className="mb-6">
        <div className="bg-blue-50 rounded-lg p-4">
          <h3 className="font-medium text-gray-900 mb-2">Original Query:</h3>
          <p className="text-gray-700 italic">"{originalQuery}"</p>
        </div>
      </div>

      {/* Add Custom Query Section */}
      <div className="mb-6">
        {!showAddCustom ? (
          <button
            onClick={() => setShowAddCustom(true)}
            className="flex items-center gap-2 px-4 py-2 bg-green-50 text-green-700 rounded-lg hover:bg-green-100 transition-colors border border-green-200"
          >
            <Plus className="w-4 h-4" />
            Add Custom Search Query
          </button>
        ) : (
          <div className="bg-green-50 rounded-lg p-4 border border-green-200">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-medium text-gray-900">Add Custom Query</h3>
              <button
                onClick={() => {
                  setShowAddCustom(false);
                  setCustomQuery('');
                  setCustomKeywords('');
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Search Query
                </label>
                <input
                  type="text"
                  value={customQuery}
                  onChange={(e) => setCustomQuery(e.target.value)}
                  placeholder="Enter your custom search query (e.g., artificial intelligence education methods)"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Keywords (optional)
                </label>
                <input
                  type="text"
                  value={customKeywords}
                  onChange={(e) => setCustomKeywords(e.target.value)}
                  placeholder="Enter keywords separated by commas (e.g., AI, machine learning, education)"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>
              
              <div className="flex justify-end gap-2">
                <button
                  onClick={() => {
                    setShowAddCustom(false);
                    setCustomQuery('');
                    setCustomKeywords('');
                  }}
                  className="px-3 py-2 text-gray-600 hover:text-gray-700 font-medium"
                >
                  Cancel
                </button>
                <button
                  onClick={addCustomQuery}
                  disabled={!customQuery.trim()}
                  className={cn(
                    "px-4 py-2 rounded-md font-medium transition-colors",
                    customQuery.trim()
                      ? "bg-green-600 text-white hover:bg-green-700"
                      : "bg-gray-300 text-gray-500 cursor-not-allowed"
                  )}
                >
                  Add Query
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-600">
            {selectedQueries.length} of {queries.length} queries selected
          </span>
          <div className="flex gap-2">
            <button
              onClick={selectAll}
              className="text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              Select All
            </button>
            <span className="text-gray-300">|</span>
            <button
              onClick={deselectAll}
              className="text-sm text-gray-600 hover:text-gray-700 font-medium"
            >
              Deselect All
            </button>
          </div>
        </div>

        <div className="text-sm text-gray-500">
          Generated by AI • Click to select queries
        </div>
      </div>

      <div className="space-y-3 mb-6">
        {queries.map((query) => (
          <div
            key={query.id}
            className={cn(
              "border rounded-lg p-4 transition-all cursor-pointer hover:shadow-md",
              query.selected 
                ? "border-blue-300 bg-blue-50" 
                : "border-gray-200 bg-white hover:border-gray-300"
            )}
            onClick={() => toggleQuerySelection(query.id)}
          >
            <div className="flex items-start gap-3">
              {/* Selection Checkbox */}
              <div className="flex-shrink-0 mt-1">
                {query.selected ? (
                  <CheckCircle className="w-5 h-5 text-blue-600" />
                ) : (
                  <Circle className="w-5 h-5 text-gray-400" />
                )}
              </div>

              {/* Query Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-2">
                  {getSourceIcon(query.source)}
                  <span className="text-xs text-gray-500 uppercase tracking-wide font-medium">
                    {query.source === 'user' ? 'Custom Query' : query.source}
                  </span>
                  {query.confidence && (
                    <div className="flex items-center gap-1">
                      <Star className={cn("w-3 h-3", getConfidenceColor(query.confidence))} />
                      <span className={cn("text-xs font-medium", getConfidenceColor(query.confidence))}>
                        {query.confidence}%
                      </span>
                    </div>
                  )}
                </div>

                <div className="mb-2">
                  <p className="text-gray-900 font-medium leading-relaxed">
                    {query.refinedQuery}
                  </p>
                </div>

                {/* Keywords */}
                {query.keywords.length > 0 && (
                  <div className="mb-2">
                    <div className="flex items-center gap-1 mb-1">
                      <Tag className="w-3 h-3 text-gray-400" />
                      <span className="text-xs text-gray-500">Keywords:</span>
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {query.keywords.slice(0, 6).map((keyword, index) => (
                        <span
                          key={index}
                          className="inline-block px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full"
                        >
                          {keyword}
                        </span>
                      ))}
                      {query.keywords.length > 6 && (
                        <span className="inline-block px-2 py-1 bg-gray-100 text-gray-500 text-xs rounded-full">
                          +{query.keywords.length - 6} more
                        </span>
                      )}
                    </div>
                  </div>
                )}

                {/* Search Terms Preview */}
                {query.searchTerms.length > 0 && (
                  <div className="text-xs text-gray-500">
                    <span className="font-medium">Search terms: </span>
                    {query.searchTerms.slice(0, 4).join(', ')}
                    {query.searchTerms.length > 4 && '...'}
                  </div>
                )}
              </div>

              {/* Preview Button */}
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setPreviewQuery(previewQuery === query.id ? null : query.id);
                }}
                className="flex-shrink-0 p-2 text-gray-400 hover:text-gray-600 rounded"
              >
                <ChevronRight 
                  className={cn(
                    "w-4 h-4 transition-transform",
                    previewQuery === query.id ? "rotate-90" : ""
                  )} 
                />
              </button>
            </div>

            {/* Expanded Preview */}
            {previewQuery === query.id && (
              <div className="mt-3 pt-3 border-t border-gray-200">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <h4 className="font-medium text-gray-700 mb-1">Expected Results:</h4>
                    <p className="text-gray-600 text-xs">
                      This query will search for academic papers related to the main keywords
                      and should return papers with varying degrees of relevance.
                    </p>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-700 mb-1">Search Strategy:</h4>
                    <p className="text-gray-600 text-xs">
                      {query.refinedQuery.includes('AND') && 'Uses AND logic for precise results. '}
                      {query.refinedQuery.includes('OR') && 'Uses OR logic for broader coverage. '}
                      {query.refinedQuery.includes('"') && 'Includes exact phrase matching. '}
                      Optimized for academic databases.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Summary and Actions */}
      <div className="border-t pt-6">
        <div className="flex items-center justify-between">
          <button
            onClick={onBack}
            className="px-4 py-2 text-gray-600 hover:text-gray-700 font-medium"
          >
            ← Back to Configuration
          </button>

          <div className="flex items-center gap-4">
            <div className="text-sm text-gray-600">
              Ready to search with <span className="font-semibold">{selectedQueries.length}</span> queries
            </div>
            <button
              onClick={onContinue}
              disabled={selectedQueries.length === 0}
              className={cn(
                "px-6 py-2 rounded-md font-medium transition-colors",
                selectedQueries.length > 0
                  ? "bg-blue-600 text-white hover:bg-blue-700"
                  : "bg-gray-300 text-gray-500 cursor-not-allowed"
              )}
            >
              Search Papers →
            </button>
          </div>
        </div>

        {selectedQueries.length === 0 && (
          <div className="mt-2 text-sm text-gray-500">
            Select at least one query to continue to the search phase.
          </div>
        )}
      </div>
    </div>
  );
}