import { NextRequest, NextResponse } from 'next/server';
import axios from 'axios';
import { generateId, extractKeywords } from '@/lib/utils';
import { ResearchQuery, APIConfig } from '@/types';

interface GenerateQueriesRequest {
  originalQuery: string;
  apiConfig: APIConfig;
  numQueries?: number;
}

export async function POST(request: NextRequest) {
  try {
    const { originalQuery, apiConfig, numQueries = 5 }: GenerateQueriesRequest = await request.json();
    
    console.log('Received request:', { originalQuery, hasApiConfig: !!apiConfig, numQueries });

    if (!originalQuery || !originalQuery.trim()) {
      return NextResponse.json({ error: 'Original query is required' }, { status: 400 });
    }

    const queries: ResearchQuery[] = [];

    // Try OpenRouter first if available
    if (apiConfig?.openRouterKey && apiConfig?.openRouterModel) {
      try {
        console.log('Trying OpenRouter generation...');
        const openRouterQueries = await generateQueriesWithOpenRouter(
          originalQuery, 
          apiConfig.openRouterKey, 
          numQueries,
          apiConfig.openRouterModel
        );
        queries.push(...openRouterQueries);
        console.log(`Generated ${openRouterQueries.length} queries with OpenRouter`);
      } catch (error) {
        console.error('OpenRouter generation failed:', error);
      }
    }

    // If we don't have enough queries, try Ollama
    if (queries.length < numQueries && apiConfig?.ollamaEndpoint && apiConfig?.ollamaModel) {
      try {
        console.log('Trying Ollama generation...');
        const ollamaQueries = await generateQueriesWithOllama(
          originalQuery, 
          apiConfig.ollamaEndpoint, 
          numQueries - queries.length,
          apiConfig.ollamaModel
        );
        queries.push(...ollamaQueries);
        console.log(`Generated ${ollamaQueries.length} queries with Ollama`);
      } catch (error) {
        console.error('Ollama generation failed:', error);
      }
    }

    // Always generate basic variations as fallback (this should always work)
    if (queries.length < numQueries) {
      console.log('Generating basic query variations...');
      try {
        const basicQueries = generateBasicQueryVariations(originalQuery, numQueries - queries.length);
        queries.push(...basicQueries);
        console.log(`Generated ${basicQueries.length} basic queries`);
      } catch (error) {
        console.error('Basic query generation failed:', error);
        // Last resort: return the original query
        queries.push({
          id: generateId(),
          originalQuery,
          refinedQuery: originalQuery,
          keywords: extractKeywords(originalQuery, 5),
          searchTerms: extractKeywords(originalQuery, 8),
          selected: false,
          confidence: 100,
          source: 'user'
        });
      }
    }

    console.log(`Returning ${queries.length} total queries`);
    return NextResponse.json({ queries });
  } catch (error) {
    console.error('Query generation error:', error);
    return NextResponse.json(
      { error: 'Failed to generate queries' },
      { status: 500 }
    );
  }
}

async function generateQueriesWithOpenRouter(
  originalQuery: string,
  apiKey: string,
  numQueries: number,
  model: string = 'google/gemini-2.5-flash'
): Promise<ResearchQuery[]> {
  const prompt = `You are an expert academic researcher. Given the research query below, generate ${numQueries} refined and diverse search queries that would help find relevant academic papers.

Original Query: "${originalQuery}"

Requirements:
1. Each query should be optimized for academic databases like Google Scholar and Scopus
2. Use proper academic terminology and keywords
3. Vary the approach: some broad, some specific, some with synonyms
4. Include Boolean operators where appropriate (AND, OR)
5. Consider different aspects of the research topic

Return the results as a JSON array with objects containing:
- refinedQuery: the optimized search query
- keywords: array of main keywords used
- searchTerms: array of specific search terms
- confidence: confidence score 0-100

Example format:
[
  {
    "refinedQuery": "machine learning AND healthcare diagnosis",
    "keywords": ["machine learning", "healthcare", "diagnosis"],
    "searchTerms": ["ML", "medical diagnosis", "clinical decision support"],
    "confidence": 85
  }
]`;

  const response = await axios.post(
    'https://openrouter.ai/api/v1/chat/completions',
    {
      model: model,
      messages: [
        {
          role: 'user',
          content: prompt
        }
      ],
      temperature: 0.7,
      max_tokens: 2000
    },
    {
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'HTTP-Referer': process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000',
        'X-Title': 'pAIper Research Tool',
        'Content-Type': 'application/json'
      }
    }
  );

  const content = response.data.choices[0]?.message?.content;
  if (!content) throw new Error('No response from OpenRouter');

  // Parse JSON from the response
  const jsonMatch = content.match(/\[[\s\S]*\]/);
  if (!jsonMatch) throw new Error('No JSON found in response');

  const queryData = JSON.parse(jsonMatch[0]);
  
  return queryData.map((q: any) => ({
    id: generateId(),
    originalQuery,
    refinedQuery: q.refinedQuery,
    keywords: q.keywords || [],
    searchTerms: q.searchTerms || [],
    selected: false,
    confidence: q.confidence || 75,
    source: 'openrouter' as const
  }));
}

