#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🚀 CC-Music Server Setup\n');

// Check if wrangler is installed
try {
  execSync('wrangler --version', { stdio: 'ignore' });
} catch (error) {
  console.log('Installing Wrangler CLI...');
  execSync('npm install -g wrangler', { stdio: 'inherit' });
}

// Install dependencies
console.log('📦 Installing dependencies...');
execSync('npm install', { stdio: 'inherit' });

// Login to Cloudflare
console.log('\n🔐 Logging into Cloudflare...');
try {
  execSync('wrangler whoami', { stdio: 'ignore' });
  console.log('Already logged in!');
} catch (error) {
  execSync('wrangler login', { stdio: 'inherit' });
}

// Create KV namespaces
console.log('\n📚 Creating KV namespaces...');

try {
  // Create SESSIONS namespace
  console.log('Creating SESSIONS namespace...');
  const sessionsResult = execSync('wrangler kv:namespace create SESSIONS', { encoding: 'utf-8' });
  const sessionsId = sessionsResult.match(/id = "([^"]+)"/)[1];

  // Create CHUNKS namespace
  console.log('Creating CHUNKS namespace...');
  const chunksResult = execSync('wrangler kv:namespace create CHUNKS', { encoding: 'utf-8' });
  const chunksId = chunksResult.match(/id = "([^"]+)"/)[1];

  // Update wrangler.toml
  console.log('\n📝 Updating wrangler.toml...');
  const wranglerPath = path.join(__dirname, '..', 'wrangler.toml');
  let wranglerContent = fs.readFileSync(wranglerPath, 'utf-8');

  // Add KV bindings
  const kvBindings = `
[[kv_namespaces]]
binding = "SESSIONS"
id = "${sessionsId}"

[[kv_namespaces]]
binding = "CHUNKS"
id = "${chunksId}"
`;

  wranglerContent = wranglerContent.replace('# [[kv_namespaces]]', kvBindings.trim());
  fs.writeFileSync(wranglerPath, wranglerContent);

  console.log('\n✅ Setup complete!');
  console.log('\n📋 Next steps:');
  console.log('1. Run "npm run dev" to start local development');
  console.log('2. Run "npm run deploy" to deploy to Cloudflare');
  console.log('\nYour worker will be available at: https://cc-music.<your-subdomain>.workers.dev');

} catch (error) {
  console.error('❌ Error during setup:', error.message);
  process.exit(1);
}