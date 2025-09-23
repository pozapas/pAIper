import { NextRequest, NextResponse } from 'next/server';
import axios from 'axios';
import { AcademicPaper, ResearchQuery, APIConfig, SearchResult } from '@/types';
import { generateId, calculateRelevanceScore, delay } from '@/lib/utils';

interface SearchPapersRequest {
  queries: ResearchQuery[];
  apiConfig: APIConfig;
  maxResults?: number;
  sources?: ('google-scholar' | 'scopus')[];
}

export async function POST(request: NextRequest) {
  try {
    const { 
      queries, 
      apiConfig, 
      maxResults = 50,
      sources = ['google-scholar', 'scopus']
    }: SearchPapersRequest = await request.json();

    if (!queries || queries.length === 0) {
      return NextResponse.json({ error: 'At least one query is required' }, { status: 400 });
    }

    const allPapers: AcademicPaper[] = [];
    const queryResults: any[] = [];

    // Search with each query
    for (const query of queries) {
      if (!query.selected) continue;

      const queryPapers: AcademicPaper[] = [];

      // Search Google Scholar
      if (sources.includes('google-scholar') && apiConfig.googleScholarKey) {
        try {
          const scholarPapers = await searchGoogleScholar(
            query.refinedQuery,
            apiConfig.googleScholarKey,
            query.id,
            query.originalQuery,
            Math.ceil(maxResults / queries.filter(q => q.selected).length)
          );
          queryPapers.push(...scholarPapers);
          console.log(`Google Scholar found ${scholarPapers.length} papers for: ${query.refinedQuery}`);
        } catch (error) {
          console.error('Google Scholar search failed:', error);
        }
      }

      // Search Scopus
      if (sources.includes('scopus') && apiConfig.scopusKey) {
        try {
          const scopusPapers = await searchScopus(
            query.refinedQuery,
            apiConfig.scopusKey,
            query.id,
            query.originalQuery,
            Math.ceil(maxResults / queries.filter(q => q.selected).length)
          );
          queryPapers.push(...scopusPapers);
          console.log(`Scopus found ${scopusPapers.length} papers for: ${query.refinedQuery}`);
        } catch (error) {
          console.error('Scopus search failed:', error);
        }
      }

      queryResults.push({
        query: query.refinedQuery,
        papers: queryPapers
      });

      allPapers.push(...queryPapers);
    }

    // Remove duplicates based on title similarity and DOI
    const uniquePapers = removeDuplicates(allPapers);

    // Sort by relevance score and citation count
    uniquePapers.sort((a: AcademicPaper, b: AcademicPaper) => {
      const scoreA = (a.relevanceScore || 0) + (a.citationCount * 0.1);
      const scoreB = (b.relevanceScore || 0) + (b.citationCount * 0.1);
      return scoreB - scoreA;
    });

    const result: SearchResult = {
      papers: uniquePapers.slice(0, maxResults),
      totalFound: uniquePapers.length,
      queryResults
    };

    return NextResponse.json(result);
  } catch (error) {
    console.error('Paper search error:', error);
    return NextResponse.json(
      { error: 'Failed to search for papers' },
      { status: 500 }
    );
  }
}

async function searchGoogleScholar(
  query: string, 
  apiKey: string, 
  queryId: string, 
  originalQuery: string,
  maxResults: number = 20
): Promise<AcademicPaper[]> {
  const response = await axios.get('https://serpapi.com/search.json', {
    params: {
      engine: 'google_scholar',
      q: query,
      api_key: apiKey,
      num: maxResults,
      as_ylo: 2020, // Only recent papers
      as_vis: 0, // Include citations
      hl: 'en'
    }
  });

  if (!response.data.organic_results) {
    throw new Error('No results found');
  }

  const organicResults = response.data.organic_results || [];
  
  return organicResults.map((result: any): AcademicPaper => {
    const authors = result.publication_info?.authors?.map((author: any) => ({
      name: author.name || 'Unknown Author',
      affiliation: author.affiliation
    })) || [{ name: 'Unknown Author' }];

    // Try to get more complete abstract-like content
    let abstractContent = '';
    
    // First try snippet (always available)
    if (result.snippet) {
      abstractContent = result.snippet;
    }
    
    // Try to get more content from publication_info if available
    if (result.publication_info?.summary && result.publication_info.summary !== result.snippet) {
      abstractContent += (abstractContent ? ' ' : '') + result.publication_info.summary;
    }
    
    // Try to extract content from resources or other fields
    if (result.rich_snippet && result.rich_snippet.top && result.rich_snippet.top.detected_extensions) {
      const extensions = result.rich_snippet.top.detected_extensions;
      if (extensions.abstract) {
        abstractContent = extensions.abstract;
      }
    }

    return {
      id: generateId(),
      title: result.title || 'Untitled',
      authors,
      abstract: abstractContent || result.snippet || 'No abstract available',
      publicationDate: extractDateFromPublicationInfo(result.publication_info?.summary) || new Date().toISOString(),
      journal: extractJournalFromSummary(result.publication_info?.summary),
      doi: extractDOI(result.link),
      url: result.link,
      pdfUrl: result.resources?.find((r: any) => r.title?.toLowerCase().includes('pdf'))?.link,
      citationCount: parseInt(result.inline_links?.cited_by?.total || '0'),
      keywords: extractKeywordsFromSnippet(abstractContent || result.snippet || ''),
      source: 'google-scholar',
      queryId,
      relevanceScore: calculateRelevanceScore(originalQuery, result.title || '', abstractContent || result.snippet || '')
    };
  });
}

