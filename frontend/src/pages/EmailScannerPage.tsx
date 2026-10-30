import React, { useState, useRef } from 'react';
import { 
  Mail, 
  Search, 
  AlertCircle, 
  Sparkles,
  Lock,
  UploadCloud,
  FileCheck,
  ExternalLink,
  Paperclip,
  ShieldCheck,
  ShieldAlert,
  Copy,
  Check
} from 'lucide-react';
import { scanEmail, scanEmailFile } from '../services/api';
import { EmailScanResult } from '../types';
import { ExplanationCard } from '../components/ExplanationCard';
import { FeatureImportanceChart } from '../components/FeatureImportanceChart';
import { DisclaimerBanner } from '../components/DisclaimerBanner';
import { downloadForensicReport } from '../utils/forensicReport';

export const EmailScannerPage: React.FC = () => {
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [loading, setLoading] = useState(false);
  const [fileLoading, setFileLoading] = useState(false);
  const [result, setResult] = useState<EmailScanResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadedFileName, setUploadedFileName] = useState<string | null>(null);
  const [copiedUrl, setCopiedUrl] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const emailPresets = [
    {
      title: 'Urgent Account Suspension (Phishing)',
      subject: 'URGENT: Your PayPal Account Has Been Suspended - Action Required Immediately',
      body: 'Dear Valued Customer,\nWe detected unauthorized login attempts from an unknown IP address. Your account has been temporarily restricted. You must verify your credentials and confirm your identity within 24 hours to prevent permanent account termination.\nClick the link below immediately to update your billing information and restore access:\nhttp://paypal.com.account-verification.login-service.top/auth/signin.html\nFailure to comply will result in account cancellation.\nPayPal Fraud Prevention Team',
    },
    {
      title: 'Executive Wire Transfer Fraud (BEC)',
      subject: 'Urgent Wire Transfer Request - Confidential Instruction',
      body: 'Good morning,\nI am currently in an executive committee meeting and unable to take phone calls. We have an urgent confidential acquisition invoice that must be settled via international wire transfer before end of business today. Please reply immediately with the current balance of our corporate account so I can forward beneficiary routing details.\nTreat this matter with strict discretion.\nChief Executive Officer',
    },
    {
      title: 'Sprint Planning Sync (Legitimate)',
      subject: 'Sprint Planning Sync - Thursday at 10:00 AM',
      body: 'Hi team,\nPlease find attached the agenda for our upcoming sprint planning session. We will review our Q3 backlog, assign story points to incoming issues, and discuss frontend performance improvements. Let me know if you need to add any discussion points before Thursday morning.\nBest regards,\nSarah',
    },
    {
      title: 'GitHub PR Notification (Legitimate)',
      subject: 'GitHub: [PhishGuard/core] Pull Request #14 merged',
      body: 'Your pull request #14 "Refactor URL feature extraction pipeline" has been reviewed, approved, and merged into the main branch by reviewer alex-dev. All 42 automated unit tests passed on CI. You can safely delete your feature branch.',
    },
  ];

  const handleScan = async (presetSubject?: string, presetBody?: string) => {
    const s = (presetSubject !== undefined ? presetSubject : subject).trim();
    const b = (presetBody !== undefined ? presetBody : body).trim();

    if (!b) {
      setError('Please provide the email body text to analyze.');
      return;
    }
    if (b.length < 5) {
      setError('Email body must be at least 5 characters.');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await scanEmail(s, b);
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'An error occurred during email classification.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (file: File) => {
    if (!file) return;

    if (!file.name.match(/\.(eml|msg|txt)$/i)) {
      setError('Please upload a valid .eml, .msg, or email text file.');
      return;
    }

    try {
      setFileLoading(true);
      setError(null);
      setUploadedFileName(file.name);

      const data = await scanEmailFile(file);
      setResult(data);

      // Auto-fill inputs with extracted content
      if (data.extracted_subject) setSubject(data.extracted_subject);
      if (data.extracted_body) setBody(data.extracted_body);
    } catch (err: any) {
      setError(err.message || 'Failed to parse and analyze the .eml file.');
    } finally {
      setFileLoading(false);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedUrl(text);
    setTimeout(() => setCopiedUrl(null), 2000);
  };

  return (
    <div className="space-y-8 w-full">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold font-mono tracking-tight text-white flex items-center gap-2.5">
          <Mail className="w-6 h-6 text-teal-400" />
          Email NLP Threat Scanner
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Analyzes natural language patterns, urgency pressure, credential harvesting, and suspicious calls-to-action using a TF-IDF classifier.
        </p>
      </div>

      {/* Drag & Drop .EML Parser Area */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`p-6 rounded-2xl border-2 border-dashed transition-all cursor-pointer text-center relative overflow-hidden ${
          isDragging
            ? 'border-teal-400 bg-teal-950/40 scale-[1.01]'
            : 'border-slate-800 hover:border-teal-500/50 bg-slate-900/50 hover:bg-slate-900/80'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".eml,.msg,.txt"
          className="hidden"
          onChange={(e) => {
            if (e.target.files && e.target.files.length > 0) {
              handleFileUpload(e.target.files[0]);
            }
          }}
        />

        <div className="flex flex-col items-center justify-center gap-2">
          <div className="w-12 h-12 rounded-xl bg-teal-950/60 border border-teal-800 flex items-center justify-center text-teal-400">
            {fileLoading ? (
              <div className="w-6 h-6 border-2 border-teal-400 border-t-transparent rounded-full animate-spin" />
            ) : (
              <UploadCloud className="w-6 h-6" />
            )}
          </div>
          <div>
            <h3 className="text-sm font-bold font-mono text-white">
              {fileLoading ? 'Parsing MIME Headers & Body...' : 'Drag & Drop an RFC 822 (.eml) File Here'}
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              or click to browse from disk. Automatically parses headers, SPF/DKIM flags, embedded links, and attachments.
            </p>
          </div>
          {uploadedFileName && (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-950 border border-teal-800 text-xs font-mono text-teal-300">
              <FileCheck className="w-3.5 h-3.5" /> Loaded: {uploadedFileName}
            </span>
          )}
        </div>
      </div>

      {/* Manual Input Console */}
      <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-4 shadow-xl">
        <div className="space-y-2">
          <label className="text-xs font-mono font-semibold text-slate-300 uppercase tracking-wider block">
            Email Subject Line (Optional)
          </label>
          <input
            type="text"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            placeholder="e.g. URGENT: Action required on your account"
            className="w-full bg-slate-950 border border-slate-800 focus:border-teal-500 rounded-xl px-4 py-2.5 text-sm font-sans text-white placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all"
          />
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-xs font-mono font-semibold text-slate-300 uppercase tracking-wider">
              Email Body Text
            </label>
            <span className="text-xs font-mono text-slate-400">
              {body.length} characters
            </span>
          </div>
          <textarea
            rows={6}
            value={body}
            onChange={(e) => setBody(e.target.value)}
            placeholder="Paste raw email body text or drop an .eml file above..."
            className="w-full bg-slate-950 border border-slate-800 focus:border-teal-500 rounded-xl px-4 py-3 text-sm font-sans text-white placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all resize-y"
          />
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2">
          {/* Preset Buttons */}
          <div className="w-full sm:w-auto">
            <span className="text-xs font-mono text-slate-400 flex items-center gap-1.5 mb-2">
              <Sparkles className="w-3.5 h-3.5 text-teal-400" />
              Demo Presets:
            </span>
            <div className="flex flex-wrap gap-2">
              {emailPresets.map((p, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setUploadedFileName(null);
                    setSubject(p.subject);
                    setBody(p.body);
                    handleScan(p.subject, p.body);
                  }}
                  className="px-2.5 py-1 rounded-lg bg-slate-950/80 hover:bg-slate-800 border border-slate-800 hover:border-teal-800 text-[11px] font-mono text-slate-300 hover:text-teal-300 transition-all truncate max-w-xs text-left"
                >
                  {p.title}
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-3 w-full sm:w-auto justify-end">
            {(subject || body) && (
              <button
                onClick={() => {
                  setSubject('');
                  setBody('');
                  setUploadedFileName(null);
                }}
                className="px-4 py-2.5 rounded-xl border border-slate-800 text-xs font-mono text-slate-400 hover:text-slate-200 transition-colors"
              >
                Clear
              </button>
            )}

            <button
              onClick={() => handleScan()}
              disabled={loading || !body.trim()}
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-teal-500 to-cyan-500 hover:from-teal-400 hover:to-cyan-400 font-mono font-semibold text-sm text-slate-950 flex items-center justify-center gap-2 transition-all shadow-md shadow-teal-500/20 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
                  Analyzing Text...
                </>
              ) : (
                <>
                  <Search className="w-4 h-4" />
                  Scan Email
                </>
              )}
            </button>
          </div>
        </div>

        {/* Privacy Assurance */}
        <div className="flex items-center gap-2 text-xs font-mono text-teal-400 bg-teal-950/30 border border-teal-900/40 p-2.5 rounded-lg">
          <Lock className="w-3.5 h-3.5 shrink-0" />
          <span>Privacy Protection: Raw email content is analyzed locally and never saved to persistent storage or sent to external AI APIs.</span>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-900/60 text-sm text-rose-300 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />
          <p>{error}</p>
        </div>
      )}

      {/* EML File Transport & Header Inspection Card */}
      {result?.eml_metadata && (
        <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-4 shadow-xl animate-in fade-in duration-200">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="text-sm font-bold font-mono text-white uppercase flex items-center gap-2">
              <FileCheck className="w-4 h-4 text-teal-400" />
              MIME Header & Transport Authentication
            </h3>
            <span className="text-xs font-mono text-slate-400">
              Parsed from: {uploadedFileName || 'RFC 822 stream'}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs font-mono">
            <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
              <span className="text-slate-400 block text-[10px] uppercase">From:</span>
              <span className="text-slate-200 truncate block">{result.eml_metadata.from_header || '(Not specified)'}</span>
            </div>
            <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
              <span className="text-slate-400 block text-[10px] uppercase">To:</span>
              <span className="text-slate-200 truncate block">{result.eml_metadata.to_header || '(Not specified)'}</span>
            </div>
          </div>

          {/* Authentication Signals */}
          <div className="flex flex-wrap gap-2 text-xs font-mono">
            {result.eml_metadata.spf_header ? (
              <span className="px-2.5 py-1 rounded-lg bg-slate-950 border border-slate-800 text-slate-300 flex items-center gap-1.5">
                <span className="text-slate-400">SPF Header:</span> {result.eml_metadata.spf_header.slice(0, 40)}
              </span>
            ) : (
              <span className="px-2.5 py-1 rounded-lg bg-slate-950 border border-slate-800 text-slate-400">
                SPF: No explicit header
              </span>
            )}

            <span className={`px-2.5 py-1 rounded-lg border flex items-center gap-1.5 ${
              result.eml_metadata.dkim_present
                ? 'bg-emerald-950/60 border-emerald-800 text-emerald-300'
                : 'bg-slate-950 border-slate-800 text-slate-400'
            }`}>
              {result.eml_metadata.dkim_present ? <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> : null}
              DKIM Signature: {result.eml_metadata.dkim_present ? 'Present' : 'Not Present'}
            </span>
          </div>

          {/* Embedded URLs Table */}
          {result.eml_metadata.embedded_urls && result.eml_metadata.embedded_urls.length > 0 && (
            <div className="space-y-2 pt-2 border-t border-slate-800">
              <div className="flex items-center justify-between text-xs font-mono text-slate-300">
                <span className="font-semibold flex items-center gap-1.5">
                  <ExternalLink className="w-3.5 h-3.5 text-cyan-400" />
                  Extracted Embedded URLs ({result.eml_metadata.embedded_urls.length})
                </span>
                <span className="text-slate-400 text-[11px]">Copy to analyze in URL Scanner</span>
              </div>
              <div className="space-y-1.5 max-h-40 overflow-y-auto">
                {result.eml_metadata.embedded_urls.map((u, i) => (
                  <div key={i} className="flex items-center justify-between gap-2 p-2 rounded bg-slate-950 border border-slate-800 text-xs font-mono">
                    <span className="text-cyan-300 truncate max-w-lg">{u}</span>
                    <button
                      onClick={() => copyToClipboard(u)}
                      className="px-2 py-1 rounded bg-slate-900 hover:bg-slate-800 border border-slate-800 text-[11px] text-slate-300 hover:text-white flex items-center gap-1 shrink-0"
                    >
                      {copiedUrl === u ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                      {copiedUrl === u ? 'Copied' : 'Copy'}
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Attachments Section */}
          {result.eml_metadata.attachments && result.eml_metadata.attachments.length > 0 && (
            <div className="space-y-2 pt-2 border-t border-slate-800">
              <span className="text-xs font-mono font-semibold text-slate-300 flex items-center gap-1.5">
                <Paperclip className="w-3.5 h-3.5 text-amber-400" />
                Attachments ({result.eml_metadata.attachments.length})
              </span>
              <div className="space-y-1.5">
                {result.eml_metadata.attachments.map((att, i) => (
                  <div key={i} className="flex items-center justify-between p-2 rounded bg-slate-950 border border-slate-800 text-xs font-mono">
                    <div className="flex items-center gap-2">
                      <span className="text-white font-medium">{att.filename}</span>
                      <span className="text-slate-400 text-[11px]">({(att.size_bytes / 1024).toFixed(1)} KB)</span>
                    </div>
                    {att.is_executable ? (
                      <span className="px-2 py-0.5 rounded bg-rose-950 border border-rose-800 text-rose-300 text-[10px] uppercase font-bold flex items-center gap-1">
                        <ShieldAlert className="w-3 h-3" /> Risky File Type
                      </span>
                    ) : (
                      <span className="text-slate-400 text-[10px] uppercase">
                        {att.content_type}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Analysis Results Display */}
      {result && (
        <div className="space-y-8 animate-in fade-in duration-300">
          <ExplanationCard
            prediction={result.prediction}
            isPhishing={result.is_phishing}
            confidenceScore={result.confidence_score}
            phishingProbability={result.phishing_probability}
            riskLevel={result.risk_level}
            explanation={result.explanation}
            riskIndicators={result.risk_indicators}
            modelVersion={result.model_version}
            timestamp={result.timestamp}
            disclaimerOrWarning={result.warning}
            onExportReport={() => downloadForensicReport(result)}
          />

          <FeatureImportanceChart
            terms={result.influential_terms}
            title="Influential Vocabulary Terms"
            subtitle="Words and bigrams with highest mathematical influence on the classification score (TF-IDF weight × model coefficient)."
          />
        </div>
      )}

      <DisclaimerBanner />
    </div>
  );
};
