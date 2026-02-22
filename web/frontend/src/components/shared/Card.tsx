import clsx from 'clsx';
import { motion } from 'framer-motion';
import type { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  className?: string;
  title?: string;
  icon?: ReactNode;
}

export default function Card({ children, className, title, icon }: CardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={clsx('bg-white rounded-xl shadow-md border border-gray-100 overflow-hidden', className)}
    >
      {title && (
        <div className="px-5 py-3.5 border-b border-gray-100 flex items-center gap-2">
          {icon && <span className="text-medical-teal">{icon}</span>}
          <h3 className="font-semibold text-gray-800">{title}</h3>
        </div>
      )}
      <div className="p-5">{children}</div>
    </motion.div>
  );
}
