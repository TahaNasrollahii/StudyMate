"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useOSStore } from "../../core/store/useOSStore";
import { apiClient } from "../../core/api/client";
import { cn } from "../../lib/utils";

export default function CinematicAuth() {
  const { setOSMode, setIsAuthenticated } = useOSStore();
  const [isLogin, setIsLogin] = useState(true);
  const [isVerificationMode, setIsVerificationMode] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [verificationToken, setVerificationToken] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      if (isVerificationMode) {
        // Verify Email Flow
        await apiClient.post("/users/verify-email", { token: verificationToken });
        
        // After verifying, auto-login
        const formData = new URLSearchParams();
        formData.append("username", email);
        formData.append("password", password);
        const res = await apiClient.post("/auth/login/access-token", formData, {
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
        });

        localStorage.setItem("access_token", res.data.access_token);
        localStorage.setItem("refresh_token", res.data.refresh_token);
        setIsAuthenticated(true);
        setOSMode("synapse");
        return;
      }

      if (isLogin) {
        // Login Flow
        const formData = new URLSearchParams();
        formData.append("username", email);
        formData.append("password", password);
        const res = await apiClient.post("/auth/login/access-token", formData, {
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
        });

        localStorage.setItem("access_token", res.data.access_token);
        localStorage.setItem("refresh_token", res.data.refresh_token);
        setIsAuthenticated(true);
        setOSMode("synapse");
      } else {
        // Register Flow
        await apiClient.post("/users/register", {
          email,
          password,
        });
        
        setIsVerificationMode(true);
      }
    } catch (err: any) {
      console.error(err);
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        setError(detail.map((d: any) => d.msg).join(", "));
      } else if (typeof detail === "string") {
        setError(detail);
      } else {
        setError("Authentication failed. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95, y: 20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 1.05, filter: "blur(10px)" }}
      transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
      className="relative z-20 flex flex-col items-center justify-center w-full max-w-md p-10 backdrop-blur-2xl bg-black/40 border border-white/10 rounded-3xl shadow-2xl overflow-hidden"
    >
      <div className="absolute inset-0 z-0 pointer-events-none opacity-20">
        <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-white to-transparent" />
        <div className="absolute bottom-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-white to-transparent" />
      </div>

      <div className="relative z-10 w-full flex flex-col items-center text-center space-y-2 mb-8">
        <h1 className="text-3xl font-light tracking-widest text-white uppercase">
          {isVerificationMode ? "Verify Network" : (isLogin ? "Access Network" : "Establish Identity")}
        </h1>
        <p className="text-white/40 text-sm tracking-widest uppercase">
          {isVerificationMode ? "A secure token has been dispatched." : (isLogin ? "Authenticate to Synthesize" : "Create your cognitive identity")}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="w-full flex flex-col space-y-5 relative mb-8">
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="text-red-400 text-sm bg-red-400/10 py-2 px-4 rounded-lg border border-red-400/20 text-center"
            >
              {error}
            </motion.div>
          )}
        </AnimatePresence>

        {isVerificationMode ? (
          <>
            <div className="text-xs text-[var(--color-os-accent-primary)] text-center px-2">
              [DEV FLOW]: A verification token was just printed to your Docker terminal logs (`docker compose logs app`). Paste it below.
            </div>
            <input
              type="text"
              placeholder="Verification Token"
              value={verificationToken}
              onChange={(e) => setVerificationToken(e.target.value)}
              required
              className={cn(
                "w-full bg-white/5 border border-white/10 rounded-2xl py-4 px-6 outline-none transition-all duration-300",
                "focus:border-[var(--color-os-accent-primary)] focus:bg-white/10 text-white placeholder-white/30 font-mono text-sm"
              )}
            />
          </>
        ) : (
          <>
            <input
              type="email"
              placeholder="Email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className={cn(
                "w-full bg-white/5 border border-white/10 rounded-2xl py-4 px-6 outline-none transition-all duration-300",
                "focus:border-[var(--color-os-accent-primary)] focus:bg-white/10 text-white placeholder-white/30"
              )}
            />
            <input
              type="password"
              placeholder="Password (min 8 chars)"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className={cn(
                "w-full bg-white/5 border border-white/10 rounded-2xl py-4 px-6 outline-none transition-all duration-300",
                "focus:border-[var(--color-os-accent-secondary)] focus:bg-white/10 text-white placeholder-white/30"
              )}
            />
          </>
        )}

        <button
          type="submit"
          disabled={loading}
          className={cn(
            "w-full rounded-2xl py-4 mt-4 font-medium tracking-wide transition-all duration-300 relative overflow-hidden",
            "bg-gradient-to-r from-[var(--color-os-accent-primary)] to-[var(--color-os-accent-secondary)] text-black uppercase",
            "hover:shadow-[0_0_30px_rgba(0,240,255,0.4)] hover:scale-[1.02]",
            loading ? "opacity-70 cursor-not-allowed" : ""
          )}
        >
          {loading ? "Processing..." : (isVerificationMode ? "Verify & Synthesize" : (isLogin ? "Access Network" : "Initialize"))}
        </button>
      </form>

      {!isVerificationMode && (
        <button
          type="button"
          onClick={() => {
            setIsLogin(!isLogin);
            setError("");
          }}
          className={cn(
            "px-6 py-2.5 rounded-full text-xs tracking-widest uppercase transition-all duration-300",
            "border border-white/10 bg-white/5 hover:bg-white/10 hover:border-white/20 text-white/70 hover:text-white hover:shadow-[0_0_15px_rgba(255,255,255,0.1)]"
          )}
        >
          {isLogin ? "No identity? Initialize one" : "Already linked? Access network"}
        </button>
      )}
    </motion.div>
  );
}
