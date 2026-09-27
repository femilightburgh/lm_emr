import {
  lazy,
  Suspense,
  useEffect,
  useState,
} from 'react'
import type { FormEvent } from 'react'
import AppShell from './app/AppShell'

const AdministratorWorkspace = lazy(
  () => import('./components/administration/AdministratorWorkspace'),
)
const ReceptionWorkspace = lazy(
  () => import('./components/reception/ReceptionWorkspace'),
)
const NursingWorkspace = lazy(
  () => import('./components/nursing/NursingWorkspace'),
)
const DoctorWorkspace = lazy(
  () => import('./components/doctor/DoctorWorkspace'),
)
const LaboratoryWorkspace = lazy(
  () => import('./components/laboratory/LaboratoryWorkspace'),
)
const PharmacyWorkspace = lazy(
  () => import('./components/pharmacy/PharmacyWorkspace'),
)
const DiagnosticsWorkspace = lazy(
  () => import('./components/diagnostics/DiagnosticsWorkspace'),
)

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


  function openReception() {
    setView('reception')
  }


  function openDashboard() {
    setView('dashboard')
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

  useEffect(() => {
    function handleSessionRefresh(
      event: Event,
    ) {
      const refreshed = (
        event as CustomEvent<LoginResponse>
      ).detail

      if (refreshed) {
        setSession(refreshed)
      }
    }

    window.addEventListener(
      'lightburgh:session-refreshed',
      handleSessionRefresh,
    )

    return () => {
      window.removeEventListener(
        'lightburgh:session-refreshed',
        handleSessionRefresh,
      )
    }
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

const isDoctor =
  user.roles?.includes('Doctor') ?? false

const isLaboratoryScientist =
  user.roles?.includes('Laboratory Scientist') ?? false

const isPharmacist =
  user.roles?.includes('Pharmacist') ?? false

const isDiagnosticsUser =
  user.roles?.includes('Radiographer') === true ||
  user.roles?.includes('Laboratory Scientist') === true

const dashboardAction = isReceptionist
  ? {
      label: 'Open reception',
      onClick: openReception,
    }
  : isNurse
    ? {
        label: 'Open nursing',
        onClick: () => setView('nursing'),
      }
    : isDoctor
      ? {
          label: 'Open doctor workspace',
          onClick: () => setView('doctor'),
        }
      : isLaboratoryScientist
        ? {
            label: 'Open laboratory',
            onClick: () => setView('laboratory'),
          }
        : isPharmacist
          ? {
              label: 'Open pharmacy',
              onClick: () => setView('pharmacy'),
            }
          : isAdministrator
            ? {
                label: 'Open administration',
                onClick: () => setView('administrator'),
              }
            : isDiagnosticsUser
              ? {
                  label: 'Open diagnostics',
                  onClick: () => setView('diagnostics'),
                }
              : null

return (
  <AppShell
    user={user}
    view={view}
    isReceptionist={isReceptionist}
    isAdministrator={isAdministrator}
    isNurse={isNurse}
    isDoctor={isDoctor}
    isLaboratoryScientist={isLaboratoryScientist}
    isPharmacist={isPharmacist}
    isDiagnosticsUser={isDiagnosticsUser}
    onDashboard={openDashboard}
    onReception={openReception}
    onAdministrator={() =>
      setView('administrator')
    }
    onNursing={() =>
      setView('nursing')
    }
    onDoctor={() =>
      setView('doctor')
    }
    onLaboratory={() =>
      setView('laboratory')
    }
    onPharmacy={() =>
      setView('pharmacy')
    }
    onDiagnostics={() =>
      setView('diagnostics')
    }
    onSignOut={handleSignOut}
  >
    <Suspense
      fallback={
        <section className="workspace-content">
          <div className="welcome-panel">
            <p>Loading workspace...</p>
          </div>
        </section>
      }
    >
    {view === 'dashboard' && (
      <section className="workspace-content">

        <div className="welcome-panel">

          <div>
            <p className="eyebrow">
              TODAY'S WORKSPACE
            </p>

            <h2>
              {isReceptionist
                ? 'Welcome to reception.'
                : 'Welcome to LIGHTBURGH.'}
            </h2>

            <p>
              {isReceptionist
                ? 'Search for an existing patient or register a new patient to begin their journey through LIGHTBURGH.'
                : 'Choose your workspace to continue with today’s clinical work.'}
            </p>
          </div>

          {dashboardAction && (
            <button
              type="button"
              className="primary-button dashboard-action"
              onClick={dashboardAction.onClick}
            >
              {dashboardAction.label}
            </button>
          )}

        </div>

      </section>
    )}

    {view === 'reception' && (
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

    {view === 'doctor' && isDoctor && (
      <DoctorWorkspace
        accessToken={session.access_token}
      />
    )}

    {view === 'laboratory' &&
      isLaboratoryScientist && (
      <LaboratoryWorkspace
        accessToken={session.access_token}
      />
    )}

    {view === 'pharmacy' &&
      isPharmacist && (
      <PharmacyWorkspace
        accessToken={session.access_token}
      />
    )}


    {view === 'diagnostics' &&
      isDiagnosticsUser && (
      <DiagnosticsWorkspace
        accessToken={session.access_token}
      />
    )}
    </Suspense>
    </AppShell>
  )
}

export default App
