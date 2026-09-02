import type {
  AuthenticatedUser,
  WorkspaceView,
} from '../../types'

interface HeaderProps {
  user: AuthenticatedUser
  view: WorkspaceView
  isReceptionist: boolean
}


function getWorkspaceEyebrow(
  view: WorkspaceView,
  isReceptionist: boolean,
): string {
  if (view === 'administrator') {
    return 'ADMINISTRATION'
  }

  if (view === 'nursing') {
    return 'NURSING'
  }

  if (view === 'doctor') {
    return 'DOCTOR'
  }

  if (view === 'laboratory') {
    return 'LABORATORY'
  }

  if (view === 'pharmacy') {
    return 'PHARMACY'
  }

  if (view === 'reception') {
    return 'RECEPTION'
  }

  return isReceptionist
    ? 'RECEPTION'
    : 'STAFF WORKSPACE'
}


function getWorkspaceTitle(
  view: WorkspaceView,
): string {
  switch (view) {
    case 'dashboard':
      return 'Good day'

    case 'reception':
      return 'Reception'

    case 'administrator':
      return 'Administration'

    case 'nursing':
      return 'Nursing'

    default:
      return 'LIGHTBURGH'
  }
}


export default function Header({
  user,
  view,
  isReceptionist,
}: HeaderProps) {
  return (
    <header className="workspace-header">

      <div>

        <p className="eyebrow">
          {getWorkspaceEyebrow(
            view,
            isReceptionist,
          )}
        </p>

        <h1>
          {getWorkspaceTitle(view)}
        </h1>

      </div>


      <div className="header-user">
        <span>
          {user.email}
        </span>
      </div>

    </header>
  )
}