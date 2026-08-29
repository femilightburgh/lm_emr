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

  onDashboard: () => void
  onPatients: () => void
  onRegistration: () => void
  onAdministrator: () => void
  onNursing: () => void
  onDoctor: () => void
  onLaboratory: () => void
  onPharmacy: () => void
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

  onDashboard,
  onPatients,
  onRegistration,
  onAdministrator,
  onNursing,
  onDoctor,
  onLaboratory,
  onPharmacy,
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

        onDashboard={onDashboard}
        onPatients={onPatients}
        onRegistration={onRegistration}
        onAdministrator={onAdministrator}
        onNursing={onNursing}
        onDoctor={onDoctor}
        onLaboratory={onLaboratory}
        onPharmacy={onPharmacy}
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