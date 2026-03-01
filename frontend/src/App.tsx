import { useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import Sidebar from './components/common/Sidebar';
import Dashboard from './pages/Dashboard';
import DatasetsPage from './pages/DatasetsPage';
import ModelsPage from './pages/ModelsPage';
import VisualizationsPage from './pages/VisualizationsPage';
import PublicationsPage from './pages/PublicationsPage';
import KnowledgeBasePage from './pages/KnowledgeBasePage';
import QuickActionsPage from './pages/QuickActionsPage';
import DataAlignmentPage from './pages/DataAlignmentPage';

function App() {
  const [darkMode, setDarkMode] = useState(false);

  return (
    <div className={darkMode ? 'dark' : ''}>
      <div className="flex h-screen bg-surface-50 dark:bg-surface-950">
        <Sidebar darkMode={darkMode} onToggleDarkMode={() => setDarkMode(!darkMode)} />
        <main className="flex-1 overflow-auto">
          <div className="p-6 max-w-7xl mx-auto">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/datasets" element={<DatasetsPage />} />
              <Route path="/datasets/align" element={<DataAlignmentPage />} />
              <Route path="/models" element={<ModelsPage />} />
              <Route path="/visualizations" element={<VisualizationsPage />} />
              <Route path="/publications" element={<PublicationsPage />} />
              <Route path="/knowledge-base" element={<KnowledgeBasePage />} />
              <Route path="/quick-actions" element={<QuickActionsPage />} />
            </Routes>
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
