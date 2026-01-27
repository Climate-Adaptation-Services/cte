import adapter from "@sveltejs/adapter-static";

import adapter from '@sveltejs/adapter-vercel';

const config = {
  kit: {
    adapter: adapter()
  }
};

export default config;

/** @type {import('@sveltejs/kit').Config} */
const config = {
  kit: {
    adapter: adapter({
      pages: "build",
      assets: "build",
      fallback: "index.html", // SPA fallback
      precompress: false,
      strict: false, // allow non-prerenderable routes
    }),
  },
};

export default config;
