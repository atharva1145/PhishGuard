import { UrlScanResult, EmailScanResult, HistoryItem } from '../types';

export function generateForensicMarkdown(result: UrlScanResult | EmailScanResult): string {
  const isUrl = result.scan_type === 'url';
  const urlRes = isUrl ? (result as UrlScanResult) : null;
  const emailRes = !isUrl ? (result as EmailScanResult) : null;

  const separator = '='.repeat(80);

  let doc = `${separator}\n`;
  doc += `PHISHGUARD AI FORENSIC INCIDENT INVESTIGATION REPORT\n`;
  doc += `${separator}\n\n`;

  doc += `[INCIDENT METADATA]\n`;
  doc += `Report ID:            ${result.scan_id}\n`;
  doc += `Timestamp (UTC/Local): ${result.timestamp}\n`;
  doc += `Target Type:          ${result.scan_type.toUpperCase()}\n`;
  doc += `Model Architecture:   ${result.model_version}\n`;
  doc += `Analyst Tooling:      PhishGuard v2.4 (Explainable AI Engine)\n\n`;

  doc += `[CLASSIFICATION & RISK ASSESSMENT]\n`;
  doc += `Prediction:           ${result.prediction.toUpperCase()}\n`;
  doc += `Verdict:              ${result.is_phishing ? 'CRITICAL - SUSPECTED PHISHING ATTACK' : 'BENIGN - POTENTIALLY LEGITIMATE'}\n`;
  doc += `Confidence Score:     ${(result.confidence_score * 100).toFixed(2)}%\n`;
  doc += `Phishing Probability: ${(result.phishing_probability * 100).toFixed(2)}%\n`;
  doc += `Risk Severity Level:  ${result.risk_level.toUpperCase()}\n\n`;

  doc += `[TARGET SPECIFICATION]\n`;
  if (isUrl && urlRes) {
    doc += `Analyzed Target URL:  ${urlRes.target}\n\n`;
    if (urlRes.brand_impersonation) {
      doc += `[BRAND IMPERSONATION & TYPOSQUATTING ALERT]\n`;
      doc += `Targeted Brand:       ${urlRes.brand_impersonation.target_brand}\n`;
      doc += `Canonical Domain:     ${urlRes.brand_impersonation.canonical_domain}\n`;
      doc += `Spoofing Technique:   ${urlRes.brand_impersonation.spoof_technique}\n`;
      doc += `Impersonation Score:  ${(urlRes.brand_impersonation.similarity_score * 100).toFixed(1)}%\n`;
      doc += `Details:              ${urlRes.brand_impersonation.details}\n\n`;
    }
    if (urlRes.ensemble_consensus) {
      doc += `[MULTI-MODEL ENSEMBLE CONSENSUS]\n`;
      doc += `Consensus Verdict:    ${urlRes.ensemble_consensus.consensus_verdict}\n`;
      doc += `Agreement Ratio:      ${(urlRes.ensemble_consensus.agreement_ratio * 100).toFixed(0)}%\n`;
      urlRes.ensemble_consensus.models.forEach((m) => {
        doc += `  - ${m.model_name}: ${m.prediction} (Probability: ${(m.phishing_probability * 100).toFixed(1)}%)\n`;
      });
      doc += `\n`;
    }
  } else if (emailRes) {
    doc += `Target Preview:       ${emailRes.target_preview}\n`;
    if (emailRes.extracted_subject) {
      doc += `Subject Line:         ${emailRes.extracted_subject}\n`;
    }
    if (emailRes.eml_metadata) {
      doc += `\n[EXTRACTED MIME HEADERS & FORENSICS]\n`;
      doc += `From Header:          ${emailRes.eml_metadata.from_header}\n`;
      doc += `To Header:            ${emailRes.eml_metadata.to_header}\n`;
      doc += `Date:                 ${emailRes.eml_metadata.date_header}\n`;
      doc += `SPF Header:           ${emailRes.eml_metadata.spf_header || 'Not provided in headers'}\n`;
      doc += `DKIM Signature:       ${emailRes.eml_metadata.dkim_present ? 'Present in headers' : 'Not detected in headers'}\n`;
      if (emailRes.eml_metadata.embedded_urls && emailRes.eml_metadata.embedded_urls.length > 0) {
        doc += `Embedded Hyperlinks (${emailRes.eml_metadata.embedded_urls.length}):\n`;
        emailRes.eml_metadata.embedded_urls.forEach((u, i) => {
          doc += `  [${i + 1}] ${u}\n`;
        });
      }
      if (emailRes.eml_metadata.attachments && emailRes.eml_metadata.attachments.length > 0) {
        doc += `Attachments (${emailRes.eml_metadata.attachments.length}):\n`;
        emailRes.eml_metadata.attachments.forEach((a, i) => {
          doc += `  [${i + 1}] ${a.filename} (${a.content_type}, ${a.size_bytes} bytes)${a.is_executable ? ' [CRITICAL: EXECUTABLE PAYLOAD]' : ''}\n`;
        });
      }
      doc += `\n`;
    }
  }

  doc += `[EXPLAINABLE AI REASONING & EXECUTIVE SUMMARY]\n`;
  doc += `${result.explanation}\n\n`;

  doc += `[DETECTED RISK INDICATORS (${result.risk_indicators.length})]\n`;
  if (result.risk_indicators.length === 0) {
    doc += `No high-confidence heuristic risk indicators triggered.\n\n`;
  } else {
    result.risk_indicators.forEach((ind, i) => {
      doc += `${i + 1}. [${ind.severity}] ${ind.name}\n`;
      doc += `   Evidence:  ${ind.evidence}\n`;
      doc += `   Rationale: ${ind.rationale}\n`;
    });
    doc += `\n`;
  }

  if (isUrl && urlRes && urlRes.feature_contributions && urlRes.feature_contributions.length > 0) {
    doc += `[FEATURE ATTRIBUTION LOG-ODDS (TOP CONTRIBUTORS)]\n`;
    doc += `${'Feature'.padEnd(30)} | ${'Direction'.padEnd(12)} | ${'Contribution'.padEnd(14)} | Raw Value\n`;
    doc += `${'-'.repeat(30)}-+-${'-'.repeat(12)}-+-${'-'.repeat(14)}-+----------\n`;
    urlRes.feature_contributions.forEach((fc) => {
      const feat = fc.display_name.padEnd(30);
      const dir = fc.direction.toUpperCase().padEnd(12);
      const cont = (fc.contribution >= 0 ? `+${fc.contribution.toFixed(4)}` : fc.contribution.toFixed(4)).padEnd(14);
      doc += `${feat} | ${dir} | ${cont} | ${fc.raw_value}\n`;
    });
    doc += `\n`;
  } else if (emailRes && emailRes.influential_terms && emailRes.influential_terms.length > 0) {
    doc += `[INFLUENTIAL VOCABULARY ATTRIBUTIONS]\n`;
    doc += `${'Term'.padEnd(25)} | ${'Direction'.padEnd(12)} | ${'Weight'.padEnd(12)} | TF-IDF\n`;
    doc += `${'-'.repeat(25)}-+-${'-'.repeat(12)}-+-${'-'.repeat(12)}-+--------\n`;
    emailRes.influential_terms.forEach((term) => {
      const t = term.term.padEnd(25);
      const dir = term.direction.toUpperCase().padEnd(12);
      const w = (term.contribution >= 0 ? `+${term.contribution.toFixed(4)}` : term.contribution.toFixed(4)).padEnd(12);
      doc += `${t} | ${dir} | ${w} | ${term.tfidf_value.toFixed(4)}\n`;
    });
    doc += `\n`;
  }

  doc += `[SECURITY NOTICE & CHAIN OF CUSTODY]\n`;
  doc += `This assessment was generated locally by the PhishGuard machine learning engine.\n`;
  doc += `No network requests were dispatched to the analyzed targets during scanning.\n`;
  doc += `Machine learning predictions are probabilistic indicators and should be corroborated\n`;
  doc += `with defense-in-depth security telemetry prior to active quarantine or remediation.\n`;
  doc += `${separator}\n`;
  doc += `END OF FORENSIC REPORT\n`;

  return doc;
}

export function downloadForensicReport(result: UrlScanResult | EmailScanResult): void {
  const content = generateForensicMarkdown(result);
  const targetTag = result.scan_type === 'url' ? 'url' : 'email';
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
  const filename = `phishguard-forensic-report-${targetTag}-${timestamp}.txt`;

  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

export function downloadHistoryForensicReport(item: HistoryItem): void {
  const prob = item.details?.phishing_probability ?? (item.is_phishing ? item.confidence_score : 1 - item.confidence_score);
  const syntheticResult: any = {
    scan_id: item.scan_id,
    scan_type: item.scan_type,
    target: item.target_preview,
    target_preview: item.target_preview,
    prediction: item.prediction,
    is_phishing: item.is_phishing,
    confidence_score: item.confidence_score,
    phishing_probability: prob,
    risk_level: item.risk_level,
    risk_indicators: item.details?.risk_indicators || [],
    feature_contributions: item.details?.feature_contributions || [],
    influential_terms: item.details?.influential_terms || [],
    explanation: item.details?.explanation || `Historical scan record for ${item.target_preview}`,
    model_version: item.model_version,
    timestamp: item.created_at,
    disclaimer: 'Generated from PhishGuard local audit history.',
  };
  downloadForensicReport(syntheticResult);
}
