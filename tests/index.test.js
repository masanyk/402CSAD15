const { greet } = require('../src/index');

describe('greet function', () => {
  test('returns "Hello, World!" for input "World"', () => {
    expect(greet('World')).toBe('Hello, World!');
  });

  test('returns correct greeting for any name', () => {
    expect(greet('Максим')).toBe('Hello, Максим!');
  });

  test('returns greeting with empty string', () => {
    expect(greet('')).toBe('Hello, !');
  });
});
