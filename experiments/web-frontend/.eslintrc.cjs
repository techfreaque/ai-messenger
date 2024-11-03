module.exports = {

  extends: [
    "eslint:recommended",
    "react-app",
    // "plugin:@typescript-eslint/recommended",
    // "plugin:@typescript-eslint/recommended-requiring-type-checking",
    "plugin:prettier/recommended"
  ],
  plugins: [
    "react",
    // "react-hooks",
    "simple-import-sort",

    "eslint-plugin-unused-imports",
    // "@typescript-eslint",
    "prettier",
    "import"
  ],
  "env": {
    "browser": true,
    "es2021": true,
    'node': false
  },
  parser: "@typescript-eslint/parser",
  parserOptions: {
    project: "tsconfig.json",
    sourceType: "module",
  },
  rules: {
    "react/react-in-jsx-scope": "error",


    "@typescript-eslint/no-empty-interface": "error",
    "@typescript-eslint/no-explicit-any": "error",
    "react/self-closing-comp": "error",
    "prefer-template": "error",

    "@typescript-eslint/no-unsafe-member-access": "error",
    "@typescript-eslint/no-unsafe-assignment": "error",
    // Import sorting and unused import rules
    "simple-import-sort/imports": "error",
    "simple-import-sort/exports": "error",
    "unused-imports/no-unused-imports": "error",
    // TypeScript-specific rules
    "@typescript-eslint/consistent-type-imports": "error", // Enforce consistent usage of type imports
    "@typescript-eslint/no-unsafe-call": "error",
    "@typescript-eslint/no-unused-vars": [
      "error",
      {
        argsIgnorePattern: "^_"
      }
    ], // Disallow unused variables, but allow unused variables that start with _
    "@typescript-eslint/explicit-function-return-type": "error", // Require explicit return types on functions
    "@typescript-eslint/no-explicit-any": "error", // Disallow usage of the 'any' type
    "@typescript-eslint/no-floating-promises": "error", // Require Promises to be handled appropriately
    "@typescript-eslint/no-misused-promises": "error", // Prevent using promises in places not intended
    // General JavaScript/TypeScript rules
    "prefer-template": "error", // Enforce using template literals instead of string concatenation
    "no-console": "warn", // Warn when console statements are used
    "no-debugger": "error", // Disallow the use of debugger
    curly: "error", // Require consistent use of curly braces for blocks
    eqeqeq: ["error", "always"], // Enforce strict equality checks (=== and !==)
    "no-else-return": "error", // Disallow return before else
    "no-empty-function": "error", // Disallow empty functions
    "no-implied-eval": "error", // Disallow implied eval() through setTimeout, setInterval, etc.
    "no-return-await": "error", // Disallow unnecessary return await
    "prettier/prettier": "error", // Enforce Prettier formatting
    quotes: [
      "error",
      "double",
      {
        avoidEscape: true
      }
    ] // Enforce double quotes, allow single quotes if escaping





  },
};
