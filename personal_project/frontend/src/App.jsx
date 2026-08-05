import './App.css'
import NotebookWorkspace from './components/NotebookWorkspace'

function App() {
  return (
    <div className="app-shell">
      <header className="app-header">
        <h1>Docent AI</h1>
      </header>
      <main className="app-main">
        <NotebookWorkspace />
      </main>
    </div>
  )
}

export default App
