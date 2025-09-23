import { NextRequest, NextResponse } from 'next/server';
import axios from 'axios';
import { AcademicPaper, ResearchReport, APIConfig, ApaReference } from '@/types';
import { generateId } from '@/lib/utils';
import { paperToApaReference, generateInTextCitation, sortReferencesApa } from '@/lib/apa-citations';

interface GenerateReportRequest {
  papers: AcademicPaper[];
  originalQuery: string;
  apiConfig: APIConfig;
  reportTitle?: string;
}

export async function POST(request: NextRequest) {
  try {
    const { 
      papers, 
      originalQuery, 
      apiConfig, 
      reportTitle 
    }: GenerateReportRequest = await request.json();

    if (!papers || papers.length === 0) {
      return NextResponse.json({ error: 'At least one paper is required' }, { status: 400 });
    }

    // Generate APA references
    const references = papers.map(paper => paperToApaReference(paper));
    const sortedReferences = sortReferencesApa(references);

    // Generate report using AI
    let report: ResearchReport;

    if (apiConfig.openRouterKey && apiConfig.openRouterModel) {
      report = await generateReportWithOpenRouter(
        papers, 
        originalQuery, 
        sortedReferences, 
        apiConfig.openRouterKey,
        apiConfig.openRouterModel,
        reportTitle
      );
    } else if (apiConfig.ollamaEndpoint && apiConfig.ollamaModel) {
      report = await generateReportWithOllama(
        papers, 
        originalQuery, 
        sortedReferences, 
        apiConfig.ollamaEndpoint,
        apiConfig.ollamaModel,
        reportTitle
      );
    } else {
      // Fallback: generate basic report
      report = generateBasicReport(papers, originalQuery, sortedReferences, reportTitle);
    }

    return NextResponse.json({ report });
  } catch (error) {
    console.error('Report generation error:', error);
    return NextResponse.json(
      { error: 'Failed to generate report' },
      { status: 500 }
    );
  }
}

async function generateReportWithOpenRouter(
  papers: AcademicPaper[],
  originalQuery: string,
  references: ApaReference[],
  apiKey: string,
  model: string,
  customTitle?: string
): Promise<ResearchReport> {
  // Prepare abstracts and key information
  const paperSummaries = papers.slice(0, 20).map((paper, index) => ({
    index: index + 1,
    title: paper.title,
    authors: paper.authors.map(a => a.name).join(', '),
    year: new Date(paper.publicationDate).getFullYear(),
    abstract: paper.abstract.slice(0, 800), // Limit abstract length
    citations: paper.citationCount,
    journal: paper.journal || paper.conference || 'Unknown',
    citation: generateInTextCitation(paper)
  }));

  const prompt = `You are an academic researcher writing a comprehensive literature synthesis based on research paper information. Generate a clean, professional research synthesis report about "${originalQuery}". 

IMPORTANT: Many papers may only have short snippets or limited abstract information due to API limitations. Focus your analysis on what information is available: titles, authors, journals, snippets, and any available abstract content.

CRITICAL FORMATTING REQUIREMENTS:
- Write in plain text format only - NO markdown symbols, NO asterisks, NO hashtags
- Do NOT use **, ###, ==, or any special formatting characters
- Write complete, substantive content for each section - NO empty sections allowed
- Use proper APA in-text citations like (Author, Year) throughout
- Write in formal academic prose suitable for PhD-level research

PAPERS TO ANALYZE (${paperSummaries.length} papers with available information):
${paperSummaries.map(paper => `
Paper ${paper.index}: ${paper.title}
Authors: ${paper.authors} (${paper.year})
Journal: ${paper.journal}
Available Content: ${paper.abstract}
Cite as: ${paper.citation}
`).join('\n')}

Write a comprehensive literature synthesis with these EXACT section headings (use these headings exactly, no formatting symbols):

Executive Summary
Analyze the collection of papers to identify key themes, main research directions, and significant contributions based on titles, available abstracts/snippets, and publication patterns. Synthesize the primary research focus areas and highlight critical insights that can be drawn from the available information.

Literature Overview  
Describe the scope and diversity of research represented in these papers based on titles, journals, and available content. Discuss publication venues, temporal distribution of studies, and the breadth of research approaches evident from paper titles and available abstracts/snippets.

Thematic Analysis
Identify and analyze 3-4 major themes that emerge from paper titles, available abstracts/snippets, and research focus areas. For each theme, synthesize insights across multiple papers, noting common research directions and approaches. Base analysis on available content while acknowledging data limitations.

Methodological Synthesis
Based on paper titles, available abstract content, and journal types, analyze the research methodologies and approaches evident across studies. Discuss the variety of research methods suggested by paper titles and any methodological information available in abstracts/snippets.

Research Gaps and Future Directions
Identify underexplored areas based on analysis of paper titles and available content. Highlight potential research directions suggested by the current body of work, noting areas where more investigation appears needed based on the available information.

Implications for Researchers
Synthesize key insights for academic researchers based on the themes and patterns identified in paper titles and available content. Provide recommendations for future research priorities based on the analysis of available information.

IMPORTANT: Base all analysis on the available information (titles, snippets, abstracts). Acknowledge when working with limited data but still provide meaningful synthesis and insights. Each section must contain substantial content (at least 200 words).`;

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
      temperature: 0.3, // Lower temperature for more consistent academic writing
      max_tokens: 4000
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

  return parseReportFromContent(content, references, papers.length, customTitle);
}

