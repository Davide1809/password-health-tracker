import { calculateStrength } from "./passwordStrength";

test("weak password returns weak level", () => {
  const result = calculateStrength("abc");
  expect(result.level).toBe("Weak");
});

test("strong password returns strong", () => {
  const result = calculateStrength("A1!strongPASS");
  expect(result.level).toBe("Strong");
});