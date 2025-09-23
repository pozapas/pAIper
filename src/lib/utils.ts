import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Utility function to merge Tailwind CSS classes
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Delay function for rate limiting and UX
 */
export const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * Validate email format
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Validate URL format
 */
export function isValidUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

// Counter for more predictable IDs during SSR
let idCounter = 0;

/**
 * Generate unique ID (SSR-safe)
 */
export function generateId(): string {
  // Use counter for more predictable IDs during SSR/hydration
  idCounter++;
  const timestamp = typeof window !== 'undefined' ? Date.now() : 1000000000000;
  const random = typeof window !== 'undefined' ? Math.random() : 0.5;
  
  return `${timestamp.toString(36)}-${random.toString(36).substr(2)}-${idCounter}`;
}

/**
 * Format date to readable string (client-safe)
 */
export function formatDate(date: Date | string): string {
  try {
    const d = typeof date === 'string' ? new Date(date) : date;
    
    // Check if date is valid
    if (isNaN(d.getTime())) {
      return 'Invalid Date';
    }
    
    // Use a consistent format that works on both server and client
    return d.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      timeZone: 'UTC' // Ensure consistent timezone
    });
  } catch (error) {
    return 'Invalid Date';
  }
}

/**
 * Truncate text to specified length
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength).trim() + '...';
}

/**
 * Clean and normalize text for search
 */
export function normalizeText(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

/**
 * Extract keywords from text using simple NLP
 */
export function extractKeywords(text: string, maxKeywords: number = 10): string[] {
  const stopWords = new Set([
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
    'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
    'to', 'was', 'were', 'will', 'with', 'the', 'this', 'but', 'they',
    'have', 'had', 'what', 'said', 'each', 'which', 'do', 'their', 'time',
    'if', 'up', 'out', 'many', 'then', 'them', 'can', 'only', 'other',
    'how', 'its', 'our', 'after', 'first', 'well', 'way', 'even', 'new',
    'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us'
  ]);

  const words = normalizeText(text)
    .split(/\s+/)
    .filter(word => word.length > 3 && !stopWords.has(word))
    .filter(word => !/^\d+$/.test(word));

  const wordCount = new Map<string, number>();
  words.forEach(word => {
    wordCount.set(word, (wordCount.get(word) || 0) + 1);
  });

  return Array.from(wordCount.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, maxKeywords)
    .map(([word]) => word);
}

/**
 * Calculate relevance score between query and paper
 */
export function calculateRelevanceScore(query: string, title: string, abstract: string): number {
  const queryKeywords = extractKeywords(query);
  const paperText = normalizeText(`${title} ${abstract}`);
  const titleText = normalizeText(title);
  
  let titleMatches = 0;
  let abstractMatches = 0;
  
  queryKeywords.forEach(keyword => {
    if (titleText.includes(keyword)) {
      titleMatches++;
    } else if (paperText.includes(keyword)) {
      abstractMatches++;
    }
  });
  
  if (queryKeywords.length === 0) return 0;
  
  // Calculate percentage: title matches are worth more, but cap at 100%
  const titleScore = (titleMatches / queryKeywords.length) * 60; // Title matches worth up to 60%
  const abstractScore = (abstractMatches / queryKeywords.length) * 40; // Abstract matches worth up to 40%
  
  return Math.min(100, Math.round(titleScore + abstractScore));
}

/**
 * Validate API key format (basic validation)
 */
export function validateApiKey(key: string, provider: string): boolean {
  if (!key || key.trim().length < 10) return false;
  
  switch (provider) {
    case 'openrouter':
      return key.startsWith('sk-or-') || key.length >= 20;
    case 'google-scholar':
      return key.length >= 20;
    case 'scopus':
      return key.length >= 20;
    default:
      return key.length >= 10;
  }
}

/**
 * Sanitize filename for download
 */
export function sanitizeFilename(filename: string): string {
  return filename
    .replace(/[^a-z0-9]/gi, '_')
    .replace(/_+/g, '_')
    .replace(/^_|_$/g, '')
    .toLowerCase();
}

/**
 * Format number with locale-specific formatting (SSR-safe)
 */
export function formatNumber(num: number): string {
  try {
    // Use a consistent locale for SSR/hydration
    return num.toLocaleString('en-US');
  } catch (error) {
    return num.toString();
  }
}

/**
 * Format file size in human readable format
 */
export function formatFileSize(bytes: number): string {
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  if (bytes === 0) return '0 Bytes';
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
}