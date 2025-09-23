import Papa from 'papaparse';
import { saveAs } from 'file-saver';
import jsPDF from 'jspdf';
import { AcademicPaper, ResearchReport, ExportOptions } from '@/types';
import { sanitizeFilename, formatDate } from './utils';

/**
 * Export papers to CSV format
 */
export function exportPapersToCSV(papers: AcademicPaper[], options: ExportOptions): void {
  const data = papers.map(paper => {
    const baseData = {
      Title: paper.title,
      Authors: paper.authors.map(a => a.name).join('; '),
      'Publication Date': formatDate(paper.publicationDate),
      Journal: paper.journal || paper.conference || '',
      Publisher: paper.publisher || '',
      DOI: paper.doi || '',
      URL: paper.url || '',
      'Citation Count': paper.citationCount,
      Source: paper.source,
      'Relevance Score': paper.relevanceScore || 0
    };

    if (options.includeAbstracts) {
      (baseData as any).Abstract = paper.abstract;
    }

    if (options.includeKeywords) {
      (baseData as any).Keywords = paper.keywords?.join('; ') || '';
    }

    return baseData;
  });

  // Sort data based on options
  const sortedData = [...data].sort((a, b) => {
    const key = options.sortBy as keyof typeof a;
    const aVal = a[key] || '';
    const bVal = b[key] || '';
    
    if (typeof aVal === 'string' && typeof bVal === 'string') {
      return aVal.localeCompare(bVal);
    }
    
    if (typeof aVal === 'number' && typeof bVal === 'number') {
      return bVal - aVal; // Descending for numeric values
    }
    
    return 0;
  });

  const csv = Papa.unparse(sortedData);
  const filename = `research_papers_${new Date().toISOString().split('T')[0]}.csv`;
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  saveAs(blob, filename);
}

/**
 * Export papers to JSON format
 */
export function exportPapersToJSON(papers: AcademicPaper[]): void {
  const filename = `papers_export_${new Date().toISOString().split('T')[0]}.json`;
  const json = JSON.stringify(papers, null, 2);
  const blob = new Blob([json], { type: 'application/json' });
  saveAs(blob, filename);
}

/**
 * Export papers to BibTeX format
 */
export function exportPapersToBibTeX(papers: AcademicPaper[]): void {
  const bibtexEntries = papers.map(paper => paperToBibTeX(paper)).join('\n\n');
  
  const filename = `research_papers_${new Date().toISOString().split('T')[0]}.bib`;
  const blob = new Blob([bibtexEntries], { type: 'text/plain;charset=utf-8;' });
  saveAs(blob, filename);
}

/**
 * Convert academic paper to BibTeX entry
 */
function paperToBibTeX(paper: AcademicPaper): string {
  const year = new Date(paper.publicationDate).getFullYear();
  const key = sanitizeFilename(`${paper.authors[0]?.name.split(' ').pop() || 'unknown'}${year}`);
  
  const authors = paper.authors.map(a => a.name).join(' and ');
  
  let entry = '';
  
  if (paper.journal) {
    entry = `@article{${key},
  title={${paper.title}},
  author={${authors}},
  journal={${paper.journal}},
  year={${year}}`;
  } else if (paper.conference) {
    entry = `@inproceedings{${key},
  title={${paper.title}},
  author={${authors}},
  booktitle={${paper.conference}},
  year={${year}}`;
  } else {
    entry = `@misc{${key},
  title={${paper.title}},
  author={${authors}},
  year={${year}}`;
  }

  if (paper.doi) {
    entry += `,\n  doi={${paper.doi}}`;
  }
  
  if (paper.url) {
    entry += `,\n  url={${paper.url}}`;
  }

  if (paper.publisher) {
    entry += `,\n  publisher={${paper.publisher}}`;
  }

  entry += '\n}';
  
  return entry;
}

/**
 * Export research report to PDF
 */
