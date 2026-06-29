"use client";

import React from "react";
import { motion } from "framer-motion";

export default function SynapseState() {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 1.2 }}
      className="flex flex-col items-center justify-center space-y-8"
    >
      <div className="relative w-32 h-32">
        <motion.div
          animate={{
            scale: [1, 1.5, 1],
            opacity: [0.3, 0.8, 0.3],
            rotate: [0, 90, 180],
          }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
          className="absolute inset-0 rounded-full border border-[var(--color-os-accent-primary)] mix-blend-screen shadow-[0_0_50px_rgba(0,240,255,0.5)]"
        />
        <motion.div
          animate={{
            scale: [1.5, 1, 1.5],
            opacity: [0.8, 0.3, 0.8],
            rotate: [180, 90, 0],
          }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut", delay: 0.5 }}
          className="absolute inset-0 rounded-full border border-[var(--color-os-accent-secondary)] mix-blend-screen shadow-[0_0_50px_rgba(112,0,255,0.5)]"
        />
      </div>
      <motion.p
        animate={{ opacity: [0.5, 1, 0.5] }}
        transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
        className="text-[var(--color-os-accent-primary)] font-display tracking-[0.2em] uppercase text-sm"
      >
        Synthesizing Cognitive Map...
      </motion.p>
    </motion.div>
  );
}
