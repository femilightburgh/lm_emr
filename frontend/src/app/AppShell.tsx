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
  isDoctor: boolean
  isLaboratoryScientist: boolean
  isPharmacist: boolean
  isDiagnosticsUser: boolean

  onDashboard: () => void
  onReception: () => void
  onAdministrator: () => void
  onNursing: () => void
  onDoctor: () => void
  onLaboratory: () => void
  onPharmacy: () => void
  onDiagnostics: () => void
  onSignOut: () => void

  children: ReactNode
}


export default function AppShell({
  user,
  view,

  isReceptionist,
  isAdministrator,
  isNurse,
  isDoctor,
  isLaboratoryScientist,
  isPharmacist,
  isDiagnosticsUser,

  onDashboard,
  onReception,
  onAdministrator,
  onNursing,
  onDoctor,
  onLaboratory,
  onPharmacy,
  onDiagnostics,
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
        isDoctor={isDoctor}
        isLaboratoryScientist={isLaboratoryScientist}
        isPharmacist={isPharmacist}
        isDiagnosticsUser={isDiagnosticsUser}

        onDashboard={onDashboard}
        onReception={onReception}
        onAdministrator={onAdministrator}
        onNursing={onNursing}
        onDoctor={onDoctor}
        onLaboratory={onLaboratory}
        onPharmacy={onPharmacy}
        onDiagnostics={onDiagnostics}
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