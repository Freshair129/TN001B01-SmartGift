import path from 'path';
import { fileURLToPath } from 'url';
import { createRequire } from 'module';

const require = createRequire(import.meta.url);

try {
  const bindingPath = process.env.GENESIS_BINDING_PATH || '@freshair129/gks-genesis-block-native';
  const binding = require(bindingPath);
  console.log('Successfully loaded GenesisBlock binding:', Object.keys(binding));
  
  const { GenesisDatabase } = binding;
  const db = GenesisDatabase.open({
    path: './test-db',
    vectorDim: 4
  });
  console.log('Successfully opened test GenesisDatabase instance!');
} catch (err) {
  console.error('Error loading GenesisBlockDB:', err);
}
