import eslint from '@eslint/js';
import eslintPluginVue from 'eslint-plugin-vue';
import globals from 'globals';
import typescriptEslint from 'typescript-eslint';
import vueI18n from '@intlify/eslint-plugin-vue-i18n';

export default typescriptEslint.config(
  { ignores: ['*.d.ts', '**/coverage', '**/dist', '**/GuideView.vue'] },
  {
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
      'no-irregular-whitespace': 'off',
      'no-prototype-builtins': 'off',
      'vue/first-attribute-linebreak': 'error',
      'vue/multi-word-component-names': 'off',
      'vue/no-irregular-whitespace': ['error', { 'skipHTMLTextContents': true }],
      'vue/no-template-shadow': 'off',
      'vue/no-v-html': 'off',
      'vue/require-v-for-key': 'off',
      '@typescript-eslint/ban-ts-comment': 'off',
      '@typescript-eslint/no-empty-object-type': 'off',
      '@typescript-eslint/no-explicit-any': 'off',
      '@typescript-eslint/no-unsafe-function-type': 'off',
      "@typescript-eslint/no-unused-vars": ["error", { "argsIgnorePattern": "^_"}],
      'no-control-regex': 'off',
      'vue/html-indent': ['error', 4],
      'vue/max-attributes-per-line': 'off',
      'vue/static-class-names-order': 'error',
      'vue/prefer-template': 'error',
      '@intlify/vue-i18n/no-missing-keys': 'off', // 目前不兼容ts
      '@intlify/vue-i18n/no-raw-text': 'off',
      '@intlify/vue-i18n/no-v-html': 'off', // 有个别的翻译包含了html标签
    },
    settings: {
      'vue-i18n': {
        localeDir: 'src/i18n/locales/*.ts',
        messageSyntaxVersion: '^11.0.0',
      },
    }
  },
);