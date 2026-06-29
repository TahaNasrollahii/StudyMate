"use client";

import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { useOSStore } from "../../core/store/useOSStore";
import { apiClient } from "../../core/api/client";
import { nodeMorphing } from "../../styles/animations";
import { cn } from "../../lib/utils";

export default function Constellation() {
  const { memoryNodes, setMemoryNodes, setActiveNode, setOSMode, setZDepth } = useOSStore();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await apiClient.get("/study/history");
        setMemoryNodes(res.data.results || []);
      } catch (err: any) {
        if (err?.message !== "No refresh token") {
          console.error("History fetch error:", err);
        }
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, [setMemoryNodes]);

  const handleNodeClick = (node: any) => {
    setActiveNode(node);
    setOSMode("focus");
    setZDepth(100);
  };

  if (loading) return null;

  return (
    <motion.div
      variants={nodeMorphing}
      initial="hidden"
      animate="visible"
      exit="hidden"
      className="absolute inset-0 flex items-center justify-center pointer-events-none"
    >
      <div className="relative w-full h-full max-w-[90vw] max-h-[90vh] perspective-1000">
        {memoryNodes.map((node, index) => {
          // Calculate spatial positions based on index to create a "constellation" effect
          const angle = index * 137.508; // Golden angle for organic distribution
          const radius = 100 + Math.sqrt(index) * 50;
          const x = Math.cos(angle * (Math.PI / 180)) * radius;
          const y = Math.sin(angle * (Math.PI / 180)) * radius;
          const z = -index * 50; // Older nodes go deeper into the Z-axis

          return (
            <motion.div
              key={node.id}
              className={cn(
                "absolute pointer-events-auto cursor-pointer",
                "w-48 h-48 rounded-2xl glass-panel flex flex-col p-6 items-center justify-center text-center",
                "hover:bg-white/10 hover:shadow-[0_0_20px_rgba(255,255,255,0.2)] transition-all duration-300"
              )}
              style={{
                left: `calc(50% + ${x}px)`,
                top: `calc(50% + ${y}px)`,
                transform: `translateZ(${z}px)`,
                opacity: Math.max(0.2, 1 - index * 0.05),
                filter: `blur(${Math.min(10, index * 0.5)}px)`,
              }}
              whileHover={{ scale: 1.1, z: z + 20, filter: "blur(0px)", opacity: 1 }}
              onClick={() => handleNodeClick(node)}
            >
              <h3 className="text-white font-medium text-lg truncate w-full">{node.topic}</h3>
              <span className="text-xs text-[var(--color-os-accent-primary)] mt-2 uppercase tracking-widest">{node.mode}</span>
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
}