async function generateReportWithOllama(
  papers: AcademicPaper[],
  originalQuery: string,
  references: ApaReference[],
  endpoint: string,
  model: string,
  customTitle?: string
): Promise<ResearchReport> {
  const paperSummaries = papers.slice(0, 15).map((paper, index) => ({
    title: paper.title,
    authors: paper.authors.map(a => a.name).join(', '),
    abstract: paper.abstract.slice(0, 600)
  }));

  const prompt = `Write a comprehensive academic literature synthesis about "${originalQuery}" based on these research abstracts. 

CRITICAL: Write in plain text only - NO markdown formatting, NO asterisks, NO hashtags, NO special symbols.

Papers to analyze:
${paperSummaries.map((paper, i) => `${i + 1}. ${paper.title} by ${paper.authors}\nAbstract: ${paper.abstract}\n`).join('\n')}

Write with these exact section headings (no formatting symbols):

Executive Summary
[Write substantial analysis of key themes and findings]

Literature Overview  
[Describe scope and diversity of research]

Thematic Analysis
[Identify and analyze major themes across abstracts]

Methodological Synthesis
[Analyze research approaches evident in abstracts]

Research Gaps and Future Directions
[Identify gaps and suggest future research]

Implications for Researchers
[Synthesize insights and recommendations]

Each section must be substantial (200+ words). Base analysis on abstract content only. Use academic language.`;

  const response = await axios.post(
    `${endpoint}/api/generate`,
    {
      model: model,
      prompt,
      stream: false,
      options: {
        temperature: 0.3,
        num_predict: 2000
      }
    },
    {
      timeout: 60000
    }
  );

  const content = response.data.response;
  if (!content) throw new Error('No response from Ollama');

  return parseReportFromContent(content, references, papers.length, customTitle);
}

function generateBasicReport(
  papers: AcademicPaper[],
  originalQuery: string,
  references: ApaReference[],
  customTitle?: string
): ResearchReport {
  const title = customTitle || `Literature Synthesis: ${originalQuery}`;
  
  // Generate research-focused content
  const executiveSummary = `This literature synthesis examines a collection of ${papers.length} research papers focusing on ${originalQuery}. The review identifies key thematic patterns, methodological approaches, and research contributions in the field. Major findings reveal diverse perspectives and methodologies, with significant opportunities for future research identified across theoretical and practical domains.`;
  
  const literatureOverview = `The examined literature spans ${papers.length} publications across various venues and timeframes, representing a comprehensive view of current research in ${originalQuery}. Publications demonstrate diversity in methodological approaches, theoretical frameworks, and empirical findings, providing a rich foundation for thematic synthesis and critical analysis.`;
  
  const thematicAnalysis = `Analysis of the literature reveals several dominant themes: ${papers.slice(0, 5).map(paper => {
    const year = new Date(paper.publicationDate).getFullYear();
    return `research addressing ${paper.title.toLowerCase().substring(0, 50)}... as explored by ${paper.authors[0]?.name || 'researchers'} (${year})`;
  }).join('; ')}. These themes demonstrate the multifaceted nature of ${originalQuery} and highlight both convergent findings and areas of scholarly debate.`;
  
  const methodologicalSynthesis = `The reviewed studies employ diverse methodological approaches including quantitative, qualitative, and mixed-methods designs. This methodological diversity strengthens the overall evidence base while revealing opportunities for methodological innovation and cross-study comparison in future research.`;
  
  const researchGaps = `Despite substantial contributions from the ${papers.length} reviewed papers, several research gaps emerge: limited longitudinal studies, insufficient cross-cultural validation, and need for more robust theoretical frameworks. These gaps present opportunities for significant scholarly contributions to the field.`;
  
  const implications = `This synthesis provides valuable insights for researchers in ${originalQuery}, highlighting established knowledge while identifying frontier areas requiring investigation. The findings support evidence-based approaches while calling for continued methodological innovation and theoretical development in the field.`;

  return {
    id: generateId(),
    title,
    executiveSummary,
    literatureOverview,
    thematicAnalysis,
    methodologicalSynthesis,
    researchGaps,
    implications,
    references,
    generatedAt: new Date(),
    wordCount: (executiveSummary + literatureOverview + thematicAnalysis + methodologicalSynthesis + researchGaps + implications).split(' ').length,
    paperCount: papers.length
  };
}

