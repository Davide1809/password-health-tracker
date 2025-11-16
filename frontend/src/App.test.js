import React from "react";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import Welcome from "./components/Welcome";
import Signup from "./components/Signup";
import Login from "./components/Login";
import Dashboard from "./components/Dashboard";
import PasswordAnalyzer from "./components/PasswordAnalyzer";

test("renders welcome page at /", () => {
  render(
    <MemoryRouter initialEntries={["/"]}>
      <Routes>
        <Route path="/" element={<Welcome />} />
      </Routes>
    </MemoryRouter>
  );

  const welcomeText = screen.getByText(/Welcome/i);
  expect(welcomeText).toBeInTheDocument();
});

test("renders signup page at /signup", () => {
  render(
    <MemoryRouter initialEntries={["/signup"]}>
      <Routes>
        <Route path="/signup" element={<Signup />} />
      </Routes>
    </MemoryRouter>
  );

  expect(screen.getByRole("button", { name: /Create Account/i })).toBeInTheDocument();
});

test("renders login page at /login", () => {
  render(
    <MemoryRouter initialEntries={["/login"]}>
      <Routes>
        <Route path="/login" element={<Login />} />
      </Routes>
    </MemoryRouter>
  );

  expect(screen.getByRole("button", { name: /Log in/i })).toBeInTheDocument();
});

test("renders dashboard page at /dashboard", () => {
  render(
    <MemoryRouter initialEntries={["/dashboard"]}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </MemoryRouter>
  );

  // Replace with a text that exists in your Dashboard
  expect(screen.getByText(/Dashboard/i)).toBeInTheDocument();
});

test("renders password analyzer page at /analyze", () => {
  render(
    <MemoryRouter initialEntries={["/analyze"]}>
      <Routes>
        <Route path="/analyze" element={<PasswordAnalyzer />} />
      </Routes>
    </MemoryRouter>
  );

  // Replace with some text in your PasswordAnalyzer component
  expect(screen.getByText(/Password Strength Analyzer/i)).toBeInTheDocument();
});
