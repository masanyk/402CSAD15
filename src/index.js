/**
 * Модуль вітання.
 * @param {string} name - Ім'я для вітання
 * @returns {string} Рядок вітання
 */
function greet(name) {
  return `Hello, ${name}!`;
}

// Якщо файл запускається напряму (не як модуль) — виводимо Hello, World!
if (require.main === module) {
  console.log(greet("World"));
}

module.exports = { greet };
