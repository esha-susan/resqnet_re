// frontend/src/App.jsx
// Root component. Defines all page routes.
// As we add pages, we register them here.

import { Routes, Route } from 'react-router-dom'
import Home from './pages/Home.jsx'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
    </Routes>
  )
}

export default App