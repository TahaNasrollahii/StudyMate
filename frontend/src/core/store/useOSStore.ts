import { create } from 'zustand';
import { StudyResponseData, StudyMode } from '../types';

export type OSMode = 'idle' | 'focus' | 'synapse' | 'memory' | 'auth';

interface OSState {
  // Auth State
  isAuthenticated: boolean;
  setIsAuthenticated: (val: boolean) => void;

  // Global OS State
  currentMode: OSMode;
  setOSMode: (mode: OSMode) => void;

  // History / Memory
  memoryNodes: StudyResponseData[];
  setMemoryNodes: (nodes: StudyResponseData[]) => void;
  addMemoryNode: (node: StudyResponseData) => void;

  // Active Focus
  activeNode: StudyResponseData | null;
  setActiveNode: (node: StudyResponseData | null) => void;

  // Spatial Navigation (Z-axis offset)
  zDepth: number;
  setZDepth: (depth: number) => void;
}

export const useOSStore = create<OSState>((set) => ({
  isAuthenticated: false,
  setIsAuthenticated: (val) => set({ isAuthenticated: val }),

  currentMode: 'auth',
  setOSMode: (mode) => set({ currentMode: mode }),

  memoryNodes: [],
  setMemoryNodes: (nodes) => set({ memoryNodes: nodes }),
  addMemoryNode: (node) =>
    set((state) => ({ memoryNodes: [node, ...state.memoryNodes] })),

  activeNode: null,
  setActiveNode: (node) => set({ activeNode: node }),

  zDepth: 0,
  setZDepth: (depth) => set({ zDepth: depth }),
}));
