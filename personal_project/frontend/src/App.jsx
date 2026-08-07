import './App.css'
import ApiKeyGate from './components/ApiKeyGate'
import NotebookWorkspace from './components/NotebookWorkspace'

function App() {
  return (
    <div className="app-shell">
      <header className="app-header">
        <h1>Docent AI</h1>
      </header>
      <main className="app-main">
        <ApiKeyGate>
          <NotebookWorkspace />
        </ApiKeyGate>
      </main>
    </div>
  )
}

export default App
