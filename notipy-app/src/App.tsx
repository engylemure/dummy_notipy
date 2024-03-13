import { useMemo, useState } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";
import "./App.css";
import { z } from "zod";
import Notifications from "./Notifications";
import { createNotification } from "./api";

const PATH_REGEX = /[^\/][^\/]*/;

function App() {
  const url = new URL(document.URL);
  const userId = useMemo(() => {
    try {
      const match = url.pathname.match(PATH_REGEX)?.[0];
      return z.coerce.number().int().parse(match);
    } catch (err) {
      return 1;
    }
  }, [url.pathname]);

  const [count, setCount] = useState(0);

  return (
    <>
      <div>
        <a href="https://vitejs.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)} className="mr-4">
          count is {count}
        </button>
        <button onClick={() => createNotification(userId, "Hello !!!")}>
          Create notification
        </button>
        <p>
          Edit <code>src/App.tsx</code> and save to test HMR
        </p>
      </div>
      <div className=""></div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
      <Notifications userId={userId} />
    </>
  );
}

export default App;
