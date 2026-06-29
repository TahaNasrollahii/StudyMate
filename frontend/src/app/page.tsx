"use client";

import { useEffect } from "react";
import { AnimatePresence } from "framer-motion";
import SpatialCanvas from "../components/spatial/SpatialCanvas";
import Synthesizer from "../features/workspace/Synthesizer";
import FocusNode from "../features/intelligence/FocusNode";
import SynapseState from "../features/intelligence/SynapseState";
import Constellation from "../features/memory/Constellation";
import CinematicAuth from "../features/auth/CinematicAuth";
import { useOSStore } from "../core/store/useOSStore";
import { cn } from "../lib/utils";

export default function CognitiveOS() {
  const { currentMode, setOSMode, setIsAuthenticated, isAuthenticated } = useOSStore();

  useEffect(() => {
    // Basic initialization check
    const token = localStorage.getItem("access_token");
    if (token) {
      setIsAuthenticated(true);
      if (currentMode === "auth") setOSMode("idle");
    } else {
      setIsAuthenticated(false);
      setOSMode("auth");
    }
  }, [setIsAuthenticated, setOSMode, currentMode]);

  return (
    <main className="w-screen h-screen overflow-hidden text-white font-sans">
      <SpatialCanvas>
        <AnimatePresence mode="wait">
          {currentMode === "auth" && <CinematicAuth key="auth" />}
          {currentMode === "idle" && <Synthesizer key="synthesizer" />}
          {currentMode === "synapse" && <SynapseState key="synapse" />}
          {currentMode === "focus" && <FocusNode key="focus" />}
          {currentMode === "memory" && <Constellation key="memory" />}
        </AnimatePresence>
      </SpatialCanvas>

      {/* OS Controls (Floating Dock) - Hidden during Auth */}
      {currentMode !== "auth" && (
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 glass-panel rounded-full px-6 py-3 flex space-x-4 items-center z-50">
          <button 
            onClick={() => setOSMode("idle")}
            className={cn(
              "text-sm tracking-wide uppercase px-4 py-1.5 rounded-full transition-colors",
              currentMode === "idle" ? "bg-white/20 text-white" : "text-white/50 hover:text-white"
            )}
          >
            Synthesizer
          </button>
          <div className="w-px h-4 bg-white/10" />
          <button 
            onClick={() => setOSMode("memory")}
            className={cn(
              "text-sm tracking-wide uppercase px-4 py-1.5 rounded-full transition-colors",
              currentMode === "memory" ? "bg-white/20 text-white" : "text-white/50 hover:text-white"
            )}
          >
            Memory
          </button>
        </div>
      )}

      {/* Top Right Controls - Disconnect / Logout */}
      {currentMode !== "auth" && (
        <div className="absolute top-8 right-8 z-50">
          <button 
            onClick={() => {
              localStorage.removeItem("access_token");
              localStorage.removeItem("refresh_token");
              setIsAuthenticated(false);
              setOSMode("auth");
            }}
            className="group relative flex items-center justify-center px-6 py-2.5 overflow-hidden rounded-full border border-white/10 bg-black/40 backdrop-blur-md transition-all duration-300 hover:bg-white/10 hover:border-white/30 hover:shadow-[0_0_25px_rgba(255,255,255,0.15)]"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-red-500/20 to-orange-500/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            <span className="relative z-10 text-xs font-medium tracking-[0.2em] uppercase text-white/60 group-hover:text-white transition-colors duration-300">
              Disconnect
            </span>
          </button>
        </div>
      )}
    </main>
  );
}