async function searchScopus(
  query: string,
  apiKey: string,
  queryId: string,
  originalQuery: string,
  maxResults: number = 20
): Promise<AcademicPaper[]> {
  const response = await axios.get('https://api.elsevier.com/content/search/scopus', {
    params: {
      query: `TITLE-ABS-KEY(${query})`,
      apikey: apiKey,
      count: maxResults,
      sort: 'citedby-count',
      field: 'title,creator,description,publicationName,coverDate,doi,citedby-count,link,abstract'
    },
    headers: {
      'Accept': 'application/json',
      'X-ELS-APIKey': apiKey
    }
  });

  const entries = response.data['search-results']?.entry || [];
  if (!entries || entries.length === 0) {
    return [];
  }
  
  return entries.map((entry: any): AcademicPaper => {
    const authors = entry.author?.map((author: any) => ({
      name: `${author['given-name'] || ''} ${author.surname || ''}`.trim() || 'Unknown Author',
      affiliation: author.affiliation?.[0]?.affilname
    })) || [{ name: 'Unknown Author' }];

    return {
      id: generateId(),
      title: entry['dc:title'] || 'Untitled',
      authors,
      abstract: entry['dc:description'] || '',
      publicationDate: entry['prism:coverDate'] || new Date().toISOString(),
      journal: entry['prism:publicationName'],
      doi: entry['prism:doi'],
      url: entry.link?.find((l: any) => l['@ref'] === 'scopus')?.['@href'],
      citationCount: parseInt(entry['citedby-count'] || '0'),
      keywords: extractKeywordsFromSnippet(entry['dc:description'] || ''),
      source: 'scopus',
      queryId,
      relevanceScore: calculateRelevanceScore(originalQuery, entry['dc:title'] || '', entry['dc:description'] || '')
    };
  });
}

function removeDuplicates(papers: AcademicPaper[]): AcademicPaper[] {
  const uniquePapers = new Map<string, AcademicPaper>();
  
  for (const paper of papers) {
    // Create a key based on normalized title and DOI
    const normalizedTitle = paper.title.toLowerCase().replace(/[^\w\s]/g, '').replace(/\s+/g, ' ').trim();
    const key = paper.doi || normalizedTitle;
    
    if (uniquePapers.has(key)) {
      const existing = uniquePapers.get(key)!;
      // Keep the paper with more complete data (longer abstract, more citations, etc.)
      if (paper.abstract.length > existing.abstract.length || 
          paper.citationCount > existing.citationCount ||
          (paper.doi && !existing.doi)) {
        uniquePapers.set(key, {
          ...existing,
          abstract: paper.abstract.length > existing.abstract.length ? paper.abstract : existing.abstract
        });
      }
    } else {
      uniquePapers.set(key, paper);
    }
  }
  
  return Array.from(uniquePapers.values());
}

// Helper functions
function extractDateFromPublicationInfo(summary?: string): string | undefined {
  if (!summary) return undefined;
  
  // Try to extract year from various formats
  const yearMatch = summary.match(/\b(19|20)\d{2}\b/);
  if (yearMatch) {
    return `${yearMatch[0]}-01-01T00:00:00.000Z`;
  }
  
  return undefined;
}

function extractJournalFromSummary(summary?: string): string | undefined {
  if (!summary) return undefined;
  
  // Try to extract journal name (very basic heuristic)
  const parts = summary.split(' - ');
  if (parts.length > 1) {
    return parts[parts.length - 1].trim();
  }
  
  return undefined;
}

function extractDOI(url?: string): string | undefined {
  if (!url) return undefined;
  
  // Extract DOI from URL
  const doiMatch = url.match(/doi\.org\/(.+)$/);
  if (doiMatch) {
    return doiMatch[1];
  }
  
  return undefined;
}

function extractKeywordsFromSnippet(text: string): string[] {
  if (!text || text.length < 50) return [];
  
  // Simple keyword extraction from abstract/snippet
  const words = text.toLowerCase()
    .replace(/[^\w\s]/g, ' ')
    .split(/\s+/)
    .filter(word => word.length > 4)
    .filter(word => !['abstract', 'introduction', 'conclusion', 'results', 'methods', 'this', 'that', 'with', 'from'].includes(word));
  
  // Get most frequent words
  const wordCount = new Map<string, number>();
  words.forEach(word => {
    wordCount.set(word, (wordCount.get(word) || 0) + 1);
  });
  
  return Array.from(wordCount.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([word]) => word);
}