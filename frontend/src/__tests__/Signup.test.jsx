import { render, screen, fireEvent } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import Signup from "../components/Signup";

test("shows validation errors for invalid email", () => {
  render(<BrowserRouter><Signup /></BrowserRouter>);
  fireEvent.change(screen.getByPlaceholderText(/you@example.com/i), { target: { value: "bad-email" } });
  fireEvent.change(screen.getByPlaceholderText(/Create a strong password/i), { target: { value: "Aa1!aaaa" } });
  fireEvent.click(screen.getByText(/Create account/i));
  expect(screen.getByText(/Please enter a valid email address/i)).toBeInTheDocument();
});