function parseReportFromContent(
  content: string, 
  references: ApaReference[], 
  paperCount: number,
  customTitle?: string
): ResearchReport {
  // Clean up any markdown formatting that might have slipped through
  const cleanContent = content
    .replace(/\*\*/g, '') // Remove bold markdown
    .replace(/###\s*/g, '') // Remove header markdown
    .replace(/==+/g, '') // Remove emphasis markers
    .replace(/\n\s*\n\s*\n/g, '\n\n'); // Clean up excessive line breaks

  const sections = {
    title: '',
    executiveSummary: '',
    literatureOverview: '',
    thematicAnalysis: '',
    methodologicalSynthesis: '',
    researchGaps: '',
    implications: ''
  };

  // Extract title
  const titleMatch = cleanContent.match(/(?:^|\n)(?:Title:?\s*)?(.+)(?=\n|$)/i);
  sections.title = titleMatch ? titleMatch[1].trim() : customTitle || `Literature Synthesis: ${customTitle || 'Research Analysis'}`;

  // Extract sections using the exact section headings we specified
  const sectionPatterns = {
    executiveSummary: /Executive Summary\s*\n([\s\S]*?)(?=\n(?:Literature Overview|Thematic Analysis)|$)/i,
    literatureOverview: /Literature Overview\s*\n([\s\S]*?)(?=\n(?:Thematic Analysis|Methodological Synthesis)|$)/i,
    thematicAnalysis: /Thematic Analysis\s*\n([\s\S]*?)(?=\n(?:Methodological Synthesis|Research Gaps)|$)/i,
    methodologicalSynthesis: /Methodological Synthesis\s*\n([\s\S]*?)(?=\n(?:Research Gaps|Implications)|$)/i,
    researchGaps: /Research Gaps and Future Directions\s*\n([\s\S]*?)(?=\n(?:Implications for Researchers)|$)/i,
    implications: /Implications for Researchers\s*\n([\s\S]*?)(?=\n\n|$)/i
  };

  Object.entries(sectionPatterns).forEach(([key, pattern]) => {
    const match = cleanContent.match(pattern);
    if (match && match[1]) {
      sections[key as keyof typeof sections] = match[1].trim()
        .replace(/\n+/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();
    }
  });

  // Fallback content generation if sections are empty or too short
  const minLength = 150;
  
    if (!sections.executiveSummary || sections.executiveSummary.length < minLength) {
    sections.executiveSummary = `This literature synthesis examines a collection of ${paperCount} research papers addressing research questions related to the query. The analysis reveals diverse methodological approaches and theoretical frameworks across the selected studies. Key findings indicate significant contributions to the field, with several research gaps identified that present opportunities for future investigation. The synthesized literature provides valuable insights for researchers and practitioners working in this domain.`;
  }

  if (!sections.literatureOverview || sections.literatureOverview.length < minLength) {
    sections.literatureOverview = `The examined literature comprises ${paperCount} research publications spanning multiple academic venues and research institutions. These studies represent a comprehensive view of current scholarship in the field, demonstrating methodological diversity and theoretical breadth. The temporal distribution of publications indicates sustained research interest, while the variety of publication venues suggests interdisciplinary relevance and broad academic engagement with the research topics.`;
  }

  if (!sections.thematicAnalysis || sections.thematicAnalysis.length < minLength) {
    sections.thematicAnalysis = `Analysis of the research abstracts reveals several recurring themes that characterize current scholarship in this field. These thematic patterns demonstrate both convergent findings across studies and areas of ongoing scholarly debate. The diversity of approaches to core concepts indicates a maturing field with established theoretical foundations while maintaining space for methodological innovation and conceptual development.`;
  }

  if (!sections.methodologicalSynthesis || sections.methodologicalSynthesis.length < minLength) {
    sections.methodologicalSynthesis = `The methodological approaches evident in these studies demonstrate considerable diversity in research design and analytical techniques. Both quantitative and qualitative methodologies are represented, with several studies employing mixed-methods approaches. This methodological variety strengthens the overall evidence base while highlighting opportunities for methodological innovation and cross-study comparison in future research endeavors.`;
  }

  if (!sections.researchGaps || sections.researchGaps.length < minLength) {
    sections.researchGaps = `Despite the substantial contributions of the examined studies, several research gaps emerge from this synthesis. These include opportunities for longitudinal investigations, cross-cultural validation of findings, and development of more robust theoretical frameworks. Additionally, there appears to be potential for methodological advancement and deeper exploration of the practical applications of research findings in real-world contexts.`;
  }

  if (!sections.implications || sections.implications.length < minLength) {
    sections.implications = `The findings of this literature synthesis have significant implications for researchers in this field. The analysis highlights established areas of knowledge while identifying frontier research opportunities that could yield substantial scholarly contributions. Future research should consider building upon the methodological foundations established by these studies while exploring novel theoretical perspectives and practical applications.`;
  }

  const fullText = Object.values(sections).join(' ');
  const wordCount = fullText.split(' ').filter(w => w.length > 0).length;

  return {
    id: generateId(),
    title: sections.title,
    executiveSummary: sections.executiveSummary,
    literatureOverview: sections.literatureOverview,
    thematicAnalysis: sections.thematicAnalysis,
    methodologicalSynthesis: sections.methodologicalSynthesis,
    researchGaps: sections.researchGaps,
    implications: sections.implications,
    references,
    generatedAt: new Date(),
    wordCount,
    paperCount
  };
}