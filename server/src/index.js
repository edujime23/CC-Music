// CC-Music Worker with rich metadata + PCM8/DFPWM support
export default {
  async fetch(request, env, ctx) {
    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    };

    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }

    const url = new URL(request.url);
    const path = url.pathname;

    console.log(`Request: ${request.method} ${path}`);

    try {
      // Health/root
      if (path === "/" && request.method === "GET") {
        return new Response(
          JSON.stringify({
            name: "CC-Music Server",
            status: "running",
            version: "1.1.0",
          }),
          { headers: { "Content-Type": "application/json", ...corsHeaders } }
        );
      }

      // Create session
      if (path === "/session" && request.method === "POST") {
        const sessionId = crypto.randomUUID();
        await env.SESSIONS.put(
          sessionId,
          JSON.stringify({ created: Date.now(), status: "active" }),
          { expirationTtl: 3600 }
        );

        console.log("Session created:", sessionId);
        return new Response(JSON.stringify({ sessionId }), {
          headers: { "Content-Type": "application/json", ...corsHeaders },
        });
      }

      // Request track processing
      if (path === "/track" && request.method === "POST") {
        const body = await request.json();
        const { sessionId, videoId, format: reqFormat, sampleRate, duration } = body || {};

        const format = reqFormat === "dfpwm" ? "dfpwm" : "pcm8"; // default pcm8
        const sr = Number(sampleRate) || 48000; // default 48k
        const dur = Number(duration) || 10; // default 10s demo

        console.log("Track requested:", { sessionId, videoId, format, sampleRate: sr, duration: dur });

        ctx.waitUntil(processVideo({ sessionId, videoId, format, sampleRate: sr, duration: dur }, env));

        return new Response(
          JSON.stringify({ status: "processing", sessionId, videoId, format }),
          { headers: { "Content-Type": "application/json", ...corsHeaders } }
        );
      }

      // Get metadata
      if (path.startsWith("/metadata/") && request.method === "GET") {
        const videoId = path.split("/")[2];
        const metadata = await env.CHUNKS.get(`meta_${videoId}`);
        if (!metadata) return new Response("Not found", { status: 404, headers: corsHeaders });

        return new Response(metadata, {
          headers: { "Content-Type": "application/json", "Cache-Control": "public, max-age=60", ...corsHeaders },
        });
      }

      // Get a chunk
      if (path.startsWith("/chunk/") && request.method === "GET") {
        const [, , videoId, chunkId] = path.split("/");
        const chunk = await env.CHUNKS.get(`chunk_${videoId}_${chunkId}`, "arrayBuffer");
        if (!chunk) return new Response("Chunk not found", { status: 404, headers: corsHeaders });

        return new Response(chunk, {
          headers: {
            "Content-Type": "application/octet-stream",
            "Cache-Control": "public, max-age=86400",
            ...corsHeaders,
          },
        });
      }

      return new Response("Not Found", { status: 404, headers: corsHeaders });
    } catch (error) {
      console.error("Server error:", error);
      return new Response(JSON.stringify({ error: "Internal Server Error", message: error.message }), {
        status: 500,
        headers: { "Content-Type": "application/json", ...corsHeaders },
      });
    }
  },
};

// Helper: generate/process a track, store chunks + metadata
async function processVideo(opts, env) {
  const { sessionId, videoId, format, sampleRate, duration } = opts;
  try {
    const chunkSizeSamples = 16 * 1024; // 16k samples per chunk
    const channels = 1;

    // Generate tone (mono PCM8 in -128..127)
    const totalSamples = sampleRate * duration;
    const pcm8 = new Int8Array(totalSamples);
    for (let i = 0; i < totalSamples; i++) {
      // 440Hz sine at modest amplitude
      pcm8[i] = Math.floor(Math.sin((2 * Math.PI * 440 * i) / sampleRate) * 64);
    }

    let chunks = [];
    if (format === "dfpwm") {
      // Convert PCM8 -> Float32 [-1..1] -> DFPWM chunks
      const f32 = new Float32Array(pcm8.length);
      for (let i = 0; i < pcm8.length; i++) f32[i] = pcm8[i] / 127;
      const { convertToDFPWM } = await import("./lib/audio.js");
      chunks = await convertToDFPWM(f32, chunkSizeSamples);
    } else {
      // Raw PCM8 chunks
      for (let i = 0; i < pcm8.length; i += chunkSizeSamples) {
        const slice = pcm8.slice(i, Math.min(i + chunkSizeSamples, pcm8.length));
        chunks.push(slice); // Uint8Array view with its own buffer
      }
    }

    // Store chunks in KV as ArrayBuffer
    for (let i = 0; i < chunks.length; i++) {
      const ab = chunks[i].buffer; // ArrayBuffer for KV
      await env.CHUNKS.put(`chunk_${videoId}_${i}`, ab, { expirationTtl: 86400 });
    }

    // Tiny 16x8-ish NFT-like pattern (as hex color rows)
    const thumbnail =
      "00000000\n" +
      "01111110\n" +
      "01000010\n" +
      "01011010\n" +
      "01011010\n" +
      "01000010\n" +
      "01111110\n" +
      "00000000";

    const metadata = {
      version: 1,
      videoId,
      title: "Test Track " + videoId,
      artist: "CC-Music Test",
      duration,
      thumbnail,
      totalChunks: chunks.length,
      format,            // "pcm8" | "dfpwm"
      sampleRate,        // 48000 default
      channels,          // 1 (mono)
      chunkSize: chunkSizeSamples, // samples per chunk
      createdAt: Date.now(),
      ready: true,
    };

    await env.CHUNKS.put(`meta_${videoId}`, JSON.stringify(metadata), { expirationTtl: 86400 });
    console.log("Processed", videoId, "chunks:", chunks.length, "format:", format);
  } catch (e) {
    console.error("Processing error:", e);
  }
}