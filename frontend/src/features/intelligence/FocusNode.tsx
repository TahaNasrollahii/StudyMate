"use client";

import React from "react";
import { motion } from "framer-motion";
import { useOSStore } from "../../core/store/useOSStore";
import { nodeMorphing } from "../../styles/animations";
import { cn } from "../../lib/utils";

import ReactMarkdown from "react-markdown";

export default function FocusNode() {
  const { activeNode, setOSMode, setActiveNode, setZDepth } = useOSStore();

  if (!activeNode) return null;

  const handleClose = () => {
    setActiveNode(null);
    setOSMode("idle");
    setZDepth(0);
  };

  return (
    <motion.div
      variants={nodeMorphing}
      initial="hidden"
      animate="visible"
      exit="hidden"
      className={cn(
        "glass-panel-active w-full max-w-4xl max-h-[80vh] overflow-y-auto p-12 rounded-3xl",
        "flex flex-col space-y-6 relative custom-scrollbar"
      )}
    >
      <button 
        onClick={handleClose}
        className="absolute top-8 right-8 w-10 h-10 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center transition-colors text-white"
      >
        ✕
      </button>

      <div className="flex items-center space-x-4">
        <span className="px-3 py-1 rounded-full bg-[var(--color-os-accent-primary)]/20 text-[var(--color-os-accent-primary)] text-sm font-semibold uppercase tracking-wider">
          {activeNode.mode}
        </span>
        <h2 className="text-3xl font-display font-medium text-white">{activeNode.topic}</h2>
      </div>

      <div className="prose prose-invert prose-lg max-w-none prose-headings:text-white prose-a:text-[var(--color-os-accent-primary)] prose-strong:text-white prose-p:text-[var(--color-os-text-secondary)] prose-li:text-[var(--color-os-text-secondary)]">
        <ReactMarkdown>{activeNode.result}</ReactMarkdown>
      </div>
    </motion.div>
  );
}
