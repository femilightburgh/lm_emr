import type {
  AuthenticatedUser,
  WorkspaceView,
} from '../../types'


interface SidebarProps {
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
}


export default function Sidebar({
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
}: SidebarProps) {
  return (
    <aside className="sidebar">

      <div className="sidebar-brand">

        <div className="brand">
          LIGHTBURGH
        </div>

        <div className="sidebar-caption">
          Hospital Information System
        </div>

      </div>


      <nav className="sidebar-nav">

        {/* Dashboard */}

        <button
          type="button"
          className={
            view === 'dashboard'
              ? 'nav-item active'
              : 'nav-item'
          }
          onClick={onDashboard}
        >
          <span>Dashboard</span>
        </button>


        {/* Reception */}

        {isReceptionist && (
          <>
            <button
              type="button"
              className={
                view === 'patients'
                  ? 'nav-item active'
                  : 'nav-item'
              }
              onClick={onPatients}
            >
              <span>Patients</span>
            </button>


            <button
              type="button"
              className={
                view === 'register'
                  ? 'nav-item active'
                  : 'nav-item'
              }
              onClick={onRegistration}
            >
              <span>Register patient</span>
            </button>


            <button
              type="button"
              className="nav-item"
              disabled
            >
              <span>Returning patient</span>
              <small>Coming soon</small>
            </button>


            <button
              type="button"
              className="nav-item"
              disabled
            >
              <span>Queue</span>
              <small>Coming soon</small>
            </button>


            <button
              type="button"
              className="nav-item"
              disabled
            >
              <span>Payments</span>
              <small>Coming soon</small>
            </button>
          </>
        )}


        {/* Nursing */}

        {isNurse && (
          <button
            type="button"
            className={
              view === 'nursing'
                ? 'nav-item active'
                : 'nav-item'
            }
            onClick={onNursing}
          >
            <span>Nursing</span>
            <small>Clinical</small>
          </button>
        )}


        {/* Doctor */}

        {isDoctor && (
          <button
            type="button"
            className={
              view === 'doctor'
                ? 'nav-item active'
                : 'nav-item'
            }
            onClick={onDoctor}
          >
            <span>Doctor Workspace</span>
            <small>Clinical</small>
          </button>
        )}


        {/* Laboratory */}

        {isLaboratoryScientist && (
          <button
            type="button"
            className={
              view === 'laboratory'
                ? 'nav-item active'
                : 'nav-item'
            }
            onClick={onLaboratory}
          >
            <span>Laboratory</span>
            <small>Clinical</small>
          </button>
        )}


        {/* Pharmacy */}

        {isPharmacist && (
          <button
            type="button"
            className={
              view === 'pharmacy'
                ? 'nav-item active'
                : 'nav-item'
            }
            onClick={onPharmacy}
          >
            <span>Pharmacy</span>
            <small>Clinical</small>
          </button>
        )}


        {/* Administration */}

        {isAdministrator && (
          <button
            type="button"
            className={
              view === 'administrator'
                ? 'nav-item active'
                : 'nav-item'
            }
            onClick={onAdministrator}
          >
            <span>Administration</span>
            <small>Admin</small>
          </button>
        )}

      </nav>


      <div className="sidebar-footer">

        <div className="user-summary">

          <div className="user-avatar">
            {user.email
              .charAt(0)
              .toUpperCase()}
          </div>


          <div>

            <strong>
              {user.email}
            </strong>

            <span>
              {isAdministrator
                ? 'Administrator'
                : isNurse
                  ? 'Nurse'
                  : isReceptionist
                    ? 'Receptionist'
                    : isDoctor
                      ? 'Doctor'
                      : 'Staff'}
            </span>

          </div>

        </div>


        <button
          type="button"
          className="sign-out-button"
          onClick={onSignOut}
        >
          Sign out
        </button>

      </div>

    </aside>
  )
}