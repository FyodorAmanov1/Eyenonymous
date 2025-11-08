'use client';

import { useTheme } from '@/providers/ThemeProvider';
import { Moon, Sun } from 'lucide-react';

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();
  return (
    <button
      type="button"
      onClick={toggleTheme}
      aria-label="Toggle theme"
      className="h-8 px-3 rounded border border-border bg-surface text-foreground text-xs transition-base hover:bg-accent-ghost hover:text-accent hover:border-accent hover-scale"
    >
      {theme === 'dark' ? <Sun className="w-4 h-4 transition-base" /> : <Moon className="w-4 h-4 transition-base" />}
    </button>
  );
}