export function exportReportToPDF(report: ResearchReport): void {
  const pdf = new jsPDF();
  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();
  const margin = 20;
  const lineHeight = 7;
  let yPosition = margin;

  // Title
  pdf.setFontSize(16);
  pdf.setFont('helvetica', 'bold');
  pdf.text(report.title, margin, yPosition);
  yPosition += lineHeight * 2;

  // Meta information
  pdf.setFontSize(10);
  pdf.setFont('helvetica', 'normal');
  pdf.text(`Generated: ${formatDate(report.generatedAt)}`, margin, yPosition);
  yPosition += lineHeight;
  pdf.text(`Word Count: ${report.wordCount} | Papers Analyzed: ${report.paperCount}`, margin, yPosition);
  yPosition += lineHeight * 2;

  // Sections
  const sections = [
    { title: 'Executive Summary', content: report.executiveSummary },
    { title: 'Literature Overview', content: report.literatureOverview },
    { title: 'Thematic Analysis', content: report.thematicAnalysis },
    { title: 'Methodological Synthesis', content: report.methodologicalSynthesis },
    { title: 'Research Gaps & Future Directions', content: report.researchGaps },
    { title: 'Implications for Researchers', content: report.implications }
  ];

  pdf.setFontSize(12);

  sections.forEach(section => {
    // Check if we need a new page
    if (yPosition > pageHeight - margin - 50) {
      pdf.addPage();
      yPosition = margin;
    }

    // Section title
    pdf.setFont('helvetica', 'bold');
    pdf.text(section.title, margin, yPosition);
    yPosition += lineHeight * 1.5;

    // Section content
    pdf.setFont('helvetica', 'normal');
    const splitText = pdf.splitTextToSize(section.content, pageWidth - margin * 2);
    
    splitText.forEach((line: string) => {
      if (yPosition > pageHeight - margin) {
        pdf.addPage();
        yPosition = margin;
      }
      pdf.text(line, margin, yPosition);
      yPosition += lineHeight;
    });
    
    yPosition += lineHeight;
  });

  // References
  if (report.references.length > 0) {
    if (yPosition > pageHeight - margin - 50) {
      pdf.addPage();
      yPosition = margin;
    }

    pdf.setFont('helvetica', 'bold');
    pdf.text('References', margin, yPosition);
    yPosition += lineHeight * 1.5;

    pdf.setFont('helvetica', 'normal');
    report.references.forEach(ref => {
      if (yPosition > pageHeight - margin) {
        pdf.addPage();
        yPosition = margin;
      }

      const splitRef = pdf.splitTextToSize(ref.citation, pageWidth - margin * 2);
      splitRef.forEach((line: string) => {
        pdf.text(line, margin, yPosition);
        yPosition += lineHeight;
      });
      yPosition += lineHeight * 0.5;
    });
  }

  const filename = `research_report_${sanitizeFilename(report.title)}_${new Date().toISOString().split('T')[0]}.pdf`;
  pdf.save(filename);
}

/**
 * Export research report to plain text
 */
export function exportReportToText(report: ResearchReport): void {
  let content = `${report.title}\n`;
  content += `${'='.repeat(report.title.length)}\n\n`;
  content += `Generated: ${formatDate(report.generatedAt)}\n`;
  content += `Word Count: ${report.wordCount} | Papers Analyzed: ${report.paperCount}\n\n`;

  content += `Executive Summary\n${'='.repeat(17)}\n${report.executiveSummary}\n\n`;
  content += `Literature Overview\n${'='.repeat(19)}\n${report.literatureOverview}\n\n`;
  content += `Thematic Analysis\n${'='.repeat(17)}\n${report.thematicAnalysis}\n\n`;
  content += `Methodological Synthesis\n${'='.repeat(24)}\n${report.methodologicalSynthesis}\n\n`;
  content += `Research Gaps & Future Directions\n${'='.repeat(33)}\n${report.researchGaps}\n\n`;
  content += `Implications for Researchers\n${'='.repeat(28)}\n${report.implications}\n\n`;

  if (report.references.length > 0) {
    content += `References\n----------\n`;
    report.references.forEach(ref => {
      content += `${ref.citation}\n\n`;
    });
  }

  const filename = `research_report_${sanitizeFilename(report.title)}_${new Date().toISOString().split('T')[0]}.txt`;
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8;' });
  saveAs(blob, filename);
}

/**
 * Export complete research session data
 */
export function exportCompleteSession(
  papers: AcademicPaper[],
  report: ResearchReport | null,
  originalQuery: string
): void {
  const data = {
    exportedAt: new Date().toISOString(),
    originalQuery,
    totalPapers: papers.length,
    papers,
    report,
    metadata: {
      sources: [...new Set(papers.map(p => p.source))],
      dateRange: {
        earliest: papers.length > 0 ? new Date(Math.min(...papers.map(p => new Date(p.publicationDate).getTime()))) : null,
        latest: papers.length > 0 ? new Date(Math.max(...papers.map(p => new Date(p.publicationDate).getTime()))) : null
      },
      topAuthors: getTopAuthors(papers, 10),
      topJournals: getTopJournals(papers, 10)
    }
  };

  const json = JSON.stringify(data, null, 2);
  const filename = `complete_research_session_${new Date().toISOString().split('T')[0]}.json`;
  const blob = new Blob([json], { type: 'application/json' });
  saveAs(blob, filename);
}

/**
 * Get top authors by paper count
 */
function getTopAuthors(papers: AcademicPaper[], limit: number): { name: string; count: number }[] {
  const authorCounts = new Map<string, number>();
  
  papers.forEach(paper => {
    paper.authors.forEach(author => {
      const count = authorCounts.get(author.name) || 0;
      authorCounts.set(author.name, count + 1);
    });
  });

  return Array.from(authorCounts.entries())
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, limit);
}

/**
 * Get top journals by paper count
 */
function getTopJournals(papers: AcademicPaper[], limit: number): { name: string; count: number }[] {
  const journalCounts = new Map<string, number>();
  
  papers.forEach(paper => {
    const venue = paper.journal || paper.conference;
    if (venue) {
      const count = journalCounts.get(venue) || 0;
      journalCounts.set(venue, count + 1);
    }
  });

  return Array.from(journalCounts.entries())
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, limit);
}