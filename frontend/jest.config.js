module.exports = {
  testEnvironment: "jsdom",
  moduleDirectories: ["node_modules", "src"],
  transformIgnorePatterns: [
    "node_modules/(?!react-router-dom)"
  ],
};
