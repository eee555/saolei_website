import eslint from '@eslint/js';
import eslintPluginVue from 'eslint-plugin-vue';
import globals from 'globals';
import typescriptEslint from 'typescript-eslint';
import vueI18n from '@intlify/eslint-plugin-vue-i18n';
import stylistic from '@stylistic/eslint-plugin'

export default typescriptEslint.config(
  { ignores: ['*.d.ts', '**/coverage', '**/dist', '**/GuideView.vue'] },
  {
    plugins: {
      '@stylistic': stylistic,
    },
    extends: [
      eslint.configs.recommended,
      ...typescriptEslint.configs.recommended,
      ...eslintPluginVue.configs['flat/recommended'],
      ...vueI18n.configs.recommended,
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
      'no-control-regex': 'off', 
      'no-irregular-whitespace': 'off',
      'no-prototype-builtins': 'off',
      'vue/first-attribute-linebreak': 'error',
      'vue/html-indent': ['error', 4],
      'vue/max-attributes-per-line': 'off', // 属性长度差别很大
      'vue/multi-word-component-names': 'off',
      'vue/no-irregular-whitespace': ['error', { 'skipHTMLTextContents': true }],
      'vue/no-template-shadow': 'off',
      'vue/no-v-html': 'off',
      'vue/prefer-template': 'error',
      'vue/require-v-for-key': 'off',
      'vue/static-class-names-order': 'error',
      '@intlify/vue-i18n/no-duplicate-keys-in-locale': 'error',
      '@intlify/vue-i18n/no-missing-keys': 'off', // 目前不兼容ts
      '@intlify/vue-i18n/no-raw-text': 'off', // 开发中有些地方需要使用原始文本
      '@intlify/vue-i18n/no-v-html': 'off', // 有个别的翻译包含了html标签
      '@stylistic/array-bracket-newline': 'error',
      '@stylistic/array-bracket-spacing': 'error',
      '@stylistic/arrow-parens': 'error',
      '@stylistic/arrow-spacing': 'error',
      '@stylistic/block-spacing': 'error',
      '@stylistic/brace-style': ['error', '1tbs', { 'allowSingleLine': true }],
      '@stylistic/comma-dangle': ['error', 'always-multiline'],
      '@stylistic/comma-spacing': 'error',
      '@stylistic/comma-style': 'error',
      '@stylistic/computed-property-spacing': 'error',
      '@stylistic/curly-newline': ['error', { 'consistent': true }],
      '@stylistic/dot-location': 'error',
      '@typescript-eslint/ban-ts-comment': 'off',
      '@typescript-eslint/no-empty-object-type': 'off',
      '@typescript-eslint/no-explicit-any': 'off',
      '@typescript-eslint/no-unsafe-function-type': 'off',
      "@typescript-eslint/no-unused-vars": ["error", { "argsIgnorePattern": "^_"}],
    },
    settings: {
      'vue-i18n': {
        localeDir: 'src/i18n/locales/*.ts',
        messageSyntaxVersion: '^11.0.0',
      },
    }
  },
);