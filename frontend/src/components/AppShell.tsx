import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../lib/auth'

export function AppShell() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  async function handleLogout() {
    await logout()
    navigate('/auth')
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Automotive tuning datalogs</p>
          <h1>Data Log Visual</h1>
        </div>
        <div className="topbar-actions">
          <nav className="nav-links">
            <NavLink to="/" end>
              Library
            </NavLink>
            <NavLink to="/upload">Upload</NavLink>
          </nav>
          <div className="user-pill">
            <span>{user?.display_name || user?.email}</span>
            <button type="button" className="ghost-button" onClick={handleLogout}>
              Logout
            </button>
          </div>
        </div>
      </header>
      <main className="app-content">
        <Outlet />
      </main>
    </div>
  )
}
