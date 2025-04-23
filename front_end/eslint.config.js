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
      'vue/singleline-html-element-content-newline': 'error',
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
      '@stylistic/eol-last': 'error',
      '@stylistic/function-call-spacing': 'error',
      '@stylistic/generator-star-spacing': 'error',
      '@stylistic/implicit-arrow-linebreak': 'error',
      '@stylistic/indent': ['error', 4],
      '@stylistic/indent-binary-ops': ['error', 4],
      '@stylistic/key-spacing': 'error',
      '@stylistic/keyword-spacing': 'error',
      '@stylistic/member-delimiter-style': 'error',
      '@stylistic/new-parens': 'error',
      '@stylistic/newline-per-chained-call': 'off', // 不兼容代码风格
      '@stylistic/no-extra-parens': 'off', // 有些一元运算符需要括号保持可读性
      '@stylistic/no-extra-semi': 'error',
      '@stylistic/no-floating-decimal': 'error',
      '@stylistic/no-mixed-operators': 'off', // 加法和乘法还是不需要括号的
      '@stylistic/no-mixed-spaces-and-tabs': 'error',
      '@stylistic/no-multi-spaces': ['error', { 'ignoreEOLComments': true }],
      '@stylistic/no-trailing-spaces': 'error',
      '@stylistic/no-whitespace-before-property': 'error',
      '@stylistic/nonblock-statement-body-position': 'error',
      '@stylistic/object-curly-newline': ['error', { 'consistent': true }],
      '@stylistic/object-curly-spacing': ['error', 'always'],
      '@stylistic/padded-blocks': ['error', 'never'],
      '@stylistic/quotes': ['error', 'single'],
      '@stylistic/rest-spread-spacing': 'error',
      '@stylistic/semi': 'error',
      '@stylistic/semi-spacing': 'error',
      '@stylistic/semi-style': 'error',
      '@stylistic/space-before-blocks': 'error',
      '@stylistic/space-before-function-paren': ['error', { 'named': 'never' }],
      '@stylistic/space-in-parens': 'error',
      '@stylistic/space-infix-ops': 'error',
      '@stylistic/space-unary-ops': 'error',
      '@stylistic/spaced-comment': 'error',
      '@stylistic/switch-colon-spacing': 'error',
      '@stylistic/template-curly-spacing': 'error',
      '@stylistic/template-tag-spacing': 'error',
      '@stylistic/type-annotation-spacing': 'error',
      '@stylistic/type-generic-spacing': 'error',
      '@stylistic/type-named-tuple-spacing': 'error',
      '@stylistic/wrap-regex': 'error',
      '@stylistic/yield-star-spacing': 'error',
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