import { Variants } from "framer-motion";

export const springConfig = {
  type: "spring",
  stiffness: 200,
  damping: 20,
  mass: 1,
};

export const slowSpringConfig = {
  type: "spring",
  stiffness: 100,
  damping: 30,
  mass: 1.5,
};

// Continuous floating animation for background gradients
export const floatingBlob: Variants = {
  idle: {
    x: ["-10%", "10%", "-5%", "-10%"],
    y: ["-5%", "10%", "-10%", "-5%"],
    rotate: [0, 90, 180, 0],
    transition: {
      duration: 25,
      ease: "linear",
      repeat: Infinity,
    },
  },
  active: {
    x: ["-20%", "20%", "-10%", "-20%"],
    y: ["-10%", "20%", "-20%", "-10%"],
    rotate: [0, 180, 360, 0],
    transition: {
      duration: 15,
      ease: "linear",
      repeat: Infinity,
    },
  },
};

// Spatial layout shifts for depth (Z-axis navigation)
export const depthTransition: Variants = {
  initial: {
    opacity: 0,
    scale: 0.8,
    y: 50,
    filter: "blur(10px)",
  },
  animate: {
    opacity: 1,
    scale: 1,
    y: 0,
    filter: "blur(0px)",
    transition: springConfig,
  },
  exit: {
    opacity: 0,
    scale: 1.1,
    y: -50,
    filter: "blur(10px)",
    transition: springConfig,
  },
};

// Node morphing for when a summary turns into a quiz or plan
export const nodeMorphing: Variants = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: { 
    opacity: 1, 
    scale: 1,
    transition: {
      staggerChildren: 0.1,
      ...springConfig
    }
  },
};

export const itemMorphing: Variants = {
  hidden: { opacity: 0, y: 20, filter: "blur(5px)" },
  visible: { 
    opacity: 1, 
    y: 0, 
    filter: "blur(0px)",
    transition: springConfig
  },
};
