import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import ParticleBackground from './components/ParticleBackground'
import Layout from './components/Layout'
import AuthPage from './pages/Auth'
import ProcessPage from './pages/Process'
import HistoryPage from './pages/History'
import SettingsPage from './pages/Settings'
import AskPage from './pages/Ask'

function PrivateRoute({ children }) {
    const { user, loading } = useAuth()

    if (loading) {
        return (
            <div className="loading-screen">
                <div className="loader"></div>
            </div>
        )
    }

    return user ? children : <Navigate to="/login" />
}

export default function App() {
    const { user, loading } = useAuth()

    if (loading) {
        return (
            <div className="loading-screen">
                <ParticleBackground />
                <div className="loader"></div>
            </div>
        )
    }

    return (
        <>
            <ParticleBackground />
            <div style={{ position: 'relative', zIndex: 1, minHeight: '100vh' }}>
                <Routes>
                    <Route
                        path="/login"
                        element={user ? <Navigate to="/" /> : <AuthPage />}
                    />
                    <Route
                        path="/"
                        element={
                            <PrivateRoute>
                                <Layout>
                                    <ProcessPage />
                                </Layout>
                            </PrivateRoute>
                        }
                    />
                    <Route
                        path="/ask"
                        element={
                            <PrivateRoute>
                                <Layout>
                                    <AskPage />
                                </Layout>
                            </PrivateRoute>
                        }
                    />
                    <Route
                        path="/history"
                        element={
                            <PrivateRoute>
                                <Layout>
                                    <HistoryPage />
                                </Layout>
                            </PrivateRoute>
                        }
                    />
                    <Route
                        path="/settings"
                        element={
                            <PrivateRoute>
                                <Layout>
                                    <SettingsPage />
                                </Layout>
                            </PrivateRoute>
                        }
                    />
                </Routes>
            </div>

            <style>{`
        .loading-screen {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .loader {
          width: 40px;
          height: 40px;
          border: 3px solid var(--border);
          border-top-color: var(--accent);
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }
      `}</style>
        </>
    )
}
