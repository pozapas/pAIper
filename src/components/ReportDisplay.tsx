'use client';

import React, { useState } from 'react';
import { 
  FileText, 
  Download, 
  Share, 
  Eye, 
  BookOpen, 
  Calendar,
  Hash,
  Users,
  ChevronDown,
  ChevronUp,
  Copy,
  Check
} from 'lucide-react';
import { ResearchReport } from '@/types';
import { formatDate, formatNumber } from '@/lib/utils';
import { exportReportToPDF, exportReportToText } from '@/lib/export';
import { cn } from '@/lib/utils';

interface ReportDisplayProps {
  report: ResearchReport;
  onBack: () => void;
}

export default function ReportDisplay({ report, onBack }: ReportDisplayProps) {
  const [activeSection, setActiveSection] = useState<string>('executiveSummary');
  const [showReferences, setShowReferences] = useState(false);
  const [copiedReference, setCopiedReference] = useState<string | null>(null);

  const sections = [
    { id: 'executiveSummary', title: 'Executive Summary', content: report.executiveSummary, icon: Eye },
    { id: 'literatureOverview', title: 'Literature Overview', content: report.literatureOverview, icon: BookOpen },
    { id: 'thematicAnalysis', title: 'Thematic Analysis', content: report.thematicAnalysis, icon: Hash },
    { id: 'methodologicalSynthesis', title: 'Methodological Synthesis', content: report.methodologicalSynthesis, icon: Users },
    { id: 'researchGaps', title: 'Research Gaps & Future Directions', content: report.researchGaps, icon: ChevronUp },
    { id: 'implications', title: 'Implications for Researchers', content: report.implications, icon: Check }
  ];

  const handleExportPDF = () => {
    exportReportToPDF(report);
  };

  const handleExportText = () => {
    exportReportToText(report);
  };

  const copyReference = async (citation: string, refId: string) => {
    await navigator.clipboard.writeText(citation);
    setCopiedReference(refId);
    setTimeout(() => setCopiedReference(null), 2000);
  };

  const scrollToSection = (sectionId: string) => {
    setActiveSection(sectionId);
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <div className="max-w-5xl mx-auto p-6">
      {/* Header */}
      <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-gray-900 mb-3 leading-tight">
              {report.title}
            </h1>
            
            <div className="flex items-center gap-6 text-sm text-gray-600">
              <div className="flex items-center gap-1">
                <Calendar className="w-4 h-4" />
                <span>Generated {formatDate(report.generatedAt)}</span>
              </div>
              <div className="flex items-center gap-1">
                <FileText className="w-4 h-4" />
                <span>{formatNumber(report.wordCount)} words</span>
              </div>
              <div className="flex items-center gap-1">
                <BookOpen className="w-4 h-4" />
                <span>{report.paperCount} papers analyzed</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3 ml-6">
            <button
              onClick={onBack}
              className="px-4 py-2 text-gray-600 hover:text-gray-700 font-medium"
            >
              ← Back to Papers
            </button>
            
            <div className="flex items-center gap-2">
              <button
                onClick={handleExportPDF}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 font-medium flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                Export PDF
              </button>
              
              <button
                onClick={handleExportText}
                className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 font-medium flex items-center gap-2"
              >
                <FileText className="w-4 h-4" />
                Export Text
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Table of Contents */}
        <div className="lg:col-span-1">
          <div className="bg-white border border-gray-200 rounded-lg p-4 sticky top-6">
            <h3 className="font-semibold text-gray-900 mb-3">Table of Contents</h3>
            <nav className="space-y-1">
              {sections.map((section) => {
                const Icon = section.icon;
                return (
                  <button
                    key={section.id}
                    onClick={() => scrollToSection(section.id)}
                    className={cn(
                      "w-full flex items-center gap-2 px-3 py-2 text-left rounded-md transition-colors",
                      activeSection === section.id
                        ? "bg-blue-100 text-blue-900"
                        : "text-gray-600 hover:bg-gray-50"
                    )}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="text-sm">{section.title}</span>
                  </button>
                );
              })}
              
              <button
                onClick={() => scrollToSection('references')}
                className={cn(
                  "w-full flex items-center gap-2 px-3 py-2 text-left rounded-md transition-colors",
                  activeSection === 'references'
                    ? "bg-blue-100 text-blue-900"
                    : "text-gray-600 hover:bg-gray-50"
                )}
              >
                <Share className="w-4 h-4" />
                <span className="text-sm">References</span>
                <span className="ml-auto text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
                  {report.references.length}
                </span>
              </button>
            </nav>
          </div>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-3">
          <div className="bg-white border border-gray-200 rounded-lg">
            {/* Report Sections */}
            <div className="p-8">
              {sections.map((section) => (
                <section key={section.id} id={section.id} className="mb-8 last:mb-0">
                  <div className="flex items-center gap-2 mb-4">
                    <section.icon className="w-5 h-5 text-blue-600" />
                    <h2 className="text-2xl font-bold text-gray-900">{section.title}</h2>
                  </div>
                  
                  <div className="prose prose-lg max-w-none">
                    <div className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                      {section.content}
                    </div>
                  </div>
                </section>
              ))}

              {/* References Section */}
              <section id="references" className="border-t pt-8">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-2">
                    <Share className="w-5 h-5 text-blue-600" />
                    <h2 className="text-2xl font-bold text-gray-900">References</h2>
                    <span className="bg-gray-100 text-gray-600 px-2 py-1 rounded-full text-sm">
                      {report.references.length} papers
                    </span>
                  </div>
                  
                  <button
                    onClick={() => setShowReferences(!showReferences)}
                    className="flex items-center gap-1 text-blue-600 hover:text-blue-700 font-medium"
                  >
                    {showReferences ? (
                      <>Hide References <ChevronUp className="w-4 h-4" /></>
                    ) : (
                      <>Show All References <ChevronDown className="w-4 h-4" /></>
                    )}
                  </button>
                </div>

                {showReferences && (
                  <div className="space-y-3">
                    {report.references.map((reference, index) => (
                      <div
                        key={reference.id}
                        className="group relative pl-8 pr-12 py-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors border border-gray-200"
                      >
                        <div className="absolute left-3 top-4 w-5 h-5 bg-blue-100 text-blue-600 text-xs rounded-full flex items-center justify-center font-semibold">
                          {index + 1}
                        </div>
                        
                        <div className="text-gray-700 leading-relaxed text-sm break-words overflow-hidden">
                          {reference.citation}
                        </div>

                        <button
                          onClick={() => copyReference(reference.citation, reference.id)}
                          className="absolute right-3 top-4 p-1.5 opacity-0 group-hover:opacity-100 text-gray-400 hover:text-gray-600 transition-opacity rounded hover:bg-gray-200"
                          title="Copy citation"
                        >
                          {copiedReference === reference.id ? (
                            <Check className="w-4 h-4 text-green-600" />
                          ) : (
                            <Copy className="w-4 h-4" />
                          )}
                        </button>
                      </div>
                    ))}
                  </div>
                )}

                {!showReferences && report.references.length > 0 && (
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="text-sm text-gray-600 mb-2">Sample references:</div>
                    <div className="space-y-2">
                      {report.references.slice(0, 3).map((reference, index) => (
                        <div key={reference.id} className="text-sm text-gray-700 leading-relaxed">
                          <span className="font-medium text-gray-600">[{index + 1}]</span> {reference.citation}
                        </div>
                      ))}
                      {report.references.length > 3 && (
                        <div className="text-sm text-gray-500 italic">
                          ...and {report.references.length - 3} more references
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </section>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="mt-8 p-6 bg-gray-50 rounded-lg">
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-600">
            <p className="mb-1">
              This report was automatically generated by pAIper using AI analysis of {report.paperCount} academic papers.
            </p>
            <p>
              Generated on {formatDate(report.generatedAt)} • {formatNumber(report.wordCount)} words
            </p>
          </div>
          
          <div className="text-right text-sm text-gray-500">
            <p className="font-medium">pAIper Research Tool</p>
            <p>AI-Powered Academic Research</p>
          </div>
        </div>
      </div>
    </div>
  );
}