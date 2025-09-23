import { AcademicPaper, ApaReference } from '@/types';

/**
 * Convert academic paper to APA reference
 */
export function paperToApaReference(paper: AcademicPaper): ApaReference {
  const year = new Date(paper.publicationDate).getFullYear().toString();
  
  // Format authors (Last, F. M.)
  const authorsString = formatAuthorsApa(paper.authors.map(a => a.name));
  
  // Clean title (remove extra spaces and formatting)
  const cleanTitle = paper.title.replace(/\s+/g, ' ').trim();
  
  // Build citation based on publication type
  let citation = '';
  
  if (paper.journal) {
    // Journal article
    citation = `${authorsString} (${year}). ${cleanTitle}. *${paper.journal}*`;
    if (paper.doi) {
      citation += `. https://doi.org/${paper.doi}`;
    } else if (paper.url) {
      citation += `. ${paper.url}`;
    }
  } else if (paper.conference) {
    // Conference paper
    citation = `${authorsString} (${year}). ${cleanTitle}. In *${paper.conference}*`;
    if (paper.doi) {
      citation += `. https://doi.org/${paper.doi}`;
    } else if (paper.url) {
      citation += `. ${paper.url}`;
    }
  } else {
    // Generic publication
    citation = `${authorsString} (${year}). ${cleanTitle}`;
    if (paper.publisher) {
      citation += `. ${paper.publisher}`;
    }
    if (paper.doi) {
      citation += `. https://doi.org/${paper.doi}`;
    } else if (paper.url) {
      citation += `. ${paper.url}`;
    }
  }
  
  return {
    id: paper.id,
    authors: authorsString,
    year,
    title: cleanTitle,
    journal: paper.journal,
    doi: paper.doi,
    url: paper.url,
    citation: citation
  };
}

/**
 * Format authors in APA style
 */
export function formatAuthorsApa(authors: string[]): string {
  if (authors.length === 0) return '';
  
  const formattedAuthors = authors.map(author => formatSingleAuthorApa(author));
  
  if (formattedAuthors.length === 1) {
    return formattedAuthors[0];
  } else if (formattedAuthors.length === 2) {
    return `${formattedAuthors[0]}, & ${formattedAuthors[1]}`;
  } else if (formattedAuthors.length <= 20) {
    const allButLast = formattedAuthors.slice(0, -1).join(', ');
    return `${allButLast}, & ${formattedAuthors[formattedAuthors.length - 1]}`;
  } else {
    // For more than 20 authors, include first 19, then ellipses, then last
    const first19 = formattedAuthors.slice(0, 19).join(', ');
    const last = formattedAuthors[formattedAuthors.length - 1];
    return `${first19}, ... ${last}`;
  }
}

/**
 * Format single author name in APA style (Last, F. M.)
 */
export function formatSingleAuthorApa(fullName: string): string {
  const parts = fullName.trim().split(/\s+/);
  
  if (parts.length === 1) {
    return parts[0];
  }
  
  const lastName = parts[parts.length - 1];
  const firstNames = parts.slice(0, -1);
  
  // Get initials from first names
  const initials = firstNames
    .map(name => name.charAt(0).toUpperCase())
    .join('. ') + (firstNames.length > 0 ? '.' : '');
  
  return `${lastName}, ${initials}`;
}

/**
 * Generate in-text citation in APA style
 */
export function generateInTextCitation(paper: AcademicPaper, page?: string): string {
  const year = new Date(paper.publicationDate).getFullYear();
  
  if (paper.authors.length === 0) {
    return `(${year}${page ? `, p. ${page}` : ''})`;
  }
  
  if (paper.authors.length === 1) {
    const lastName = getLastName(paper.authors[0].name);
    return `(${lastName}, ${year}${page ? `, p. ${page}` : ''})`;
  }
  
  if (paper.authors.length === 2) {
    const lastName1 = getLastName(paper.authors[0].name);
    const lastName2 = getLastName(paper.authors[1].name);
    return `(${lastName1} & ${lastName2}, ${year}${page ? `, p. ${page}` : ''})`;
  }
  
  if (paper.authors.length >= 3) {
    const firstAuthor = getLastName(paper.authors[0].name);
    return `(${firstAuthor} et al., ${year}${page ? `, p. ${page}` : ''})`;
  }
  
  return `(${year}${page ? `, p. ${page}` : ''})`;
}

/**
 * Extract last name from full name
 */
function getLastName(fullName: string): string {
  const parts = fullName.trim().split(/\s+/);
  return parts[parts.length - 1];
}

/**
 * Sort references alphabetically by author last name (APA style)
 */
export function sortReferencesApa(references: ApaReference[]): ApaReference[] {
  return [...references].sort((a, b) => {
    // Extract first author's last name for comparison
    const aFirstAuthor = a.authors.split(',')[0].trim();
    const bFirstAuthor = b.authors.split(',')[0].trim();
    
    if (aFirstAuthor < bFirstAuthor) return -1;
    if (aFirstAuthor > bFirstAuthor) return 1;
    
    // If same first author, sort by year
    if (a.year < b.year) return -1;
    if (a.year > b.year) return 1;
    
    // If same author and year, sort by title
    return a.title.localeCompare(b.title);
  });
}

/**
 * Generate full APA reference list
 */
export function generateReferenceList(references: ApaReference[]): string {
  const sortedRefs = sortReferencesApa(references);
  return sortedRefs.map(ref => ref.citation).join('\n\n');
}

/**
 * Validate APA citation format
 */
export function validateApaCitation(citation: string): boolean {
  // Basic validation - should contain author, year, and title
  const hasYear = /\(\d{4}\)/.test(citation);
  const hasTitle = citation.includes('.');
  const hasAuthor = citation.length > 10 && !citation.startsWith('(');
  
  return hasYear && hasTitle && hasAuthor;
}

/**
 * Clean and standardize DOI format
 */
export function formatDoi(doi: string): string {
  if (!doi) return '';
  
  // Remove common prefixes
  doi = doi.replace(/^(doi:|DOI:|https?:\/\/(dx\.)?doi\.org\/)/i, '');
  
  // Ensure it starts with "10."
  if (!doi.startsWith('10.')) {
    return doi; // Return as-is if not a standard DOI format
  }
  
  return doi;
}

/**
 * Generate hanging indent for reference (for display purposes)
 */
export function formatReferenceWithHangingIndent(citation: string): string {
  const lines = citation.split('\n');
  if (lines.length <= 1) return citation;
  
  return lines[0] + '\n' + lines.slice(1).map(line => '    ' + line).join('\n');
}