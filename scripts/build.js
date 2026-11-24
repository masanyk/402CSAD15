#!/usr/bin/env node
/**
 * Кросплатформне складання проєкту (без сторонніх залежностей).
 *
 * Створює каталог build/hello/ з:
 *   - lib/        — копія вихідних файлів із src/
 *   - hello       — виконуваний файл для Linux/macOS (shell-лаунчер, chmod +x)
 *   - hello.cmd   — виконуваний файл для Windows
 *
 * Запуск: npm run build
 * Результат запуску: build/hello/hello (або build\hello\hello.cmd) → "Hello, World!"
 */
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const srcDir = path.join(root, 'src');
const outDir = path.join(root, 'build', 'hello');
const libDir = path.join(outDir, 'lib');

// Перезбираємо лише власний каталог build/hello — інших файлів не чіпаємо.
fs.rmSync(outDir, { recursive: true, force: true });
fs.mkdirSync(libDir, { recursive: true });

for (const file of fs.readdirSync(srcDir)) {
  if (file.endsWith('.js')) {
    fs.copyFileSync(path.join(srcDir, file), path.join(libDir, file));
  }
}

const unixLauncher = [
  '#!/bin/sh',
  'DIR="$(cd "$(dirname "$0")" && pwd)"',
  'exec node "$DIR/lib/index.js" "$@"',
  '',
].join('\n');
fs.writeFileSync(path.join(outDir, 'hello'), unixLauncher);
fs.chmodSync(path.join(outDir, 'hello'), 0o755);

const winLauncher = ['@echo off', 'node "%~dp0lib\\index.js" %*', ''].join('\r\n');
fs.writeFileSync(path.join(outDir, 'hello.cmd'), winLauncher);

console.log(`Build OK: ${path.relative(root, outDir)}`);
console.log('  hello      (Linux/macOS)');
console.log('  hello.cmd  (Windows)');
