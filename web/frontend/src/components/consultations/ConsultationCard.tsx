import { memo, useState } from 'react';
import { ChevronDown, ChevronUp, Stethoscope } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { formatDateTime } from '../../utils/formatters';
import type { Consultation } from '../../types/patient';

interface Props {
  consultation: Consultation;
}

export default memo(function ConsultationCard({ consultation: c }: Props) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full px-5 py-4 flex items-center gap-3 hover:bg-gray-50 transition-colors text-left"
        aria-expanded={expanded}
      >
        <div className="w-10 h-10 bg-medical-light rounded-lg flex items-center justify-center shrink-0">
          <Stethoscope size={20} className="text-medical-teal" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-gray-800">{c.specialty}</span>
            <span className="text-xs text-gray-400">{formatDateTime(c.date)}</span>
          </div>
          <p className="text-sm text-gray-500 truncate">{c.complaints}</p>
        </div>
        {expanded ? <ChevronUp size={18} className="text-gray-400" /> : <ChevronDown size={18} className="text-gray-400" />}
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-5 pb-4 border-t border-gray-100 pt-3">
              <pre className="whitespace-pre-wrap text-sm text-gray-700 font-sans leading-relaxed">
                {typeof c.response === 'string'
                  ? c.response
                  : JSON.stringify(c.response, null, 2)}
              </pre>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
});
