"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useOSStore } from "../../core/store/useOSStore";
import { StudyMode } from "../../core/types";
import { apiClient } from "../../core/api/client";
import { nodeMorphing } from "../../styles/animations";
import { cn } from "../../lib/utils";

export default function Synthesizer() {
  const { setOSMode, setActiveNode, setZDepth } = useOSStore();
  const [topic, setTopic] = useState("");
  const [mode, setMode] = useState<StudyMode>(StudyMode.SUMMARY);
  const [error, setError] = useState("");

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) return;

    setError("");
    setOSMode("synapse");
    setZDepth(-200); // push back during generation

    try {
      const res = await apiClient.post("/study/generate", { topic, mode });
      setActiveNode(res.data);
      setOSMode("focus");
      setZDepth(100); // pull forward on success
    } catch (err: any) {
      console.error(err);
      setOSMode("idle");
      setZDepth(0);
      
      const detail = err.response?.data?.detail;
      if (typeof detail === "string") {
        setError(detail);
      } else {
        setError("Synthesis failed. The neural link might be unstable or rate limited. Please try again.");
      }
    }
  };

  return (
    <motion.div
      variants={nodeMorphing}
      initial="hidden"
      animate="visible"
      exit="hidden"
      className="glass-panel w-full max-w-2xl p-8 md:p-12 rounded-3xl flex flex-col items-center justify-center text-center space-y-8"
    >
      <motion.h1 
        className="text-4xl md:text-6xl font-sans font-extralight tracking-tighter text-white/90"
      >
        Synthesize Knowledge
      </motion.h1>

      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="w-full text-red-400 text-sm bg-red-400/10 py-3 px-6 rounded-xl border border-red-400/20"
          >
            {error}
          </motion.div>
        )}
      </AnimatePresence>

      <form onSubmit={handleGenerate} className="w-full flex flex-col items-center space-y-6">
        <input
          type="text"
          placeholder="What do you want to understand?"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          className={cn(
            "w-full bg-black/40 border border-[var(--color-os-border)] rounded-2xl py-6 px-8 text-xl outline-none transition-all duration-500",
            "focus:border-[var(--color-os-accent-primary)] focus:bg-black/60 focus:shadow-[0_0_30px_rgba(0,240,255,0.2)]",
            "text-white placeholder-white/30 text-center"
          )}
        />
        
        <AnimatePresence>
          {topic.trim().length > 0 && (
            <motion.div 
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="flex justify-center space-x-4 pt-4 pb-8 w-full"
            >
              {[StudyMode.SUMMARY, StudyMode.QUIZ, StudyMode.PLAN].map((m) => (
                <button
                  key={m}
                  type="button"
                  onClick={() => setMode(m)}
                  className={cn(
                    "px-8 py-3 rounded-full text-xs font-semibold tracking-[0.15em] uppercase transition-all duration-500 border relative",
                    mode === m 
                      ? "bg-gradient-to-r from-[var(--color-os-accent-primary)] to-cyan-400 text-black border-transparent shadow-[0_0_40px_rgba(0,240,255,0.4)] scale-105"
                      : "bg-white/5 text-white/60 border-white/10 shadow-[0_0_20px_rgba(0,0,0,0.5)] hover:bg-white/10 hover:text-white hover:shadow-[0_0_25px_rgba(255,255,255,0.1)] hover:-translate-y-1"
                  )}
                >
                  {m}
                </button>
              ))}
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {topic.trim().length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 10 }}
              className="w-full flex justify-center mt-2"
            >
              <button
                type="submit"
                className="group relative flex items-center justify-center px-10 py-4 overflow-hidden rounded-2xl border border-white/10 bg-white/5 backdrop-blur-md transition-all duration-500 hover:bg-white/10 hover:border-[var(--color-os-accent-primary)] hover:shadow-[0_0_30px_rgba(0,240,255,0.3)] hover:-translate-y-1"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-[var(--color-os-accent-primary)] to-cyan-400 opacity-0 group-hover:opacity-20 transition-opacity duration-500" />
                <span className="relative z-10 text-sm font-medium tracking-[0.25em] uppercase text-white/70 group-hover:text-white transition-colors duration-500 flex items-center gap-3">
                  Initiate Synthesis
                  <svg className="w-4 h-4 opacity-70 group-hover:opacity-100 group-hover:translate-x-1 transition-all" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                  </svg>
                </span>
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </form>
    </motion.div>
  );
}
