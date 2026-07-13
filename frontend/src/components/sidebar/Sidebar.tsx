import React, { useState } from 'react';
import { TabButton } from '../shared/TabButton';
import { TransitPanel } from './TransitPanel';
import { EcoVisionPanel } from './EcoVisionPanel';
import { IncidentPanel } from './IncidentPanel';
import type { FanSession } from '../../types';

interface SidebarProps {
  session: FanSession;
  onUpdateTransit: (method: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ session, onUpdateTransit }) => {
  const [activeTab, setActiveTab] = useState<'transit' | 'eco' | 'incident'>('transit');

  return (
    <div className="flex flex-col h-full">
      <div className="flex border-b border-slate-800 mb-6">
        <TabButton 
          active={activeTab === 'transit'} 
          onClick={() => setActiveTab('transit')}
        >
          Transit
        </TabButton>
        <TabButton 
          active={activeTab === 'eco'} 
          onClick={() => setActiveTab('eco')}
        >
          Eco-Vision
        </TabButton>
        <TabButton 
          active={activeTab === 'incident'} 
          onClick={() => setActiveTab('incident')}
        >
          Report
        </TabButton>
      </div>

      <div className="flex-1 overflow-y-auto pr-2 pb-8 custom-scrollbar">
        {activeTab === 'transit' && (
          <TransitPanel session={session} onUpdateTransit={onUpdateTransit} />
        )}
        {activeTab === 'eco' && (
          <EcoVisionPanel />
        )}
        {activeTab === 'incident' && (
          <IncidentPanel />
        )}
      </div>
    </div>
  );
};
