'use client';

import React, { createContext, useContext, ReactNode } from 'react';
import { SectionData } from '@/types/validation';

type DataMode = 'OLD' | 'NEW' | 'OLD_NEW';

interface DataContextType {
  selectedSections: SectionData[];
  dataMode: DataMode;
  stockId: string;
  triggerId: string;
}

const DataContext = createContext<DataContextType | undefined>(undefined);

interface DataProviderProps {
  children: ReactNode;
  selectedSections: SectionData[];
  dataMode: DataMode;
  stockId: string;
  triggerId: string;
}

export function DataProvider({
  children,
  selectedSections,
  dataMode,
  stockId,
  triggerId
}: DataProviderProps) {
  const value: DataContextType = {
    selectedSections,
    dataMode,
    stockId,
    triggerId
  };

  return <DataContext.Provider value={value}>{children}</DataContext.Provider>;
}

export function useData() {
  const context = useContext(DataContext);
  if (context === undefined) {
    throw new Error('useData must be used within a DataProvider');
  }
  return context;
}
