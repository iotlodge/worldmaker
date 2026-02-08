import type { NextConfig } from "next";
import { resolve } from "path";

// Resolve THIS_DIR (the frontend/ directory) robustly across all
// Next.js config loading mechanisms (jiti for .ts, ESM, CJS).
// __dirname is always available when Next.js transpiles the config via jiti.
// Falls back to process.cwd() which is correct when launched from frontend/.
const THIS_DIR = typeof __dirname !== "undefined"
  ? __dirname
  : process.cwd();

const nextConfig: NextConfig = {
  // The root worldmaker/ dir has its own package-lock.json (playwright),
  // which causes Next.js 16 to infer the wrong workspace root.
  // Explicitly anchor everything to THIS_DIR (frontend/).
  turbopack: {
    root: THIS_DIR,
  },

  // Fix webpack CSS module resolution for the nested project structure.
  // CSS @import "tailwindcss" goes through enhanced-resolve; we must
  // ensure it looks in frontend/node_modules, not worldmaker/node_modules.
  webpack: (config) => {
    const frontendNodeModules = resolve(THIS_DIR, "node_modules");

    config.resolve = config.resolve || {};
    config.resolve.modules = [
      frontendNodeModules,
      ...(config.resolve.modules || ["node_modules"]),
    ];

    // Also set alias so CSS imports resolve correctly even when
    // enhanced-resolve starts from the wrong description file.
    config.resolve.alias = {
      ...(config.resolve.alias || {}),
      tailwindcss: resolve(frontendNodeModules, "tailwindcss"),
    };

    return config;
  },
};

export default nextConfig;
