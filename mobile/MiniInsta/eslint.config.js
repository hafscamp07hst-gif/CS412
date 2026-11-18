// https://docs.expo.dev/guides/using-eslint/
const { defineConfig } = require('eslint/config');
const expoConfig = require('eslint-config-expo/flat');

module.exports = defineConfig([
  expoConfig,
  {
    ignores: ['dist/*'],
    // Keep the effect-based fetching pattern taught in videos 67-70.
    rules: { 'react-hooks/set-state-in-effect': 'off' },
  },
]);
