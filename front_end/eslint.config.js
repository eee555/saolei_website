import eslint from '@eslint/js';
import eslintConfigPrettier from 'eslint-config-prettier';
import eslintPluginVue from 'eslint-plugin-vue';
import globals from 'globals';
import typescriptEslint from 'typescript-eslint';

export default typescriptEslint.config(
  { ignores: ['*.d.ts', '**/coverage', '**/dist', '**/GuideView.vue'] },
  {
    extends: [
      eslint.configs.recommended,
      ...typescriptEslint.configs.recommended,
      ...eslintPluginVue.configs['flat/recommended'],
    ],
    files: ['**/*.{ts,vue}'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: globals.browser,
      parserOptions: {
        parser: typescriptEslint.parser,
      },
    },
    rules: {
      'vue/valid-v-for': 'off',
      'vue/first-attribute-linebreak': 'off',
      '@typescript-eslint/no-explicit-any': 'off',
      '@typescript-eslint/ban-ts-comment': 'off',
      'vue/no-v-html': 'off',
      'vue/require-v-for-key': 'off',
      '@typescript-eslint/no-unsafe-function-type': 'off',
      'no-prototype-builtins': 'off',
      '@typescript-eslint/no-empty-object-type': 'off',
      'vue/multi-word-component-names': 'off',
      'vue/no-template-shadow': 'off',
      'no-irregular-whitespace': 'off',
      "@typescript-eslint/no-unused-vars": ["error", { "argsIgnorePattern": "^_"}],
    },
  },
  eslintConfigPrettier
);