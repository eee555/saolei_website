import eslint from '@eslint/js';
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
      'vue/first-attribute-linebreak': 'error',
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
      'vue/no-irregular-whitespace': ['error', { 'skipHTMLTextContents': true }],
      "@typescript-eslint/no-unused-vars": ["error", { "argsIgnorePattern": "^_"}],
      'no-control-regex': 'off',
      'vue/html-indent': ['error', 4],
      'vue/max-attributes-per-line': 'off',
      'vue/static-class-names-order': 'error',
      'vue/prefer-template': 'error',
    },
  },
);