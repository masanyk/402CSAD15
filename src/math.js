/**
 * Допоміжний математичний модуль для демонстрації юніт-тестування.
 */

/**
 * Додає два числа.
 * @param {number} a
 * @param {number} b
 * @returns {number}
 */
function add(a, b) {
  return a + b;
}

/**
 * Віднімає друге число від першого.
 * @param {number} a
 * @param {number} b
 * @returns {number}
 */
function subtract(a, b) {
  return a - b;
}

module.exports = { add, subtract };
