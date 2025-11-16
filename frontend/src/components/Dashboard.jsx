import { useEffect, useState } from "react";
import { BACKEND_URL } from "../config";

export default function Dashboard() {
  const [data, setData] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const res = await fetch(`${BACKEND_URL}/api/dashboard`);
        const body = await res.json();
        setData(body);
      } catch (err) {
        console.error("Dashboard fetch error:", err);
      }
    }
    fetchData();
  }, []);

  return <h1>{data ? `Welcome, ${data.userEmail}` : "Loading..."}</h1>;
}