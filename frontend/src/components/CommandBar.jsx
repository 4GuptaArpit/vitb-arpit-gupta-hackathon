import React, { useState, useEffect } from 'react';

export default function CommandBar({ isOpen, onClose, onExecuteMnemonic }) {
  const [query, setQuery] = useState('');

  const COMMANDS = [
    { mnemonic: 'ATTRIB <GO>', desc: 'View Brinson-Fachler Multi-Factor Attribution', action: () => onExecuteMnemonic('ATTRIB') },
    { mnemonic: 'GOVERNOR <GO>', desc: 'Toggle Basel III / RBI Capital Conservation Governor', action: () => onExecuteMnemonic('GOVERNOR') },
    { mnemonic: 'REBALANCE <GO>', desc: 'Run Tactical Quadratic Index Rebalance', action: () => onExecuteMnemonic('REBALANCE') },
    { mnemonic: 'RESET <GO>', desc: 'Reset Active Allocations to Benchmark Index', action: () => onExecuteMnemonic('RESET') },
    { mnemonic: 'STRESS <GO>', desc: 'Run Macroeconomic Wholesale Stress Scenario', action: () => onExecuteMnemonic('STRESS') },
    { mnemonic: 'QUADRANT <GO>', desc: 'Toggle Bloomberg 4-Quadrant Command Desk', action: () => onExecuteMnemonic('QUADRANT') },
  ];

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen) {
        e.preventDefault();
        onClose(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const filtered = COMMANDS.filter(c => 
    c.mnemonic.toLowerCase().includes(query.toLowerCase()) || 
    c.desc.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-start justify-center pt-20 px-4">
      <div className="w-full max-w-2xl bg-slate-900 border border-cyan-500/50 rounded-xl shadow-2xl overflow-hidden font-mono">
        <div className="flex items-center px-4 py-3 border-b border-slate-800 bg-slate-950/80">
          <span className="text-cyan-400 font-bold mr-3 text-sm">CRISIL/BLOOMBERG PROMPT &gt;</span>
          <input
            type="text"
            className="w-full bg-transparent text-slate-100 placeholder-slate-500 text-sm focus:outline-none"
            placeholder="Type mnemonic (e.g. ATTRIB, REBALANCE, STRESS) and press Enter..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            autoFocus
            onKeyDown={(e) => {
              if (e.key === 'Enter' && filtered.length > 0) {
                filtered[0].action();
                onClose(false);
              }
            }}
          />
          <kbd className="text-[10px] text-slate-400 bg-slate-800 px-2 py-0.5 rounded border border-slate-700">ESC</kbd>
        </div>
        <div className="max-h-64 overflow-y-auto divide-y divide-slate-800/60">
          {filtered.map((cmd, i) => (
            <div
              key={i}
              onClick={() => {
                cmd.action();
                onClose(false);
              }}
              className="px-4 py-3 flex items-center justify-between hover:bg-cyan-950/40 cursor-pointer transition text-xs"
            >
              <span className="text-amber-400 font-bold">{cmd.mnemonic}</span>
              <span className="text-slate-400">{cmd.desc}</span>
            </div>
          ))}
          {filtered.length === 0 && (
            <div className="px-4 py-6 text-center text-slate-500 text-xs">
              No recognized mnemonic. Try <span className="text-cyan-400 font-semibold">ATTRIB &lt;GO&gt;</span> or <span className="text-cyan-400 font-semibold">REBALANCE &lt;GO&gt;</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