async function generateQueriesWithOllama(
  originalQuery: string,
  endpoint: string,
  numQueries: number,
  model: string = 'llama3.1:8b'
): Promise<ResearchQuery[]> {
  const prompt = `Generate ${numQueries} academic search queries based on: "${originalQuery}"

Make each query optimized for academic databases. Vary the approach and terminology. Return as JSON array with refinedQuery, keywords, searchTerms, and confidence fields.`;

  const response = await axios.post(
    `${endpoint}/api/generate`,
    {
      model: model,
      prompt,
      stream: false,
      options: {
        temperature: 0.7,
        num_predict: 1000
      }
    },
    {
      timeout: 30000
    }
  );

  const content = response.data.response;
  if (!content) throw new Error('No response from Ollama');

  // Try to parse JSON from the response
  const jsonMatch = content.match(/\[[\s\S]*\]/);
  if (jsonMatch) {
    try {
      const queryData = JSON.parse(jsonMatch[0]);
      return queryData.map((q: any) => ({
        id: generateId(),
        originalQuery,
        refinedQuery: q.refinedQuery,
        keywords: q.keywords || [],
        searchTerms: q.searchTerms || [],
        selected: false,
        confidence: q.confidence || 70,
        source: 'ollama' as const
      }));
    } catch (parseError) {
      console.error('Failed to parse Ollama JSON response');
    }
  }

  // Fallback: extract queries from text response
  const lines = content.split('\n').filter((line: string) => line.trim());
  const queries: ResearchQuery[] = [];
  
  lines.forEach((line: string, index: number) => {
    if (index < numQueries && line.length > 10) {
      const cleanQuery = line.replace(/^\d+\.\s*/, '').replace(/^[-*]\s*/, '').trim();
      if (cleanQuery) {
        queries.push({
          id: generateId(),
          originalQuery,
          refinedQuery: cleanQuery,
          keywords: extractKeywords(cleanQuery, 5),
          searchTerms: extractKeywords(cleanQuery, 8),
          selected: false,
          confidence: 65,
          source: 'ollama'
        });
      }
    }
  });

  return queries;
}

function generateBasicQueryVariations(originalQuery: string, numQueries: number): ResearchQuery[] {
  const queries: ResearchQuery[] = [];
  const keywords = extractKeywords(originalQuery, 6);
  
  // Generate different query variations
  const variations = [
    `"${originalQuery}"`, // Exact phrase
    `${keywords.slice(0, 3).join(' AND ')}`, // Top 3 keywords with AND
    `${keywords.slice(0, 2).join(' OR ')} AND ${keywords[2] || ''}`, // OR combination
    `${originalQuery} review`, // Add "review"
    `${originalQuery} systematic review`, // Systematic review
    `${keywords[0]} AND (${keywords.slice(1, 3).join(' OR ')})`, // Boolean combination
    `${originalQuery} methodology`, // Add methodology
    `${originalQuery} analysis` // Add analysis
  ];

  for (let i = 0; i < Math.min(numQueries, variations.length); i++) {
    queries.push({
      id: generateId(),
      originalQuery,
      refinedQuery: variations[i],
      keywords: extractKeywords(variations[i], 5),
      searchTerms: extractKeywords(variations[i], 8),
      selected: false,
      confidence: 50,
      source: 'openrouter' // Default source for basic variations
    });
  }

  return queries;
}