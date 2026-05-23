import React from "react";

export const FormContainer: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => (
  <div className="flex flex-col md:flex-row gap-8 flex-1 min-h-0 p-2 items-start h-full">
    {children}
  </div>
);

export const FormColumn: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => (
  <div className="w-full md:flex-1 space-y-6 md:overflow-y-auto md:pr-4 md:custom-scrollbar md:max-h-full pb-8">
    {children}
  </div>
);

interface FormSectionProps {
  title: string;
  children: React.ReactNode;
  sticky?: boolean;
}

export const FormSection: React.FC<FormSectionProps> = ({
  title,
  children,
  sticky,
}) => (
  <div className="space-y-4">
    <h3
      className={`text-[10px] font-bold uppercase tracking-wider text-default-400 py-2 z-20 border-b border-divider mb-2 ${sticky ? "sticky top-0 bg-content1/95 backdrop-blur-md" : ""}`}
    >
      {title}
    </h3>
    <div className="space-y-4">{children}</div>
  </div>
);

export const FormGrid: React.FC<{
  children: React.ReactNode;
  className?: string;
}> = ({ children, className = "" }) => (
  <div className={`grid grid-cols-1 md:grid-cols-2 gap-4 ${className}`}>
    {children}
  </div>
);
