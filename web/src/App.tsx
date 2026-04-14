import { NavLink, Route, Routes } from "react-router-dom";
import { IngestPage } from "./pages/IngestPage";
import { JobPage } from "./pages/JobPage";

export default function App() {
  return (
    <div className="shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">KiniVideo</p>
          <h1>Replay-first AI clipping for tech livestreams</h1>
        </div>
        <nav className="nav">
          <NavLink to="/">Ingest</NavLink>
          <NavLink to="/jobs/demo">Review</NavLink>
        </nav>
      </header>

      <main>
        <Routes>
          <Route path="/" element={<IngestPage />} />
          <Route path="/jobs/:jobId" element={<JobPage />} />
        </Routes>
      </main>
    </div>
  );
}
