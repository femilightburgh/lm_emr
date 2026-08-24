import type {
  ReactNode,
} from 'react'

import type {
  AuthenticatedUser,
  WorkspaceView,
} from '../types'

import Sidebar from '../components/layout/Sidebar'
import Header from '../components/layout/Header'


interface AppShellProps {
  user: AuthenticatedUser
  view: WorkspaceView

  isReceptionist: boolean
  isAdministrator: boolean
  isNurse: boolean

  onDashboard: () => void
  onPatients: () => void
  onRegistration: () => void
  onAdministrator: () => void
  onNursing: () => void
  onSignOut: () => void

  children: ReactNode
}


export default function AppShell({
  user,
  view,

  isReceptionist,
  isAdministrator,
  isNurse,

  onDashboard,
  onPatients,
  onRegistration,
  onAdministrator,
  onNursing,
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
        isNurse={isNurse}

        onDashboard={onDashboard}
        onPatients={onPatients}
        onRegistration={onRegistration}
        onAdministrator={onAdministrator}
        onNursing={onNursing}
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