import React from 'react';
import { 
  BookOpen, 
  ShieldCheck, 
  AlertTriangle, 
  Layers, 
  Cpu, 
  Lock, 
  Terminal, 
  Database,
  CheckCircle2,
  FileText
} from 'lucide-react';
import { DisclaimerBanner } from '../components/DisclaimerBanner';

export const AboutPage: React.FC = () => {
  return (
    <div className="space-y-8 w-full">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold font-mono tracking-tight text-white flex items-center gap-2.5">
          <BookOpen className="w-6 h-6 text-cyan-400" />
          About & Scientific Methodology
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Technical specifications, feature engineering taxonomy, training protocols, and system boundaries.
        </p>
      </div>

      {/* Scope: What PhishGuard Does vs Cannot Determine */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-6 rounded-2xl bg-emerald-950/20 border border-emerald-900/40 space-y-3">
          <h3 className="text-sm font-bold font-mono text-emerald-400 uppercase tracking-wider flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4" />
            What PhishGuard Analyzes
          </h3>
          <ul className="text-xs text-slate-300 space-y-2 leading-relaxed">
            <li className="flex items-start gap-2">
              <span className="text-emerald-400 font-bold">•</span>
              <span><strong>URL Lexical & Structural Metrics:</strong> Parses hostname length, subdomain depth, IP addresses, punycode, non-standard ports, and deceptive keyword sequences.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-emerald-400 font-bold">•</span>
              <span><strong>Email NLP Linguistics:</strong> Uses TF-IDF tokenization to identify psychological urgency cues, direct credential requests, and payment fraud patterns.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-emerald-400 font-bold">•</span>
              <span><strong>Explainable AI Attributions:</strong> Computes exact log-odds contributions ($w_i \cdot x_i$) for linear classifiers and pairs them with transparent heuristic rationale.</span>
            </li>
          </ul>
        </div>

        <div className="p-6 rounded-2xl bg-rose-950/20 border border-rose-900/40 space-y-3">
          <h3 className="text-sm font-bold font-mono text-rose-400 uppercase tracking-wider flex items-center gap-2">
            <AlertTriangle className="w-4 h-4" />
            System Boundaries & Limitations
          </h3>
          <ul className="text-xs text-slate-300 space-y-2 leading-relaxed">
            <li className="flex items-start gap-2">
              <span className="text-rose-400 font-bold">•</span>
              <span><strong>Zero Dynamic Execution:</strong> PhishGuard never opens an HTTP socket to a submitted URL or downloads JavaScript, DOM elements, or file attachments.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-rose-400 font-bold">•</span>
              <span><strong>No Transport Header Verification:</strong> When analyzing email text, PhishGuard does not inspect SPF, DKIM, or DMARC records, as those require raw server relay headers.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-rose-400 font-bold">•</span>
              <span><strong>Adversarial Evasion:</strong> Attackers continuously adapt vocabulary and register lookalike domains; static classifiers must be paired with defense-in-depth security controls.</span>
            </li>
          </ul>
        </div>
      </div>

      {/* Model Architectures */}
      <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-4">
        <h3 className="text-base font-bold font-mono text-white flex items-center gap-2">
          <Cpu className="w-4 h-4 text-cyan-400" />
          Model Architecture & Training Protocol
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
            <span className="font-semibold text-cyan-400 text-sm">URL Classifier</span>
            <p className="text-slate-300 font-sans leading-relaxed">
              Standardized numerical feature vector ($D=24$) passed into an L2-regularized Logistic Regression classifier with balanced class weights. Evaluated against Random Forest and Linear SVM candidates via 5-Fold Stratified Cross-Validation on training data.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
            <span className="font-semibold text-teal-400 text-sm">Email NLP Classifier</span>
            <p className="text-slate-300 font-sans leading-relaxed">
              Sublinear TF-IDF vectorizer ($N$-grams 1-2, max features 5,000, English stop-word filtering) feeding into a Logistic Regression classifier. Vocabulary and IDF weights are fitted exclusively on training splits to prevent data snooping leakage.
            </p>
          </div>
        </div>
      </div>

      {/* Leakage Prevention & Train/Test Separation */}
      <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-3">
        <h3 className="text-base font-bold font-mono text-white flex items-center gap-2">
          <Layers className="w-4 h-4 text-cyan-400" />
          Train/Test Separation & Leakage Controls
        </h3>
        <p className="text-xs text-slate-300 leading-relaxed font-sans">
          To ensure valid generalization measurement, datasets undergo rigorous deduplication on normalized text and URL keys prior to splitting. An 80/20 stratified split is established with a fixed random seed (42). Automated unit tests explicitly assert that the set intersection of training items and testing items is strictly empty ($A \cap B = \emptyset$).
        </p>
      </div>

      {/* Dataset Sources and Licenses */}
      <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-4">
        <h3 className="text-base font-bold font-mono text-white flex items-center gap-2">
          <Database className="w-4 h-4 text-cyan-400" />
          Dataset Provenance & Licenses
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase">
                <th className="py-2.5 px-3">Dataset Domain</th>
                <th className="py-2.5 px-3">Primary Source / Benchmark</th>
                <th className="py-2.5 px-3">License / Terms</th>
                <th className="py-2.5 px-3">Target Definition</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              <tr>
                <td className="py-2.5 px-3 font-semibold text-cyan-400">URL Detection</td>
                <td className="py-2.5 px-3">PhishTank Verified Archives & Tranco Top 1M</td>
                <td className="py-2.5 px-3">CC0 / Open Data Commons</td>
                <td className="py-2.5 px-3">0 = Legitimate Root/Path, 1 = Phishing Spoof</td>
              </tr>
              <tr>
                <td className="py-2.5 px-3 font-semibold text-teal-400">Email NLP</td>
                <td className="py-2.5 px-3">Apache SpamAssassin Public Corpus & Nazario Archives</td>
                <td className="py-2.5 px-3">Public Domain / Apache 2.0</td>
                <td className="py-2.5 px-3">0 = Benign Corporate/Tech, 1 = Social Engineering Phish</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Reproduction Commands */}
      <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-3">
        <h3 className="text-base font-bold font-mono text-white flex items-center gap-2">
          <Terminal className="w-4 h-4 text-cyan-400" />
          Reproducibility Guide (Local Commands)
        </h3>
        <div className="p-4 rounded-xl bg-slate-950 font-mono text-xs text-slate-300 space-y-2 border border-slate-800">
          <p className="text-slate-400"># Train both classifiers and generate evaluation JSON reports:</p>
          <p className="text-cyan-400">python scripts/train_models.py</p>
          <p className="text-slate-400 mt-2"># Run the full automated test suite (28 unit & integration tests):</p>
          <p className="text-cyan-400">python -m pytest</p>
          <p className="text-slate-400 mt-2"># Start the FastAPI backend server:</p>
          <p className="text-cyan-400">uvicorn backend.app.main:app --reload --port 8000</p>
        </div>
      </div>

      <DisclaimerBanner />
    </div>
  );
};
