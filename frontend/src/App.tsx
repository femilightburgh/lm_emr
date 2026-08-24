import {
  useEffect,
  useState,
} from 'react'
import type { FormEvent } from 'react'
import AdministratorWorkspace from './components/administration/AdministratorWorkspace'
import ReceptionWorkspace from './components/reception/ReceptionWorkspace'
import AppShell from './app/AppShell'

import {
  getCurrentUser,
  login,
  refreshAccessToken,
} from './api'

import {
  clearSession,
  getAccessToken,
  getRefreshToken,
  saveSession,
} from './auth'

import type {
  AuthenticatedUser,
  LoginResponse,
  WorkspaceView,
} from './types'

import './App.css'
import ActivateAccount from './components/auth/ActivateAccount'
import NursingWorkspace from './components/nursing/NursingWorkspace'

function App() {
  // ==========================================================================
  // Authentication
  // ==========================================================================

  const [hospitalCode, setHospitalCode] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const [session, setSession] =
    useState<LoginResponse | null>(null)

  const [user, setUser] =
    useState<AuthenticatedUser | null>(null)

  const [initializing, setInitializing] =
    useState(true)

  const [loading, setLoading] =
    useState(false)

  const [error, setError] =
    useState<string | null>(null)


  // ==========================================================================
  // Workspace
  // ==========================================================================

  const [view, setView] =
    useState<WorkspaceView>('dashboard')


  function openPatients() {
    setView('patients')
  }


  function openDashboard() {
    setView('dashboard')
  }


  function openRegistration() {
    setView('register')
  }



  // ==========================================================================
  // Session Restoration
  // ==========================================================================

  useEffect(() => {
    async function restoreSession() {
      const accessToken = getAccessToken()
      const refreshToken = getRefreshToken()

      if (!accessToken || !refreshToken) {
        setInitializing(false)
        return
      }

      try {
        const currentUser =
          await getCurrentUser(accessToken)

        setSession({
          access_token: accessToken,
          refresh_token: refreshToken,
          token_type: 'bearer',
        })

        setUser(currentUser)
      } catch {
        try {
          const refreshed =
            await refreshAccessToken(
              refreshToken,
            )

          const currentUser =
            await getCurrentUser(
              refreshed.access_token,
            )

          saveSession(
            refreshed,
            currentUser,
          )

          setSession(refreshed)
          setUser(currentUser)
        } catch {
          clearSession()
          setSession(null)
          setUser(null)
        }
      } finally {
        setInitializing(false)
      }
    }

    restoreSession()
  }, [])


  // ==========================================================================
  // Login
  // ==========================================================================

  async function handleLogin(
    event: FormEvent,
  ) {
    event.preventDefault()

    setLoading(true)
    setError(null)

    try {
      const response =
        await login({
          hospital_code:
            hospitalCode.trim(),
          email:
            email.trim(),
          password,
        })

      const currentUser =
        await getCurrentUser(
          response.access_token,
        )

      saveSession(
        response,
        currentUser,
      )

      setSession(response)
      setUser(currentUser)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to sign in.',
      )
    } finally {
      setLoading(false)
    }
  }


  // ==========================================================================
  // Sign Out
  // ==========================================================================

  function handleSignOut() {
    clearSession()

    setSession(null)
    setUser(null)

    setHospitalCode('')
    setEmail('')
    setPassword('')

    setView('dashboard')
  }

  // ==========================================================================
  // Initialization Screen
  // ==========================================================================

  if (initializing) {
    return (
      <main className="login-shell">
        <section className="login-card loading-card">
          <div className="brand">
            LIGHTBURGH
          </div>

          <h1>Loading...</h1>

          <p className="login-subtitle">
            Restoring your session.
          </p>
        </section>
      </main>
    )
  }


  if (
    window.location.pathname === '/activate'
  ) {
    return (
      <ActivateAccount
        onActivated={() => {
          window.history.pushState(
            {},
            '',
            '/',
          )

          window.location.reload()
        }}
      />
    )
  }


  // ==========================================================================
  // Login Screen
  // ==========================================================================

  if (!session || !user) {
    return (
      <main className="login-shell">
        <section className="login-card">

          <div className="brand">
            LIGHTBURGH
          </div>

          <div className="workspace-name">
            Hospital Information System
          </div>

          <div className="login-heading">
            <p className="eyebrow">
              STAFF ACCESS
            </p>

            <h1>
              Sign in
            </h1>

            <p className="login-subtitle">
              Sign in to access your hospital workspace.
            </p>
          </div>

          {error && (
            <div className="login-error">
              {error}
            </div>
          )}

          <form
            className="login-form"
            onSubmit={handleLogin}
          >
            <label>
              Hospital code

              <input
                type="text"
                value={hospitalCode}
                onChange={event =>
                  setHospitalCode(
                    event.target.value,
                  )
                }
                placeholder="e.g. WTH001"
                autoComplete="organization"
                required
              />
            </label>

            <label>
              Email

              <input
                type="email"
                value={email}
                onChange={event =>
                  setEmail(
                    event.target.value,
                  )
                }
                placeholder="you@hospital.com"
                autoComplete="email"
                required
              />
            </label>

            <label>
              Password

              <input
                type="password"
                value={password}
                onChange={event =>
                  setPassword(
                    event.target.value,
                  )
                }
                placeholder="Enter your password"
                autoComplete="current-password"
                required
              />
            </label>

            <button
              type="submit"
              className="primary-button"
              disabled={loading}
            >
              {loading
                ? 'Signing in...'
                : 'Sign in'}
            </button>
          </form>

        </section>
      </main>
    )
  }


// ==========================================================================
// Authenticated Workspace
// ==========================================================================

const isReceptionist =
  user.roles?.includes('Receptionist') ?? false

const isAdministrator =
  user.roles?.includes('Administrator') ?? false

const isNurse =
  user.roles?.includes('Nurse') ?? false

return (
  <AppShell
    user={user}
    view={view}
    isReceptionist={isReceptionist}
    isAdministrator={isAdministrator}
    isNurse={isNurse}
    onDashboard={openDashboard}
    onPatients={openPatients}
    onRegistration={openRegistration}
    onAdministrator={() =>
      setView('administrator')
    }
    onNursing={() =>
      setView('nursing')
    }
    onSignOut={handleSignOut}
  >
    {view === 'dashboard' && (
      <section className="workspace-content">

        <div className="welcome-panel">

          <div>
            <p className="eyebrow">
              TODAY'S WORKSPACE
            </p>

            <h2>
              Welcome to reception.
            </h2>

            <p>
              Search for an existing patient or
              register a new patient to begin
              their journey through LIGHTBURGH.
            </p>
          </div>

          <button
            type="button"
            className="primary-button dashboard-action"
            onClick={openPatients}
          >
            Find patient
          </button>

        </div>

      </section>
    )}

    {(view === 'patients' ||
      view === 'register') && (
      <ReceptionWorkspace
        accessToken={session.access_token}
        onDashboard={openDashboard}
      />
    )}

    {view === 'administrator' &&
      isAdministrator && (
      <AdministratorWorkspace
        accessToken={session.access_token}
        currentUserEmail={user.email}
        hospitalId={user.hospital_id}
      />
    )}

    {view === 'nursing' && (
      <NursingWorkspace
        accessToken={session.access_token}
        staffId={user.id}
      />
    )}
    </AppShell>
  )
}

export default App