'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from '@/providers/I18nProvider';

export default function AdminPage() {
  const t = useTranslations();
  const [rtspUrl, setRtspUrl] = useState('');
  const [demoMode, setDemoMode] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem('rtspUrl');
    if (saved) setRtspUrl(saved);
    const demo = localStorage.getItem('demoMode');
    if (demo === 'true') setDemoMode(true);
  }, []);

  const save = () => {
    localStorage.setItem('rtspUrl', rtspUrl);
    alert('saved (local only)');
  };

  const toggleDemoMode = () => {
    const newMode = !demoMode;
    setDemoMode(newMode);
    localStorage.setItem('demoMode', String(newMode));
    if (newMode) {
      alert('Demo mode enabled - Using mock detection data');
    }
  };

  return (
    <div className="space-y-4">
      <div className="bg-surface border border-border rounded-lg p-4 max-w-lg animate-fade-in hover-lift">
        <h1 className="text-lg font-semibold mb-4">{t('admin.title')}</h1>
        <label className="text-xs text-muted mb-2 block">
          {t('admin.rtsp')}
        </label>
        <input
          value={rtspUrl}
          onChange={(e) => setRtspUrl(e.target.value)}
          className="w-full bg-background border border-border rounded px-3 py-2 text-sm transition-base focus:outline-none focus:ring-2 focus:ring-accent focus:border-accent"
          placeholder="rtsp://192.168.0.150:8554/unicast"
        />
        <button
          onClick={save}
          className="mt-3 px-3 py-1.5 bg-foreground text-background rounded text-sm transition-base hover-scale hover:opacity-90"
        >
          {t('admin.save')}
        </button>
      </div>

      <div className="bg-surface border border-border rounded-lg p-4 max-w-lg animate-fade-in hover-lift" style={{ animationDelay: '100ms' }}>
        <h2 className="text-sm font-semibold mb-3">Demo Mode</h2>
        <p className="text-xs text-muted mb-3">
          Enable demo mode to use mock detection data when Jetson hardware is not available.
        </p>
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={demoMode}
            onChange={toggleDemoMode}
            className="w-4 h-4 rounded border-border text-accent focus:ring-2 focus:ring-accent"
          />
          <span className="text-sm text-foreground">
            {demoMode ? 'Demo mode enabled' : 'Enable demo mode'}
          </span>
        </label>
        {demoMode && (
          <p className="text-xs text-positive mt-2">
            ✓ Mock detection data will be used. Refresh the Live page to see demo data.
          </p>
        )}
      </div>
    </div>
  );
}