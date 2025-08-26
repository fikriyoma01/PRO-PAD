import { useState } from "react";
import Dashboard from "./pages/Dashboard";
import AdminParameters from "./pages/AdminParameters";
import Workspace from "./pages/Workspace";

export default function App(){
  const [tab, setTab] = useState<"dashboard"|"workspace"|"admin">("dashboard");
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="p-4 shadow bg-white flex gap-3">
        <h1 className="text-xl font-bold">PRO-PAD</h1>
        <nav className="flex gap-2">
          <button className={`px-3 py-1 rounded ${tab==='dashboard'?'bg-gray-900 text-white':'bg-gray-200'}`} onClick={()=>setTab('dashboard')}>Dashboard</button>
          <button className={`px-3 py-1 rounded ${tab==='workspace'?'bg-gray-900 text-white':'bg-gray-200'}`} onClick={()=>setTab('workspace')}>Workspace</button>
                  <button className={`px-3 py-1 rounded ${tab==='admin'?'bg-gray-900 text-white':'bg-gray-200'}`} onClick={()=>setTab('admin')}>Admin</button>
        </nav>
      </header>
      <main className="p-6">
        {tab==='dashboard'? <Dashboard/> : tab==='workspace'? <Workspace/> : <AdminParameters/>}
      </main>
    </div>
  )
}
