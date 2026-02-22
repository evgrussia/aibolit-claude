import { useState } from 'react';
import { Info, ChevronDown, ChevronUp, AlertTriangle, Lightbulb } from 'lucide-react';
import clsx from 'clsx';

type BannerVariant = 'info' | 'tip' | 'warning';

interface InfoBannerProps {
  variant?: BannerVariant;
  title: string;
  children: React.ReactNode;
  collapsible?: boolean;
  defaultOpen?: boolean;
}

const STYLES: Record<BannerVariant, { bg: string; border: string; icon: React.ReactNode; titleColor: string }> = {
  info: {
    bg: 'bg-blue-50',
    border: 'border-blue-200',
    icon: <Info size={15} className="text-blue-500 shrink-0 mt-0.5" />,
    titleColor: 'text-blue-800',
  },
  tip: {
    bg: 'bg-amber-50',
    border: 'border-amber-200',
    icon: <Lightbulb size={15} className="text-amber-500 shrink-0 mt-0.5" />,
    titleColor: 'text-amber-800',
  },
  warning: {
    bg: 'bg-orange-50',
    border: 'border-orange-200',
    icon: <AlertTriangle size={15} className="text-orange-500 shrink-0 mt-0.5" />,
    titleColor: 'text-orange-800',
  },
};

export default function InfoBanner({
  variant = 'info',
  title,
  children,
  collapsible = true,
  defaultOpen = false,
}: InfoBannerProps) {
  const [open, setOpen] = useState(defaultOpen);
  const s = STYLES[variant];

  return (
    <div className={clsx('rounded-xl border p-3 text-sm', s.bg, s.border)}>
      <button
        className="w-full flex items-start gap-2 text-left"
        onClick={() => collapsible && setOpen(o => !o)}
        disabled={!collapsible}
      >
        {s.icon}
        <span className={clsx('font-semibold flex-1', s.titleColor)}>{title}</span>
        {collapsible && (
          open
            ? <ChevronUp size={15} className="text-gray-400 shrink-0 mt-0.5" />
            : <ChevronDown size={15} className="text-gray-400 shrink-0 mt-0.5" />
        )}
      </button>
      {(!collapsible || open) && (
        <div className={clsx('mt-2 ml-5 text-xs leading-relaxed', s.titleColor.replace('800', '700'))}>
          {children}
        </div>
      )}
    </div>
  );
}
