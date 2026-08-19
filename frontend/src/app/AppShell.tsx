import type {
  ReactNode,
} from 'react'

import type {
  AuthenticatedUser,
} from '../types'

import Sidebar from '../components/layout/Sidebar'
import Header from '../components/layout/Header'


type WorkspaceView =
  | 'dashboard'
  | 'patients'
  | 'register'
  | 'administrator'


interface AppShellProps {
  user: AuthenticatedUser
  view: WorkspaceView
  isReceptionist: boolean
  isAdministrator: boolean
  onDashboard: () => void
  onPatients: () => void
  onRegistration: () => void
  onAdministrator: () => void
  onSignOut: () => void
  children: ReactNode
}


export default function AppShell({
  user,
  view,
  isReceptionist,
  isAdministrator,
  onDashboard,
  onPatients,
  onRegistration,
  onAdministrator,
  onSignOut,
  children,
}: AppShellProps) {
  return (
    <div className="app-shell">

      <Sidebar
        user={user}
        view={view}
        isReceptionist={isReceptionist}
        isAdministrator={isAdministrator}
        onDashboard={onDashboard}
        onPatients={onPatients}
        onRegistration={onRegistration}
        onAdministrator={onAdministrator}
        onSignOut={onSignOut}
      />

      <main className="workspace">

        <Header
          user={user}
          view={view}
          isReceptionist={isReceptionist}
        />

        {children}

      </main>

    </div>
  )
}