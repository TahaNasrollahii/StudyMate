"use client";

import React, { useEffect } from "react";
import { motion, useSpring, useTransform } from "framer-motion";
import { useOSStore } from "../../core/store/useOSStore";
import { floatingBlob } from "../../styles/animations";
import { cn } from "../../lib/utils";

export default function SpatialCanvas({ children }: { children: React.ReactNode }) {
  const { currentMode, zDepth } = useOSStore();
  
  // Parallax rotation springs (-1 to 1)
  const mouseX = useSpring(0, { stiffness: 300, damping: 30 });
  const mouseY = useSpring(0, { stiffness: 300, damping: 30 });
  
  // Cursor coordinate springs (px)
  const cursorX = useSpring(0, { stiffness: 200, damping: 40 });
  const cursorY = useSpring(0, { stiffness: 200, damping: 40 });

  useEffect(() => {
    // Center the cursor light initially
    cursorX.set(window.innerWidth / 2);
    cursorY.set(window.innerHeight / 2);

    const handleMouseMove = (e: MouseEvent) => {
      mouseX.set((e.clientX / window.innerWidth) * 2 - 1);
      mouseY.set((e.clientY / window.innerHeight) * 2 - 1);
      cursorX.set(e.clientX);
      cursorY.set(e.clientY);
    };

    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, [mouseX, mouseY, cursorX, cursorY]);

  return (
    <div className="relative w-screen h-screen overflow-hidden bg-black perspective-1000">
      {/* Interactive Motion Light (Cursor Spotlight) */}
      <motion.div
        className="absolute top-0 left-0 w-[40vw] h-[40vw] rounded-full mix-blend-screen filter blur-[100px] pointer-events-none z-0"
        style={{
          x: useTransform(cursorX, (x) => `calc(${x}px - 20vw)`),
          y: useTransform(cursorY, (y) => `calc(${y}px - 20vw)`),
          backgroundColor: currentMode === "synapse" ? "rgba(112, 0, 255, 0.4)" : "rgba(0, 240, 255, 0.15)",
        }}
      />

      {/* Ambient Mesh Background (Floating Blobs) */}
      <div
        className={cn(
          "absolute inset-0 z-0 transition-opacity duration-1000",
          currentMode === "synapse" ? "opacity-100" : "opacity-40"
        )}
      >
        <motion.div 
          variants={floatingBlob}
          initial="idle"
          animate={currentMode === "synapse" ? "active" : "idle"}
          className="absolute top-1/4 left-1/4 w-[60vw] h-[60vh] bg-[var(--color-os-accent-primary)] rounded-full mix-blend-screen filter blur-[200px] opacity-20 origin-center pointer-events-none" 
        />
        <motion.div 
          variants={floatingBlob}
          initial="idle"
          animate={currentMode === "synapse" ? "active" : "idle"}
          style={{ animationDelay: "2s" }}
          className="absolute bottom-1/4 right-1/4 w-[60vw] h-[60vh] bg-[var(--color-os-accent-secondary)] rounded-full mix-blend-screen filter blur-[200px] opacity-20 origin-center pointer-events-none" 
        />
      </div>

      {/* Spatial Z-Axis Container */}
      <motion.div
        className="relative z-10 w-full h-full flex items-center justify-center transform-style-3d"
        style={{
          z: zDepth,
          rotateX: mouseY,
          rotateY: mouseX,
        }}
      >
        {children}
      </motion.div>
    </div>
  );
}
